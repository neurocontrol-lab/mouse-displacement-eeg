"""Fixed full-dataset decoder evaluation: personalised, whole-run holdouts."""

# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
from collections import defaultdict
import csv
import json

import numpy as np
import scipy
from scipy.io import loadmat
import sklearn
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

HERE = ROOT / "output/DEC_decoding/DEC_02_full_cohort_decoders"
PILOT = code_path("DEC_01")
sys.path.insert(0, str(PILOT))
from analyse_classification import make_lda
from analyse_decision_tree import TREE_PARAMS

MODELS = {
    "LDA_full": ("LDA, all eight", list(range(56))),
    "LDA_central": ("LDA, Cz/FCz", list(range(35, 49))),
    "DT_full": ("Decision tree, all eight", list(range(56))),
}
SESSIONS = ["pre", "post", "retest"]
METRICS = [
    "balanced_accuracy",
    "accuracy",
    "sensitivity_D",
    "specificity_ND",
    "roc_auc",
]


def read(name):
    with (HERE / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    assert rows, name
    with (HERE / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def measure(y, predicted, score):
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    sensitivity = tp / (tp + fn) if tp + fn else np.nan
    specificity = tn / (tn + fp) if tn + fp else np.nan
    return dict(
        n=len(y),
        n_ND=int(np.sum(y == 0)),
        n_D=int(np.sum(y == 1)),
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
        balanced_accuracy=float((sensitivity + specificity) / 2),
        accuracy=float(np.mean(y == predicted)),
        sensitivity_D=float(sensitivity),
        specificity_ND=float(specificity),
        roc_auc=float(roc_auc_score(y, score)) if len(set(y)) == 2 else np.nan,
    )


def mean_defined(values):
    values = np.array(values, dtype=float)
    return (
        float(np.mean(values[np.isfinite(values)]))
        if np.isfinite(values).any()
        else np.nan
    )


def main():
    metadata = read("trial_metadata.csv")
    mat = loadmat(HERE / "features.mat")
    features = mat["features"]
    assert features.shape == (len(metadata), 56) and np.isfinite(features).all()
    assert [str(x.item()) for x in mat["channels"].ravel()] == [
        "P3",
        "PO3",
        "PO7",
        "CP5",
        "CP1",
        "Cz",
        "FCz",
        "FC1",
    ]
    assert np.allclose(mat["binStart"].ravel(), np.arange(7) / 10 + 0.2)
    assert len({(m["run"], m["trial"]) for m in metadata}) == len(metadata)
    yall = np.array([int(m["label"]) - 1 for m in metadata])
    assert set(yall) == {0, 1}
    subjects = sorted({r["subject"] for r in read("recording_inventory.csv")})
    assert len(subjects) == 25
    predictions, folds, summary, statuses = [], [], [], []
    evaluated = set()
    with threadpool_limits(limits=1):
        for subject in subjects:
            for session in SESSIONS:
                ids = np.array(
                    [
                        i
                        for i, m in enumerate(metadata)
                        if (m["subject"], m["session"]) == (subject, session)
                    ],
                    dtype=int,
                )
                cohort = "pilot" if subject in ["mle01", "spe30"] else "validation"
                y = yall[ids]
                groups = np.array([metadata[i]["run"] for i in ids])
                n_runs = len(set(groups))
                status = "ok"
                splits = []
                if n_runs < 2:
                    status = "fewer_than_two_accepted_recordings"
                elif len(set(y)) < 2:
                    status = "only_one_accepted_class"
                else:
                    splits = list(LeaveOneGroupOut().split(ids, y, groups))
                    if any(len(set(y[train])) < 2 for train, test in splits):
                        status = "a_training_fold_has_only_one_class"
                statuses.append(
                    dict(
                        subject=subject,
                        session=session,
                        cohort=cohort,
                        status=status,
                        n_accepted=len(ids),
                        n_ND=int(np.sum(y == 0)),
                        n_D=int(np.sum(y == 1)),
                        n_accepted_recordings=n_runs,
                    )
                )
                if status != "ok":
                    print(
                        f"{subject}/{session}: excluded from CV: {status}; accepted={len(ids)}, runs={n_runs}",
                        flush=True,
                    )
                    continue
                evaluated.update(ids.tolist())
                for model_id, (name, columns) in MODELS.items():
                    X = features[ids][:, columns]
                    oof_pred = np.full(len(ids), -1)
                    oof_score = np.full(len(ids), np.nan)
                    oof_dummy = np.full(len(ids), -1)
                    seen = np.zeros(len(ids), dtype=int)
                    current = []
                    for train, test in splits:
                        assert not set(groups[train]) & set(groups[test])
                        assert len(set(groups[test])) == 1
                        model = (
                            DecisionTreeClassifier(**TREE_PARAMS)
                            if model_id == "DT_full"
                            else make_lda()
                        )
                        model.fit(X[train], y[train])
                        if model_id != "DT_full":
                            assert np.allclose(model[0].mean_, X[train].mean(axis=0))
                        predicted = model.predict(X[test])
                        score = (
                            model.predict_proba(X[test])[:, 1]
                            if model_id == "DT_full"
                            else model.decision_function(X[test])
                        )
                        assert np.isfinite(score).all()
                        dummy = np.full(
                            len(test), np.bincount(y[train], minlength=2).argmax()
                        )
                        oof_pred[test], oof_score[test], oof_dummy[test] = (
                            predicted,
                            score,
                            dummy,
                        )
                        seen[test] += 1
                        result = measure(y[test], predicted, score)
                        base = dict(
                            subject=subject,
                            session=session,
                            cohort=cohort,
                            model_id=model_id,
                            model=name,
                            n_features=len(columns),
                        )
                        row = dict(
                            **base,
                            heldout_run=str(groups[test][0]),
                            n_train=len(train),
                            train_ND=int(np.sum(y[train] == 0)),
                            train_D=int(np.sum(y[train] == 1)),
                            **result,
                            dummy_accuracy=float(np.mean(dummy == y[test])),
                            tree_depth=(
                                model.get_depth() if model_id == "DT_full" else ""
                            ),
                            tree_leaves=(
                                model.get_n_leaves() if model_id == "DT_full" else ""
                            ),
                        )
                        folds.append(row)
                        current.append(row)
                        for local, pred, decision in zip(test, predicted, score):
                            m = metadata[ids[local]]
                            predictions.append(
                                dict(
                                    **base,
                                    run=m["run"],
                                    run_number=int(m["runNumber"]),
                                    trial=int(m["trial"]),
                                    original_label=int(m["label"]),
                                    true_D=int(y[local]),
                                    predicted_D=int(pred),
                                    score=float(decision),
                                )
                            )
                    assert np.all(seen == 1) and np.isfinite(oof_score).all()
                    result = measure(y, oof_pred, oof_score)
                    result["pooled_oof_roc_auc"] = result.pop("roc_auc")
                    for metric in METRICS:
                        result[f"mean_run_{metric}"] = mean_defined(
                            [r[metric] for r in current]
                        )
                    result["runs_with_defined_auc"] = sum(
                        np.isfinite(r["roc_auc"]) for r in current
                    )
                    result["min_run_balanced_accuracy"] = (
                        min(
                            r["balanced_accuracy"]
                            for r in current
                            if np.isfinite(r["balanced_accuracy"])
                        )
                        if any(np.isfinite(r["balanced_accuracy"]) for r in current)
                        else np.nan
                    )
                    result["max_run_balanced_accuracy"] = (
                        max(
                            r["balanced_accuracy"]
                            for r in current
                            if np.isfinite(r["balanced_accuracy"])
                        )
                        if any(np.isfinite(r["balanced_accuracy"]) for r in current)
                        else np.nan
                    )
                    result["dummy_accuracy"] = float(np.mean(oof_dummy == y))
                    summary.append(dict(**base, n_runs=n_runs, **result))
                    print(
                        f"{cohort} {subject}/{session} {model_id}: n={len(ids)}, runs={n_runs}, "
                        f'BA={result["balanced_accuracy"]:.3f}, AUC={result["mean_run_roc_auc"]:.3f}',
                        flush=True,
                    )
    assert len(predictions) == 3 * len(evaluated)
    assert len({(r["run"], r["trial"], r["model_id"]) for r in predictions}) == len(
        predictions
    )
    write("session_eligibility.csv", statuses)
    write("session_metrics.csv", summary)
    write("fold_metrics.csv", folds)
    write("heldout_predictions.csv", predictions)
    from summarise_results import summarise

    summarise(summary, folds, statuses)
    settings = dict(
        sklearn=sklearn.__version__,
        numpy=np.__version__,
        scipy=scipy.__version__,
        python=sys.version,
        participants=subjects,
        pilots=["mle01", "spe30"],
        preprocessing="Saved v1 fourth-order continuous 1-20 Hz Butterworth, zero phase; no FORCe; "
        "baseline [-0.2,0); final two-second peak absolute amplitude <=100 microvolts; "
        "raw gap/finite/edge checks over [-1.5,1.5) with two-second guards",
        feature_interval="[0.2,0.9) s",
        bin_ms=100,
        models={
            name: dict(label=label, n_features=len(columns))
            for name, (label, columns) in MODELS.items()
        },
        lda="Training-fold StandardScaler -> LDA(solver=lsqr,shrinkage=auto,priors=[0.5,0.5])",
        tree_parameters=TREE_PARAMS,
        tree_class_handling="Equal sample weights, empirical class proportions",
        validation="Leave one complete recording run out within each participant/session; identical folds for all models",
        selection="All no-FORCe accepted trials; no FORCe acceptance intersection",
        cohort_aggregation="Mean of eligible sessions within each participant, then equal-weight participant mean; pilots separate",
        missing_data="Session needs >=2 accepted recording runs and both labels in every training fold. "
        "Single-class test folds remain predicted; their AUC and fold BA are undefined, explicitly counted.",
        tuning="None; all three configurations fixed after the two-participant pilot",
        n_accepted_trials=len(metadata),
        n_evaluated_trials=len(evaluated),
        n_predictions=len(predictions),
        n_fits=len(folds),
        n_evaluated_sessions=sum(r["status"] == "ok" for r in statuses),
    )
    (HERE / "analysis_settings.json").write_text(
        json.dumps(settings, indent=2), encoding="utf-8"
    )
    print(
        f"FULL DATASET COMPLETE: {len(evaluated)} evaluated trials; {len(folds)} fits; {len(predictions)} predictions.",
        flush=True,
    )


if __name__ == "__main__":
    main()
