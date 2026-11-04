"""Matched pilot: fixed shrinkage LDA, whole-run holdouts, Cz/FCz only."""

# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv
import json
import platform
import warnings

import numpy as np
import scipy
from scipy.io import loadmat
import sklearn
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

HERE = ROOT / "output/DEC_decoding/DEC_01_pilot_decoders"
CONDITIONS = {1: "BP no-FORCe", 2: "BP FORCe", 3: "Split no-FORCe", 4: "Split FORCe"}
REPRESENTATIONS = {"100ms": 50, "50ms": 25, "samples": 1}
SUBJECTS = ["mle01", "spe30"]
SESSIONS = ["pre", "post", "retest"]


def write_csv(name, rows):
    assert rows, name
    with (HERE / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def metrics(y, predicted, score):
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    return dict(
        n=len(y),
        n_ND=int(np.sum(y == 0)),
        n_D=int(np.sum(y == 1)),
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
        balanced_accuracy=float((sensitivity + specificity) / 2),
        roc_auc=float(roc_auc_score(y, score)),
        sensitivity_D=float(sensitivity),
        specificity_ND=float(specificity),
    )


def make_lda():
    """Fixed decoder shared by the central-only and channel-set comparisons."""
    return make_pipeline(
        StandardScaler(),
        LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto", priors=[0.5, 0.5]),
    )


def main():
    with (HERE / "trial_metadata.csv").open(newline="", encoding="utf-8-sig") as f:
        metadata = list(csv.DictReader(f))
    mat = loadmat(HERE / "central_features.mat")
    raw = mat["rawFeatures"]
    n = len(metadata)
    assert raw.shape == (n, 700, 4) and np.isfinite(raw).all()
    assert float(mat["fs"].item()) == 500
    assert np.allclose(mat["sampleTimes"].ravel(), np.arange(100, 450) / 500)
    assert set(int(m["label"]) for m in metadata) == {1, 2}
    keys = [(m["subject"], m["session"], m["run"], int(m["trial"])) for m in metadata]
    assert len(set(keys)) == n
    y_all = np.array([int(m["label"]) - 1 for m in metadata])
    assert n == 2562
    features = {}
    for cid in CONDITIONS:
        z = raw[:, :, cid - 1].reshape(n, 2, 350)
        for rep, width in REPRESENTATIONS.items():
            features[cid, rep] = (
                z.reshape(n, 2, 350 // width, width).mean(axis=-1).reshape(n, -1)
            )
    predictions, folds, summaries = [], [], []
    fold_scores = {}
    heldout_ids = {}
    # One thread avoids unnecessary BLAS overhead for these small, repeated fits.
    with threadpool_limits(limits=1), warnings.catch_warnings():
        warnings.simplefilter("error")
        for subject in SUBJECTS:
            for session in SESSIONS:
                selected = np.array(
                    [
                        i
                        for i, m in enumerate(metadata)
                        if m["subject"] == subject and m["session"] == session
                    ]
                )
                y = y_all[selected]
                groups = np.array([metadata[i]["run"] for i in selected])
                splits = list(LeaveOneGroupOut().split(selected, y, groups))
                assert len(splits) == (
                    4 if (subject, session) == ("spe30", "retest") else 5
                )
                for cid, condition in CONDITIONS.items():
                    for rep in REPRESENTATIONS:
                        X = features[cid, rep][selected]
                        oof_pred = np.full(len(selected), -1)
                        oof_score = np.full(len(selected), np.nan)
                        seen = np.zeros(len(selected), dtype=int)
                        config_folds = []
                        for train, test in splits:
                            assert not set(groups[train]) & set(groups[test])
                            assert len(set(groups[test])) == 1
                            assert set(y[train]) == set(y[test]) == {0, 1}
                            model = make_lda()
                            model.fit(X[train], y[train])
                            assert np.allclose(model[0].mean_, X[train].mean(axis=0))
                            pred = model.predict(X[test])
                            score = model.decision_function(X[test])
                            assert np.isfinite(score).all()
                            oof_pred[test], oof_score[test] = pred, score
                            seen[test] += 1
                            run = str(groups[test][0])
                            base = dict(
                                subject=subject,
                                session=session,
                                condition_id=cid,
                                condition=condition,
                                representation=rep,
                                n_features=X.shape[1],
                                heldout_run=run,
                                heldout_run_number=metadata[selected[test[0]]][
                                    "runNumber"
                                ],
                                n_train=len(train),
                                train_ND=int(np.sum(y[train] == 0)),
                                train_D=int(np.sum(y[train] == 1)),
                            )
                            result = dict(**base, **metrics(y[test], pred, score))
                            # Training-majority dummy: balanced accuracy and AUC are both 0.5.
                            result["majority_class"] = int(
                                np.bincount(y[train]).argmax()
                            )
                            result["dummy_balanced_accuracy"] = 0.5
                            result["dummy_roc_auc"] = 0.5
                            folds.append(result)
                            config_folds.append(result)
                            fold_scores[subject, session, cid, rep, run] = result
                            heldout_ids[cid, rep, run] = tuple(selected[test])
                            for local, predicted, decision in zip(test, pred, score):
                                row = metadata[selected[local]]
                                predictions.append(
                                    dict(
                                        subject=subject,
                                        session=session,
                                        run=row["run"],
                                        run_number=int(row["runNumber"]),
                                        trial=int(row["trial"]),
                                        original_label=int(row["label"]),
                                        true_D=int(y[local]),
                                        condition_id=cid,
                                        condition=condition,
                                        representation=rep,
                                        predicted_D=int(predicted),
                                        decision_score=float(decision),
                                    )
                                )
                        assert np.all(seen == 1) and np.isfinite(oof_score).all()
                        result = metrics(y, oof_pred, oof_score)
                        # Each fold fits a different score scale; primary AUC averages within-run AUCs.
                        result["pooled_oof_roc_auc"] = result.pop("roc_auc")
                        result["mean_run_roc_auc"] = float(
                            np.mean([r["roc_auc"] for r in config_folds])
                        )
                        result["mean_run_balanced_accuracy"] = float(
                            np.mean([r["balanced_accuracy"] for r in config_folds])
                        )
                        result["min_run_balanced_accuracy"] = float(
                            min(r["balanced_accuracy"] for r in config_folds)
                        )
                        result["max_run_balanced_accuracy"] = float(
                            max(r["balanced_accuracy"] for r in config_folds)
                        )
                        summaries.append(
                            dict(
                                subject=subject,
                                session=session,
                                condition_id=cid,
                                condition=condition,
                                representation=rep,
                                n_features=X.shape[1],
                                n_runs=len(splits),
                                **result,
                            )
                        )
                        print(
                            f"{subject}/{session}: {condition}, {rep} ({X.shape[1]} features): "
                            f'BA={result["balanced_accuracy"]:.3f}, mean-run AUC={result["mean_run_roc_auc"]:.3f}',
                            flush=True,
                        )
    assert len(folds) == 348 and len(summaries) == 72 and len(predictions) == n * 12
    for run in sorted({m["run"] for m in metadata}):
        reference = heldout_ids[1, "100ms", run]
        for cid in CONDITIONS:
            for rep in REPRESENTATIONS:
                assert heldout_ids[cid, rep, run] == reference
    assert len(
        {
            (r["run"], r["trial"], r["condition_id"], r["representation"])
            for r in predictions
        }
    ) == len(predictions)
    contrasts = []
    # Same-fold paired differences; descriptive, not independent significance tests.
    for subject in SUBJECTS:
        for session in SESSIONS:
            runs = sorted(
                {
                    m["run"]
                    for m in metadata
                    if (m["subject"], m["session"]) == (subject, session)
                }
            )
            comparisons = []
            for rep in REPRESENTATIONS:
                for a, b in [(2, 1), (4, 3), (3, 1), (4, 2)]:
                    comparisons.append((f"condition {a} minus {b}", a, rep, b, rep))
            for cid in CONDITIONS:
                for rep in ["50ms", "samples"]:
                    comparisons.append((f"{rep} minus 100ms", cid, rep, cid, "100ms"))
            for name, a, ra, b, rb in comparisons:
                for run in runs:
                    first, second = (
                        fold_scores[subject, session, a, ra, run],
                        fold_scores[subject, session, b, rb, run],
                    )
                    contrasts.append(
                        dict(
                            subject=subject,
                            session=session,
                            comparison=name,
                            condition_a=a,
                            representation_a=ra,
                            condition_b=b,
                            representation_b=rb,
                            heldout_run=run,
                            delta_balanced_accuracy=first["balanced_accuracy"]
                            - second["balanced_accuracy"],
                            delta_roc_auc=first["roc_auc"] - second["roc_auc"],
                            delta_sensitivity_D=first["sensitivity_D"]
                            - second["sensitivity_D"],
                            delta_specificity_ND=first["specificity_ND"]
                            - second["specificity_ND"],
                        )
                    )
    write_csv("fold_metrics.csv", folds)
    write_csv("session_metrics.csv", summaries)
    write_csv("heldout_predictions.csv", predictions)
    write_csv("paired_fold_differences.csv", contrasts)
    settings = dict(
        python=sys.version,
        platform=platform.platform(),
        numpy=np.__version__,
        scipy=scipy.__version__,
        sklearn=sklearn.__version__,
        channels=["Cz", "FCz"],
        interval_seconds=[0.2, 0.9],
        right_endpoint_excluded=True,
        fs=500,
        original_label_mapping={
            "1": "non-displaced / binary 0",
            "2": "displaced / binary 1",
        },
        conditions=CONDITIONS,
        representations={k: v.shape[1] for (cid, k), v in features.items() if cid == 1},
        estimator="StandardScaler -> LinearDiscriminantAnalysis(solver=lsqr, shrinkage=auto, priors=[0.5,0.5])",
        validation="Leave one complete run out, separately within each participant/session",
        selection="Intersection of accepted trial IDs in all four saved conditions; no additional flag exclusions",
        tuning="None; fixed settings for every condition and feature representation",
        primary_auc="Unweighted mean of held-out-run ROC-AUCs; pooled OOF AUC saved as secondary",
        total_trials=n,
        configurations=12,
        fits=len(folds),
        prediction_rows=len(predictions),
        verification=[
            "all features finite",
            "exactly one OOF prediction per trial/configuration",
            "identical held-out trial IDs across configurations",
            "whole-run train/test separation",
            "scaler fitted on training fold only",
            "both labels present in every training/test fold",
        ],
    )
    (HERE / "analysis_settings.json").write_text(
        json.dumps(settings, indent=2), encoding="utf-8"
    )
    print(
        f"CLASSIFICATION COMPLETE: {len(folds)} fits; {len(predictions)} held-out predictions.",
        flush=True,
    )


if __name__ == "__main__":
    main()
