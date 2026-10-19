# Design — xgboost-binary-v1 @ `rating >= 4` (prove-all-models-gte4)

Technical decisions for assembling the validation notebook. The notebook is
self-contained (all logic inline, no `src/` split) and retrains the binary
XGBoost recommendation model with the positive-label cutoff at `rating >= 4`,
validated under the MLflow `test` alias. This design differs from the prior
`xgboost-binary-v1` spec in exactly two ways: the binarization threshold and the
removal of the popularity baseline (now deferred to shared plan step t10).

## Decision: pointwise binary framing `rating >= 4 -> 1`

Keep ALL ratings in `{1, 2, 3, 4, 5}`, map `rating >= 4 -> 1` and
`rating < 4 -> 0` (i.e. `1, 2, 3 -> 0`; `4, 5 -> 1`), and train a pointwise
binary classifier (`objective: binary:logistic`). Ranking is produced by sorting
candidates by predicted `P(positive)` descending, per user.

Rationale: the human's directive is to prove every model against the `>= 4`
cutoff, treating 4-/5-star as positive and 1-/2-/3-star as negative. This is a
stricter framing than the prior `>= 3` (which treated 3-star as positive) and
moves the model toward a "like vs dislike" signal. Class balance shifts: the
positive class (4-5 star) is now ~57.5% of ratings (≈ 575,281 of ~1,000,209),
with negative (1-2-3 star) at ~42.5% — roughly balanced (positive/negative ≈
1.35). `scale_pos_weight` is recorded explicitly so the imbalance is visible and
tunable; we do not down/up-sample at this stage.

## Decision: tabular features only (no embeddings) — unchanged 47 features

- user: `age`, `gender` (one-hot), `occupation` (one-hot).
- item: `genres` (multi-hot), `release_year`.
- interaction: `user_mean_rating`, `item_mean_rating`, `user_rating_count`,
  `item_rating_count`.

These are the same 47 features as the prior spec (47 columns in the assembled
feature matrix). No new features are introduced.

Rationale: the directive limits the change to the label threshold; features,
split, seed, and hyperparameters stay fixed so the retrain isolates the effect
of the threshold change.

## Decision: leakage guard on interaction statistics

`user_mean_rating`, `item_mean_rating`, `user_rating_count`, `item_rating_count`
are computed from training folds only and mapped onto validation/test rows by
user/item key. This prevents the model from seeing its own target through the
aggregate (a row's rating must not be counted into its own mean).

## Decision: chronological 80/10/10 split

Sort by timestamp, take the earliest 80% as train, next 10% as validation, last
10% as test. This respects the temporal nature of recommendation and prevents
future information leaking into training. Test users' held-out positive
(`rating >= 4`) items are the ground-truth relevant set for ranking evaluation.

## Decision: ranking evaluation with NO popularity baseline

For each test user:
- relevant set = held-out positive (`rating >= 4`) movies (in test).
- candidate pool = full catalog minus items rated by that user in train
  (optionally capped for speed).
- rank candidates by predicted `P(positive)` descending, take top 10.
- `precision@10 = |top10 ∩ relevant| / 10`; `recall@10 = |top10 ∩ relevant| / |relevant|`;
  `NDCG@10` over the same top-10 with binary relevance.

Report the mean over test users (excluding users with empty relevant sets).
`precision@10` is the PRIMARY optimization target; `NDCG@10` and `recall@10` are
secondary.

There is NO popularity baseline comparison inside this notebook. The popularity
comparison is applied as a SEPARATE shared step (plan t10) uniformly across all
four model notebooks, so it must not be built into this notebook now.

## Decision: reproducibility

Fixed seed `42` for XGBoost (`random_state=42`), deterministic chronological
split, `max_depth=6`, and all hyperparameters (`max_depth`, `n_estimators`,
`learning_rate`, `scale_pos_weight`) logged as MLflow params.

## Decision: MLflow `test` alias only, registry `xgboost-v1`

The run is logged with tags `code_version` (git sha), `data_version` (data
hash), `intent` (`xgboost-binary-v1-gte4`), metrics `precision@10` (primary) /
`NDCG@10` / `recall@10`, and the model registered under `xgboost-v1` with the
`test` alias. No `Staging`/`Production` promotion at this stage (that happens
only after the human gate and `mle-engineer` implementation). The `intent` tag
carries the `-gte4` suffix to distinguish this threshold-retrain run from the
original `xgboost-binary-v1` and `-gte2` runs.

## Rejected alternative

- **Keep the `>= 3` (or `>= 2`) cutoff.** Rejected: the human's directive is to
  prove every model at `>= 4`; the whole point of this task is the threshold
  change.

- **Popularity baseline comparison inside this notebook.** Rejected/removed:
  the popularity comparison is a SEPARATE shared step (plan t10) applied to all
  four notebooks; it must not be duplicated here.

- **Pairwise/learning-to-rank loss** (e.g. `rank:pairwise`). Rejected for this
  validation step: the idea remains a *pointwise* binary classifier ranked by
  predicted probability; pairwise ranking is a separate follow-on hypothesis.

- **Embeddings / matrix factorization features.** Rejected: XGBoost is the
  tabular proof; embedding-derived features are out of scope for this idea.
