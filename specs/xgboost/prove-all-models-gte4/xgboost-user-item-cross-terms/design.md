# Design — xgboost-user-item-cross-terms @ rating >= 4

Technical decisions for assembling the validation notebook as part of plan
`prove-all-models-gte4` (task t4). The notebook is self-contained (all logic
inline, no `src/` split) and retrains the 89-feature cross-terms XGBoost
recommender at a single fixed threshold `rating >= 4`, validated under the
MLflow `test` alias in registry `xgboost-v1`.

## Decision: single fixed threshold `>= 4` (no sweep)

The prior cross-terms notebook swept the binary cutoff over `T ∈ {2, 3, 4, 5}`
and reported per-threshold metrics, selecting the best threshold. This plan's
directive replaces that with a single fixed cutoff across ALL models:
`label = 1 if rating >= 4 else 0` (`1,2,3 -> 0`; `4,5 -> 1`). All ratings are
kept in every case — nothing is dropped.

Rationale: the human directive (`prove-all-models-gte4`) standardizes the
positive-label definition at `>= 4` so every model family is proven against the
same relevance definition and the same popularity baseline. A threshold sweep
would reintroduce per-model threshold selection and break cross-model
comparability.

The class imbalance is therefore a single fixed value: `scale_pos_weight =
n_negative / n_positive` computed from the `>= 4` label split (expected ~0.73,
i.e. 4/5-star positives outnumber 1/2/3-star negatives).

## Decision: unchanged features (89 total)

Everything about the feature matrix is inherited verbatim from the base
cross-terms spec:

- 47 base tabular features (user age/gender/occupation; item genres/release_year;
  interaction user_mean_rating, item_mean_rating, user_rating_count,
  item_rating_count) with train-fold-only leakage guards.
- 18 standalone `user_genre_affinity[g]` = shrunk mean-rating deviation
  `(sum(rating - global_mean)) / (count + 5)`, train-fold only, fallback 0.0.
- 24 cross terms: `um_x_im`, `um_x_ic`, `uc_x_im`, `uc_x_ic`, `age_x_year`,
  `genre_affinity_score` (dot product), 18 `aff_x_genre_{g}`.

Total 47 + 24 + 18 = 89. No scaling/normalization (XGBoost is monotonic-scale
invariant); no demographic × item terms (excluded by the plan).

## Decision: chronological 80/10/10 split, seed 42, max_depth=6

Unchanged from the prior notebook. The time-ordered global split guarantees no
temporal leakage, and the fixed seed / `max_depth=6` / `binary:logistic` hold
every knob fixed so the only thing that changed versus prior runs is the label
cutoff (and the removed baseline).

## Decision: relevance set = held-out items with `rating >= 4`

For each test user: relevant set = held-out items with `rating >= 4`; candidate
pool = full catalog minus the user's train-rated items; rank by predicted
P(positive) descending; take top 10. Users with an empty relevant set are
excluded from the mean. This matches the plan's shared eval protocol.

## Decision: NO inline popularity baseline

Per the plan, the popularity baseline comparison is factored out into a separate
shared step (t10) applied uniformly across all four model notebooks. This
notebook therefore does not compute or report any popularity-baseline ranking or
model-vs-baseline deltas; it reports the model's own metrics only. This avoids
duplicating the baseline logic (and any inconsistency) across notebooks and
keeps the t10 step the single authority for baseline comparison.

## Decision: metrics

`precision@10` is PRIMARY (optimization target); `recall@10` and `NDCG@10` are
secondary. All three are reported as the mean over included test users.

## Decision: MLflow `test` alias, registry `xgboost-v1`

Log with tags `code_version` (git sha), `data_version` (data hash),
`intent=xgboost-user-item-cross-terms-gte4`, metrics `precision@10` / `recall@10`
/ `NDCG@10`, hyperparameters (`max_depth`, `n_estimators`, `learning_rate`,
`scale_pos_weight`), and register the model under the `test` alias in registry
`xgboost-v1`. No `Staging`/`Production` promotion at this stage (that happens
only after the human gate and `mle-engineer` implementation).

## Rejected alternative

- **Threshold sweep over `{2, 3, 4, 5}` with best-threshold selection.** Rejected:
  the `prove-all-models-gte4` directive fixes the cutoff at `>= 4` across all
  models to enable a like-for-like comparison against the shared popularity
  baseline; a sweep would reintroduce per-model threshold selection and confound
  the cross-model comparison.

- **Inline popularity baseline inside this notebook.** Rejected: factored out to
  plan t10 so the baseline is computed once and applied uniformly to all four
  models, avoiding duplicated/divergent baseline logic.

- **Latent-factor features (ALS/SVD embeddings) as the collaborative signal.**
  Rejected (as in the base spec): `xgboost-user-item-cross-terms` is the
  *engineered*-cross-term hypothesis; mixing learned latent factors would
  confound which signal drives any gain.

- **Demographic × item cross terms (age × item_mean_rating, gender/occupation ×
  item).** Rejected: low expected signal, many columns with no clear hypothesis,
  and the plan explicitly excludes them.

- **Adding ranking objectives / hyperparameter tuning alongside the features.**
  Rejected: the run must stay comparable to prior cross-terms runs, so the
  objective and depth are held fixed.
