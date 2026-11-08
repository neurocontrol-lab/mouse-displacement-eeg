"""Within-run permutation inference for four fixed, personalised decoders.

Run after DEC_02 and DEC_03 feature preparation. No feature/model tuning occurs.
Session scores pool held-out predictions; participant scores average eligible
sessions equally. Labels are shuffled within recordings, assuming exchangeability
within each recording. Cached raw moments accelerate training-only r-squared
ranking; all classifiers and supervised ranking are refitted per permutation.
"""

from pathlib import Path
import sys

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path

sys.path.insert(0, str(code_path("DEC_01")))
sys.path.insert(0, str(code_path("DEC_03")))
from analyse_classification import make_lda
from analyse_decision_tree import TREE_PARAMS
from analyse_graz_comparison import rank_r_squared
import argparse
import csv
import json
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import scipy
import sklearn
from scipy.io import loadmat
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

MODELS = ["LDA_full", "LDA_central", "DT_full", "DT_r2_epoch"]
NAMES = [
    "LDA, all eight",
    "LDA, Cz/FCz",
    "Decision tree, all eight",
    "Graz-style top-100 amplitude tree",
]
SESSIONS = ["pre", "post", "retest"]
SEED = 20261106


def read(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def balanced_accuracy(y, prediction):
    # Pool all test recordings before taking the mean of the two class recalls.
    return 0.5 * (np.mean(prediction[y == 0] == 0) + np.mean(prediction[y == 1] == 1))


def run_session(task):
    subject, session = task["subject"], task["session"]
    X, y, groups = task["X"], task["y"], task["groups"]
    n_perm, output = task["permutations"], Path(task["output"])
    path = output / "session_nulls" / f"{subject}_{session}.npz"
    raw_data = loadmat(
        result_path("DEC_03") / "raw_epochs" / f"{subject}_{session}.mat"
    )
    raw = raw_data["rawFeatures"]
    assert np.array_equal(raw_data["globalRows"].ravel() - 1, task["global_rows"])
    assert raw.shape == (len(y), 8000) and np.isfinite(raw).all()
    del raw_data
    folds = []
    for train, test in LeaveOneGroupOut().split(X, y, groups):
        assert not set(groups[train]) & set(groups[test])
        train_raw = raw[train]
        mean = train_raw.mean(axis=0)
        centered = train_raw - mean
        folds.append(
            dict(
                train=train,
                test=test,
                raw_test=raw[test],
                mean=mean,
                ss=np.einsum("ij,ij->j", centered, centered),
            )
        )
        del train_raw, centered

    def evaluate(labels, check_ranking=False):
        predicted = np.full((len(labels), 4), -1)
        # Each test recording appears once. Subtracting its moments leaves
        # exactly the training recordings, without using held-out labels.
        projections = np.array([labels[f["test"]] @ f["raw_test"] for f in folds])
        total_projection = projections.sum(axis=0)
        for i, fold in enumerate(folds):
            train, test = fold["train"], fold["test"]
            yt = labels[train]
            covariance = total_projection - projections[i] - yt.sum() * fold["mean"]
            # The omitted label-variance factor is common to every feature.
            r2 = np.divide(
                covariance**2, fold["ss"], out=np.zeros(8000), where=fold["ss"] > 0
            )
            keep = np.argsort(-r2, kind="stable")[:100]
            if check_ranking:
                direct, _ = rank_r_squared(raw[train], yt)
                assert np.array_equal(keep, direct), (
                    subject,
                    session,
                    "ranking mismatch",
                )
            for m, model_id in enumerate(MODELS):
                if model_id == "DT_r2_epoch":
                    train_x, test_x = raw[np.ix_(train, keep)], raw[np.ix_(test, keep)]
                else:
                    columns = (
                        list(range(35, 49))
                        if model_id == "LDA_central"
                        else list(range(56))
                    )
                    train_x, test_x = (
                        X[np.ix_(train, columns)],
                        X[np.ix_(test, columns)],
                    )
                model = (
                    make_lda()
                    if model_id.startswith("LDA")
                    else DecisionTreeClassifier(**TREE_PARAMS)
                )
                model.fit(train_x, yt)
                predicted[test, m] = model.predict(test_x)
        assert np.all(predicted >= 0)
        return (
            np.array([balanced_accuracy(labels, predicted[:, m]) for m in range(4)]),
            predicted,
        )

    with threadpool_limits(limits=1):
        observed, prediction = evaluate(y, check_ranking=True)
        assert np.array_equal(prediction, task["expected"]), (
            subject,
            session,
            "saved prediction mismatch",
        )
        null = np.empty((n_perm, 4))
        done = 0
        if path.exists():
            cached = np.load(path)
            assert int(cached["seed"]) == SEED and np.allclose(
                cached["observed"], observed, atol=1e-14, rtol=0
            )
            assert cached["models"].tolist() == MODELS
            done = min(n_perm, len(cached["null"]))
            null[:done] = cached["null"][:done]
        start = time.perf_counter()
        for b in range(done, n_perm):
            rng = np.random.default_rng(
                np.random.SeedSequence(
                    [SEED, task["subject_index"], SESSIONS.index(session), b]
                )
            )
            permuted = y.copy()
            for fold in folds:
                idx = fold["test"]
                permuted[idx] = rng.permutation(y[idx])
                assert permuted[idx].sum() == y[idx].sum()
            null[b], _ = evaluate(permuted, check_ranking=(b == 0))
            if (b + 1) % 100 == 0 or b + 1 == n_perm:
                np.savez_compressed(
                    path,
                    null=null[: b + 1],
                    observed=observed,
                    models=MODELS,
                    seed=SEED,
                )
                print(
                    f"{subject}/{session}: {b+1}/{n_perm} permutations; {time.perf_counter()-start:.1f}s this invocation",
                    flush=True,
                )
    return dict(
        subject=subject,
        session=session,
        cohort=task["cohort"],
        n=len(y),
        observed=observed,
        null=null,
    )


def inference(observed, null):
    exceedances = int(np.count_nonzero(null >= observed - 1e-12))
    return dict(
        balanced_accuracy=float(observed),
        null_mean=float(null.mean()),
        chance_95=float(np.quantile(null, 0.95, method="higher")),
        exceedances=exceedances,
        p_value=(exceedances + 1) / (len(null) + 1),
        permutations=len(null),
        mc_resolution=1 / (len(null) + 1),
    )


def summarise(results, output):
    participants = []
    sessions = []
    subjects = sorted({r["subject"] for r in results})
    for r in sorted(
        results, key=lambda r: (r["subject"], SESSIONS.index(r["session"]))
    ):
        for m, model in enumerate(MODELS):
            sessions.append(
                dict(
                    subject=r["subject"],
                    session=r["session"],
                    cohort=r["cohort"],
                    model_id=model,
                    model=NAMES[m],
                    n_trials=r["n"],
                    **inference(r["observed"][m], r["null"][:, m]),
                )
            )
    for subject in subjects:
        rows = [r for r in results if r["subject"] == subject]
        observed = np.mean([r["observed"] for r in rows], axis=0)
        null = np.mean([r["null"] for r in rows], axis=0)
        for m, model in enumerate(MODELS):
            cohort = rows[0]["cohort"]
            family = (
                "exploratory_pilot"
                if cohort == "pilot"
                else ("primary_validation" if m == 0 else "secondary_validation")
            )
            participants.append(
                dict(
                    subject=subject,
                    cohort=cohort,
                    model_id=model,
                    model=NAMES[m],
                    family=family,
                    n_sessions=len(rows),
                    n_trials=sum(r["n"] for r in rows),
                    **inference(observed[m], null[:, m]),
                )
            )
    for family in sorted({r["family"] for r in participants}):
        rows = sorted(
            [r for r in participants if r["family"] == family],
            key=lambda r: r["p_value"],
        )
        previous = 0
        for rank, r in enumerate(rows):
            previous = max(previous, min(1, (len(rows) - rank) * r["p_value"]))
            r["p_holm"] = previous
            r["family_size"] = len(rows)
            r["significant_holm_05"] = int(previous <= 0.05)
    write(output / "participant_significance.csv", participants)
    write(output / "session_significance.csv", sessions)
    counts = []
    for m, model in enumerate(MODELS):
        for cohort in ["validation", "pilot"]:
            rows = [
                r
                for r in participants
                if r["model_id"] == model and r["cohort"] == cohort
            ]
            if rows:
                counts.append(
                    dict(
                        cohort=cohort,
                        model_id=model,
                        model=NAMES[m],
                        participants=len(rows),
                        significant_holm_05=sum(r["significant_holm_05"] for r in rows),
                        mean_balanced_accuracy=float(
                            np.mean([r["balanced_accuracy"] for r in rows])
                        ),
                    )
                )
    write(output / "cohort_summary.csv", counts)
    print("PERMUTATION SUMMARY", counts, flush=True)


def load_session_results(output, args):
    results = []
    for status in read(result_path("DEC_02") / "session_eligibility.csv"):
        subject, session = status["subject"], status["session"]
        if status["status"] != "ok":
            continue
        if args.subjects and subject not in args.subjects:
            continue
        if args.sessions and session not in args.sessions:
            continue
        with np.load(output / "session_nulls" / f"{subject}_{session}.npz") as saved:
            assert int(saved["seed"]) == SEED and saved["models"].tolist() == MODELS
            null = saved["null"][: args.permutations].copy()
            assert null.shape == (args.permutations, 4) and np.isfinite(null).all()
            results.append(
                dict(
                    subject=subject,
                    session=session,
                    cohort=status["cohort"],
                    n=int(status["n_accepted"]),
                    observed=saved["observed"].copy(),
                    null=null,
                )
            )
    assert results
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--permutations", type=int, default=1999)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--summarise-only",
        action="store_true",
        help="Rebuild inference from completed null-score arrays; no refits",
    )
    parser.add_argument("--subjects", nargs="*")
    parser.add_argument("--sessions", nargs="*", choices=SESSIONS)
    parser.add_argument("--output", type=Path, default=result_path("DEC_04"))
    args = parser.parse_args()
    assert args.permutations > 0
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    (output / "session_nulls").mkdir(exist_ok=True)
    if args.summarise_only:
        summarise(load_session_results(output, args), output)
        return
    metadata = read(result_path("DEC_02") / "trial_metadata.csv")
    features = loadmat(result_path("DEC_02") / "features.mat")["features"]
    expected = defaultdict(dict)
    for experiment in ["DEC_02", "DEC_03"]:
        with (result_path(experiment) / "heldout_predictions.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            for r in csv.DictReader(stream):
                if r["model_id"] in MODELS:
                    expected[(r["subject"], r["session"], r["model_id"])][
                        (r["run"], int(r["trial"]))
                    ] = int(r["predicted_D"])
    by_session = defaultdict(list)
    for i, r in enumerate(metadata):
        by_session[r["subject"], r["session"]].append(i)
    subjects = sorted({r["subject"] for r in metadata})
    tasks = []
    for status in read(result_path("DEC_02") / "session_eligibility.csv"):
        subject, session = status["subject"], status["session"]
        if status["status"] != "ok":
            continue
        if args.subjects and subject not in args.subjects:
            continue
        if args.sessions and session not in args.sessions:
            continue
        idx = np.array(by_session[subject, session])
        rows = [metadata[i] for i in idx]
        prediction = np.array(
            [
                [
                    expected[subject, session, m][(r["run"], int(r["trial"]))]
                    for m in MODELS
                ]
                for r in rows
            ]
        )
        tasks.append(
            dict(
                subject=subject,
                session=session,
                cohort=status["cohort"],
                X=features[idx],
                y=np.array([int(r["label"]) - 1 for r in rows]),
                groups=np.array([r["run"] for r in rows]),
                expected=prediction,
                global_rows=idx,
                subject_index=subjects.index(subject),
                permutations=args.permutations,
                output=str(output),
            )
        )
    assert tasks
    config = dict(
        permutations=args.permutations,
        seed=SEED,
        models=MODELS,
        sessions=len(tasks),
        statistic="session pooled OOF balanced accuracy, then equal mean of eligible sessions",
        shuffle="independently within each recording; same shuffled labels for all four models",
        assumptions="labels exchangeable within recording under the null; no claim of independent individual trials",
        families={
            "primary_validation": len(
                {t["subject"] for t in tasks if t["cohort"] == "validation"}
            ),
            "secondary_validation": 3
            * len({t["subject"] for t in tasks if t["cohort"] == "validation"}),
            "exploratory_pilot": 4
            * len({t["subject"] for t in tasks if t["cohort"] == "pilot"}),
        },
        pilot_caveat="pilot feature/model selection is not repeated; pilot tests remain exploratory",
        p_value="(1 + count(null >= observed))/(1 + permutations)",
        threshold="95th percentile, higher empirical quantile; unadjusted, descriptive",
        versions={
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
        },
        model_settings={
            "LDA": {
                "solver": "lsqr",
                "shrinkage": "auto",
                "priors": [0.5, 0.5],
                "training_standardisation": True,
            },
            "tree": TREE_PARAMS,
        },
    )
    (output / "settings.json").write_text(json.dumps(config, indent=2) + "\n")
    results = []
    if args.workers == 1:
        for task in tasks:
            results.append(run_session(task))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(run_session, t) for t in tasks]
            for future in as_completed(futures):
                results.append(future.result())
    summarise(results, output)


if __name__ == "__main__":
    main()
