"""Graz-style binary tree with our 100 ms features, versus saved matched LDA.

The paper does not specify tree hyperparameters. Use explicit CART defaults,
no tuning, and the existing whole-run holdouts. Only condition 1 is analysed.
"""

# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv
import json

import numpy as np
from scipy.io import loadmat
import sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneGroupOut

from analyse_classification import metrics, SUBJECTS, SESSIONS

HERE = ROOT / "output/DEC_decoding/DEC_01_pilot_decoders"
OUT = HERE / "decision_tree"
SEED = 20261027
TREE_PARAMS = dict(
    criterion="gini",
    splitter="best",
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features=None,
    max_leaf_nodes=None,
    min_impurity_decrease=0.0,
    class_weight=None,
    ccp_alpha=0.0,
    random_state=SEED,
)
MODELS = ["Decision tree", "Shrinkage LDA"]


def read(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def measure(y, prediction, score):
    result = metrics(y, prediction, score)
    result["accuracy"] = float(np.mean(y == prediction))
    return result


def main():
    OUT.mkdir(exist_ok=True)
    metadata = read(HERE / "trial_metadata.csv")
    raw = loadmat(HERE / "central_features.mat")["rawFeatures"]
    # Input export is Cz samples then FCz samples; average 50 samples per 100 ms bin.
    n = len(metadata)
    assert raw.shape == (n, 700, 4)
    Xall = raw[:, :, 0].reshape(n, 2, 7, 50).mean(axis=-1).reshape(n, 14)
    assert np.isfinite(Xall).all()
    yall = np.array([int(m["label"]) - 1 for m in metadata])
    lda_predictions = [
        r
        for r in read(HERE / "heldout_predictions.csv")
        if r["condition_id"] == "1" and r["representation"] == "100ms"
    ]
    lda = {(r["run"], int(r["trial"])): r for r in lda_predictions}
    assert len(lda) == len(lda_predictions) == n
    old_folds = {
        (r["subject"], r["session"], r["heldout_run"]): r
        for r in read(HERE / "fold_metrics.csv")
        if r["condition_id"] == "1" and r["representation"] == "100ms"
    }
    folds, sessions, predictions, differences = [], [], [], []
    for subject in SUBJECTS:
        for session in SESSIONS:
            selected = np.array(
                [
                    i
                    for i, m in enumerate(metadata)
                    if (m["subject"], m["session"]) == (subject, session)
                ]
            )
            X, y = Xall[selected], yall[selected]
            groups = np.array([metadata[i]["run"] for i in selected])
            seen = np.zeros(len(selected), dtype=int)
            oof = {
                name: (np.full(len(selected), -1), np.full(len(selected), np.nan))
                for name in MODELS
            }
            current_folds = {name: [] for name in MODELS}
            for train, test in LeaveOneGroupOut().split(X, y, groups):
                assert not set(groups[train]) & set(groups[test])
                assert set(y[train]) == set(y[test]) == {0, 1}
                run = str(groups[test][0])
                assert len(set(groups[test])) == 1
                old = old_folds[subject, session, run]
                assert int(old["n"]) == len(test) and int(old["n_train"]) == len(train)
                assert int(old["n_D"]) == int(np.sum(y[test] == 1))
                tree = DecisionTreeClassifier(**TREE_PARAMS)
                tree.fit(X[train], y[train])
                assert list(tree.classes_) == [0, 1]
                outputs = {
                    "Decision tree": (
                        tree.predict(X[test]),
                        tree.predict_proba(X[test])[:, 1],
                    )
                }
                saved = [
                    lda[metadata[i]["run"], int(metadata[i]["trial"])]
                    for i in selected[test]
                ]
                assert [int(r["true_D"]) for r in saved] == y[test].tolist()
                outputs["Shrinkage LDA"] = (
                    np.array([int(r["predicted_D"]) for r in saved]),
                    np.array([float(r["decision_score"]) for r in saved]),
                )
                seen[test] += 1
                for model in MODELS:
                    prediction, score = outputs[model]
                    result = measure(y[test], prediction, score)
                    if model == "Shrinkage LDA":
                        assert (
                            abs(
                                result["balanced_accuracy"]
                                - float(old["balanced_accuracy"])
                            )
                            < 1e-12
                        )
                        assert abs(result["roc_auc"] - float(old["roc_auc"])) < 1e-12
                    oof[model][0][test] = prediction
                    oof[model][1][test] = score
                    row = dict(
                        subject=subject,
                        session=session,
                        model=model,
                        heldout_run=run,
                        n_train=len(train),
                        train_ND=int(np.sum(y[train] == 0)),
                        train_D=int(np.sum(y[train] == 1)),
                        **result,
                        tree_depth=tree.get_depth() if model == "Decision tree" else "",
                        tree_leaves=(
                            tree.get_n_leaves() if model == "Decision tree" else ""
                        ),
                        train_accuracy=(
                            float(tree.score(X[train], y[train]))
                            if model == "Decision tree"
                            else ""
                        ),
                    )
                    folds.append(row)
                    current_folds[model].append(row)
                    if model == "Decision tree":
                        for local, predicted, probability in zip(
                            test, prediction, score
                        ):
                            m = metadata[selected[local]]
                            predictions.append(
                                dict(
                                    subject=subject,
                                    session=session,
                                    run=run,
                                    run_number=int(m["runNumber"]),
                                    trial=int(m["trial"]),
                                    original_label=int(m["label"]),
                                    true_D=int(y[local]),
                                    predicted_D=int(predicted),
                                    probability_D=float(probability),
                                )
                            )
                first, second = (
                    current_folds[MODELS[0]][-1],
                    current_folds[MODELS[1]][-1],
                )
                differences.append(
                    dict(
                        subject=subject,
                        session=session,
                        heldout_run=run,
                        **{
                            f"delta_{metric}_DT_minus_LDA": first[metric]
                            - second[metric]
                            for metric in [
                                "accuracy",
                                "balanced_accuracy",
                                "roc_auc",
                                "sensitivity_D",
                                "specificity_ND",
                            ]
                        },
                    )
                )
            assert np.all(seen == 1)
            for model in MODELS:
                predicted, score = oof[model]
                assert np.isfinite(score).all()
                result = measure(y, predicted, score)
                result["pooled_oof_roc_auc"] = result.pop("roc_auc")
                for metric in [
                    "accuracy",
                    "balanced_accuracy",
                    "roc_auc",
                    "sensitivity_D",
                    "specificity_ND",
                ]:
                    values = [r[metric] for r in current_folds[model]]
                    result[f"mean_run_{metric}"] = float(np.mean(values))
                    result[f"sd_run_{metric}"] = float(np.std(values, ddof=1))
                result["majority_ND_accuracy"] = float(np.mean(y == 0))
                sessions.append(
                    dict(
                        subject=subject,
                        session=session,
                        model=model,
                        n_runs=len(current_folds[model]),
                        **result,
                    )
                )
                print(
                    f'{subject}/{session} {model}: accuracy={result["accuracy"]:.3f}, '
                    f'BA={result["balanced_accuracy"]:.3f}, '
                    f'mean-run AUC={result["mean_run_roc_auc"]:.3f}',
                    flush=True,
                )
    assert len(predictions) == n == 2562 and len(folds) == 58 and len(differences) == 29
    assert len({(r["run"], r["trial"]) for r in predictions}) == n
    write("heldout_predictions.csv", predictions)
    write("fold_metrics.csv", folds)
    write("session_metrics.csv", sessions)
    write("paired_fold_differences.csv", differences)
    settings = dict(
        sklearn=sklearn.__version__,
        condition_id=1,
        condition="BP no-FORCe",
        channels=["Cz", "FCz"],
        feature_interval="[0.2, 0.9) seconds",
        bin_ms=100,
        n_features=14,
        sample_weight=None,
        tree_parameters=DecisionTreeClassifier(**TREE_PARAMS).get_params(),
        validation="Identical leave-one-whole-run-out folds to the saved LDA, separately by participant/session",
        tuning="None. Parameters fixed before inspecting decision-tree scores.",
        lda_source="../heldout_predictions.csv; condition 1, 100ms; no LDA refit",
        tree_score="Uncalibrated leaf probability of displaced class; often 0 or 1 for an unpruned tree",
        lda_score="Saved LDA decision function; AUC calculated within run, then averaged",
        match_to_Graz="Binary decision-tree family only; paper does not report tree hyperparameters.",
        differences_from_Graz=[
            "Our 14 binned Cz/FCz features, not 100 r-squared-ranked channel/time samples",
            "Whole-run holdouts, not reported 10-fold CV",
            "Sessions separate, not per-subject pooled evaluation",
            "No-FORCe primary condition and matched common accepted trial subset",
            "Explicit sklearn default tree assumptions; original software/settings not recovered",
        ],
        class_handling="DT: equal sample weights, empirical class proportions. Saved LDA: equal class priors. "
        "The comparison is between these configured decoders, not model architecture alone.",
        n_trials=n,
        tree_fits=29,
        total_comparison_folds=58,
        paper="https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf",
    )
    (OUT / "analysis_settings.json").write_text(
        json.dumps(settings, indent=2), encoding="utf-8"
    )
    summarise(sessions, folds)


def summarise(sessions, folds):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = [(s, v) for s in SUBJECTS for v in SESSIONS]
    colors = {"Decision tree": "#b46222", "Shrinkage LDA": "#1b5e91"}
    fig, axes = plt.subplots(
        2, 2, figsize=(12, 7), constrained_layout=True, sharex=True
    )
    for ax, metric, title in zip(
        axes.ravel(),
        ["balanced_accuracy", "accuracy", "sensitivity_D", "specificity_ND"],
        [
            "Balanced accuracy",
            "Overall accuracy",
            "Displaced sensitivity",
            "Non-displaced specificity",
        ],
    ):
        for model, offset in zip(MODELS, [-0.13, 0.13]):
            values = [
                next(
                    r[metric]
                    for r in sessions
                    if (r["subject"], r["session"], r["model"]) == (s, v, model)
                )
                for s, v in groups
            ]
            ax.bar(
                np.arange(6) + offset,
                values,
                width=0.25,
                label=model,
                color=colors[model],
            )
        if metric == "balanced_accuracy":
            ax.axhline(0.5, color=".4", linestyle="--", linewidth=0.8)
        if metric == "accuracy":
            majority = [
                next(
                    r["majority_ND_accuracy"]
                    for r in sessions
                    if (r["subject"], r["session"], r["model"]) == (s, v, MODELS[0])
                )
                for s, v in groups
            ]
            ax.scatter(
                range(6),
                majority,
                color=".3",
                marker="_",
                s=350,
                linewidths=2,
                label="Majority ND (overall accuracy)",
                zorder=5,
            )
        ax.set_ylim(0, 1)
        ax.set_title(title)
        ax.set_xticks(range(6), [f"{s}\n{v}" for s, v in groups], fontsize=9)
        ax.grid(axis="y", alpha=0.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    other_handles, other_labels = axes[0, 1].get_legend_handles_labels()
    baseline_index = other_labels.index("Majority ND (overall accuracy)")
    handles.append(other_handles[baseline_index])
    labels.append(other_labels[baseline_index])
    fig.legend(handles, labels, loc="outside lower center", ncol=3)
    fig.suptitle(
        "Primary no-FORCe | Cz/FCz, 14 × 100 ms features | Matched whole-run holdouts"
    )
    fig.savefig(OUT / "decoder_comparison.png", dpi=180)
    plt.close(fig)
    lines = [
        "# Decision tree with our features",
        "",
        "## Scope",
        "",
        "A binary decision tree, as used as the classifier family in the Graz paper, applied to our "
        "14 mean-amplitude features: seven consecutive 100 ms bins per channel, Cz and FCz, "
        "over [0.2, 0.9) s. Only the primary BP no-FORCe condition is used. "
        "The existing LDA results are preserved and reused for comparison.",
        "",
        "## Method and relation to Graz",
        "",
        "The paper reports a binary decision tree, 100 r-squared-ranked channel/time-point "
        "features selected within training folds, and 10-fold cross-validation. It does not state "
        "tree depth, minimum leaf size, splitting criterion, pruning or class-weight settings. "
        "Our shared legacy classifier blocks do not supply that published decision-tree setup. "
        "This is therefore a **Graz-style classifier with our features**, not an exact reproduction.",
        "",
        "The tree uses sklearn CART: Gini impurity, best binary split, all 14 features available, "
        "minimum split size 2, minimum leaf size 1, unrestricted depth, no pruning, no class "
        "weights, random seed 20261027. These are explicit default assumptions, not recovered "
        "Graz settings. No hyperparameters, thresholds or features were tuned using test data. "
        "No scaling is applied to the tree.",
        "",
        "We retain the exact whole-run holdouts from the LDA analysis, separately within each "
        "participant/session: five runs each except spe30/retest (four). Every one of the 2,562 "
        "matched trials has one held-out prediction from each decoder. This makes the local "
        "decoder comparison paired; it does not match the paper's 10-fold evaluation. "
        "No new preprocessing, FORCe optimisation or trial exclusions were performed.",
        "",
        "**Class handling differs:** the tree uses equal sample weights and empirical class "
        "proportions; saved LDA uses equal class priors. Differences therefore concern the "
        "configured decoders, including class handling, rather than architecture alone.",
        "",
        "## Results",
        "",
        "Each row aggregates the held-out predictions in that participant/session. BA is the "
        "mean of D sensitivity and ND specificity. AUC is first computed within each held-out "
        "run and then averaged. Overall accuracy is directly affected by class imbalance; "
        "the majority-ND baseline is shown for context.",
        "",
        "| Participant / session | Decoder | Accuracy | BA | D sensitivity | ND specificity | Mean run AUC |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in sessions:
        lines.append(
            f"| {r['subject']} / {r['session']} | {r['model']} | {r['accuracy']:.3f} | "
            f"{r['balanced_accuracy']:.3f} | {r['sensitivity_D']:.3f} | {r['specificity_ND']:.3f} | {r['mean_run_roc_auc']:.3f} |"
        )
    lines += [
        "",
        "| Participant / session | ND / D | Majority-ND accuracy |",
        "|---|---:|---:|",
    ]
    for r in sessions:
        if r["model"] == "Decision tree":
            lines.append(
                f"| {r['subject']} / {r['session']} | {r['n_ND']} / {r['n_D']} | {r['majority_ND_accuracy']:.3f} |"
            )
    lines += [
        "",
        "Unweighted descriptive means across the six participant/session results:",
        "",
        "| Decoder | Accuracy | BA | D sensitivity | ND specificity | Mean run AUC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model in MODELS:
        selected = [r for r in sessions if r["model"] == model]
        values = [
            np.mean([r[k] for r in selected])
            for k in [
                "accuracy",
                "balanced_accuracy",
                "sensitivity_D",
                "specificity_ND",
                "mean_run_roc_auc",
            ]
        ]
        lines.append(f"| {model} | " + " | ".join(f"{v:.3f}" for v in values) + " |")
    lookup = {(r["subject"], r["session"], r["model"]): r for r in sessions}
    wins = sum(
        lookup[s, v, "Shrinkage LDA"]["balanced_accuracy"]
        > lookup[s, v, "Decision tree"]["balanced_accuracy"]
        for s, v in groups
    )
    means = {
        model: np.mean(
            [r["balanced_accuracy"] for r in sessions if r["model"] == model]
        )
        for model in MODELS
    }
    lines += [
        "",
        f"As configured, LDA has higher balanced accuracy in {wins}/6 participant/session "
        f"analyses. Mean BA is {100*means['Decision tree']:.1f}% for the decision tree and "
        f"{100*means['Shrinkage LDA']:.1f}% for LDA. This is a descriptive pilot comparison, "
        "not evidence of a population difference. The figure marks the majority-ND accuracy "
        "separately; the 0.5 line is used only as a balanced-accuracy reference.",
    ]
    dt = [r for r in folds if r["model"] == "Decision tree"]
    lines += [
        "",
        "These six results come from two participants and are not six independent subjects. "
        "Fold means and standard deviations are saved separately for comparison with the "
        "paper's reporting style; fold spread is not a population confidence interval.",
        "",
        f"The unpruned trees had depths {min(r['tree_depth'] for r in dt)}–{max(r['tree_depth'] for r in dt)}, "
        f"with training accuracy {min(r['train_accuracy'] for r in dt):.3f}–{max(r['train_accuracy'] for r in dt):.3f}. "
        "These are fixed, unpruned baseline results; a tuned/pruned tree would be a separate "
        "experiment. Pure leaves give scores 0 or 1; consequently tree AUC can equal "
        "balanced accuracy within a run. These probabilities are not calibrated.",
        "",
        "## Interpretation limits",
        "",
        "- Compare the two decoders on these shared trial IDs and folds. Do not attribute "
        "a numerical difference from a published Graz figure to improved features: our "
        "preprocessing, features, acceptance set, session grouping and validation differ.",
        "- This experiment changes the classifier while keeping our features fixed. It does "
        "not test our features against the Graz r-squared-selected features.",
        "- Generalisation to unseen participants or sessions and the neural source of "
        "predictive information remain untested. The same pilots already informed feature choice.",
        "",
        "## Reproduction and files",
        "",
        "[Methods, settings and execution order](../../../../Code/analyses/DEC_decoding/README.md#dec_01).",
        "",
        "- `session_metrics.csv`: both decoders, overall/class-wise accuracy, BA, AUC and run means/SDs.",
        "- `fold_metrics.csv`: identical held-out-run comparisons and tree training complexity.",
        "- `heldout_predictions.csv`: individual decision-tree predictions and leaf probabilities.",
        "- `paired_fold_differences.csv`: DT minus LDA on each identical held-out run.",
        "- `analysis_settings.json`: exact parameters, assumptions and differences from Graz.",
        "- `decoder_comparison.png`: session-wise comparison figure.",
        "",
        "Sources: [Graz paper](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf), "
        "[sklearn DecisionTreeClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html).",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        "COMPLETE: 29 tree fits, 2562 matched held-out predictions, preserved LDA reference.",
        flush=True,
    )


if __name__ == "__main__":
    main()
