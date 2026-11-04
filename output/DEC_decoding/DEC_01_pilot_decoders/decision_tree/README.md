# Decision tree with our features

## Scope

A binary decision tree, as used as the classifier family in the Graz paper, applied to our 14 mean-amplitude features: seven consecutive 100 ms bins per channel, Cz and FCz, over [0.2, 0.9) s. Only the primary BP no-FORCe condition is used. The existing LDA results are preserved and reused for comparison.

## Method and relation to Graz

The paper reports a binary decision tree, 100 r-squared-ranked channel/time-point features selected within training folds, and 10-fold cross-validation. It does not state tree depth, minimum leaf size, splitting criterion, pruning or class-weight settings. Our shared legacy classifier blocks do not supply that published decision-tree setup. This is therefore a **Graz-style classifier with our features**, not an exact reproduction.

The tree uses sklearn CART: Gini impurity, best binary split, all 14 features available, minimum split size 2, minimum leaf size 1, unrestricted depth, no pruning, no class weights, random seed 20261027. These are explicit default assumptions, not recovered Graz settings. No hyperparameters, thresholds or features were tuned using test data. No scaling is applied to the tree.

We retain the exact whole-run holdouts from the LDA analysis, separately within each participant/session: five runs each except spe30/retest (four). Every one of the 2,562 matched trials has one held-out prediction from each decoder. This makes the local decoder comparison paired; it does not match the paper's 10-fold evaluation. No new preprocessing, FORCe optimisation or trial exclusions were performed.

**Class handling differs:** the tree uses equal sample weights and empirical class proportions; saved LDA uses equal class priors. Differences therefore concern the configured decoders, including class handling, rather than architecture alone.

## Results

Each row aggregates the held-out predictions in that participant/session. BA is the mean of D sensitivity and ND specificity. AUC is first computed within each held-out run and then averaged. Overall accuracy is directly affected by class imbalance; the majority-ND baseline is shown for context.

| Participant / session | Decoder | Accuracy | BA | D sensitivity | ND specificity | Mean run AUC |
|---|---|---:|---:|---:|---:|---:|
| mle01 / pre | Decision tree | 0.695 | 0.665 | 0.566 | 0.764 | 0.665 |
| mle01 / pre | Shrinkage LDA | 0.655 | 0.676 | 0.747 | 0.605 | 0.712 |
| mle01 / post | Decision tree | 0.735 | 0.706 | 0.614 | 0.798 | 0.691 |
| mle01 / post | Shrinkage LDA | 0.690 | 0.695 | 0.711 | 0.679 | 0.703 |
| mle01 / retest | Decision tree | 0.759 | 0.735 | 0.652 | 0.819 | 0.749 |
| mle01 / retest | Shrinkage LDA | 0.794 | 0.796 | 0.803 | 0.789 | 0.837 |
| spe30 / pre | Decision tree | 0.760 | 0.760 | 0.763 | 0.758 | 0.760 |
| spe30 / pre | Shrinkage LDA | 0.863 | 0.842 | 0.775 | 0.908 | 0.918 |
| spe30 / post | Decision tree | 0.781 | 0.757 | 0.680 | 0.833 | 0.757 |
| spe30 / post | Shrinkage LDA | 0.843 | 0.827 | 0.775 | 0.878 | 0.900 |
| spe30 / retest | Decision tree | 0.651 | 0.648 | 0.639 | 0.658 | 0.648 |
| spe30 / retest | Shrinkage LDA | 0.646 | 0.654 | 0.677 | 0.631 | 0.713 |

| Participant / session | ND / D | Majority-ND accuracy |
|---|---:|---:|
| mle01 / pre | 309 / 166 | 0.651 |
| mle01 / post | 218 / 114 | 0.657 |
| mle01 / retest | 237 / 132 | 0.642 |
| spe30 / pre | 326 / 169 | 0.659 |
| spe30 / post | 329 / 169 | 0.661 |
| spe30 / retest | 260 / 133 | 0.662 |

Unweighted descriptive means across the six participant/session results:

| Decoder | Accuracy | BA | D sensitivity | ND specificity | Mean run AUC |
|---|---:|---:|---:|---:|---:|
| Decision tree | 0.730 | 0.712 | 0.652 | 0.771 | 0.711 |
| Shrinkage LDA | 0.748 | 0.748 | 0.748 | 0.748 | 0.797 |

As configured, LDA has higher balanced accuracy in 5/6 participant/session analyses. Mean BA is 71.2% for the decision tree and 74.8% for LDA. This is a descriptive pilot comparison, not evidence of a population difference. The figure marks the majority-ND accuracy separately; the 0.5 line is used only as a balanced-accuracy reference.

These six results come from two participants and are not six independent subjects. Fold means and standard deviations are saved separately for comparison with the paper's reporting style; fold spread is not a population confidence interval.

The unpruned trees had depths 9–14, with training accuracy 1.000–1.000. These are fixed, unpruned baseline results; a tuned/pruned tree would be a separate experiment. Pure leaves give scores 0 or 1; consequently tree AUC can equal balanced accuracy within a run. These probabilities are not calibrated.

## Interpretation limits

- Compare the two decoders on these shared trial IDs and folds. Do not attribute a numerical difference from a published Graz figure to improved features: our preprocessing, features, acceptance set, session grouping and validation differ.
- This experiment changes the classifier while keeping our features fixed. It does not test our features against the Graz r-squared-selected features.
- Generalisation to unseen participants or sessions and the neural source of predictive information remain untested. The same pilots already informed feature choice.

## Reproduction and files



- `session_metrics.csv`: both decoders, overall/class-wise accuracy, BA, AUC and run means/SDs.
- `fold_metrics.csv`: identical held-out-run comparisons and tree training complexity.
- `heldout_predictions.csv`: individual decision-tree predictions and leaf probabilities.
- `paired_fold_differences.csv`: DT minus LDA on each identical held-out run.
- `analysis_settings.json`: exact parameters, assumptions and differences from Graz.
- `decoder_comparison.png`: session-wise comparison figure.

Sources: [Graz paper](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf), [sklearn DecisionTreeClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html).

[Methods, settings and execution order](../../../../Code/analyses/DEC_decoding/README.md#dec_01)
