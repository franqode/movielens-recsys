# Design — xgboost-binary-v1 @ `rating >= 2` (retrain-threshold-gte2)

Technical decisions for assembling the validation notebook. The notebook is
self-contained (all logic inline, no `src/` split) and retrains the binary
XGBoost recommendation model with the positive-label cutoff at `rating >= 2`,
validated under the MLflow `test` alias. This design differs from the prior
`xgboost-binary-v1` spec in exactly two ways: the binarization threshold and the
removal of the popularity baseline.

## Decision: pointwise binary framing `rating >= 2 -> 1`

Keep ALL ratings in `{1, 2, 3, 4, 5}`, map `rating >= 2 -> 1` and
`rating < 2 -> 0` (i.e. `1 -> 0`; `2, 3, 4, 5 -> 1`), and train a pointwise
binary classifier (`objective: binary:logistic`). Ranking is produced by sorting
candidates by predicted `P(positive)` descending, per user.

Rationale: the human's directive is to retrain all existing models with the
`>= 2` cutoff, treating 2-star as positive alongside 3/4/5-star. This is a
strict relaxation of the prior `>= 3` framing. Class balance shifts sharply:
the positive class (2-5 star) now covers ~94% of ratings, with only 1-star
(~6%) as negative. `scale_pos_weight` is recorded explicitly so the imbalance is
visible and tunable; we do not down/up-sample at this stage.

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
(`rating >= 2`) items are the ground-truth relevant set for ranking evaluation.

## Decision: ranking evaluation with NO popularity baseline

For each test user:
- relevant set = held-out positive (`rating >= 2`) movies (in test).
- candidate pool = movies not rated by that user in train (full catalog minus
  train-rated, optionally capped for speed).
- rank candidates by predicted `P(positive)` descending, take top 10.
- `precision@10 = |top10 ∩ relevant| / 10`; `recall@10 = |top10 ∩ relevant| / |relevant|`;
  `NDCG@10` over the same top-10 with binary relevance.

Report the mean over test users (excluding users with empty relevant sets).
There is NO popularity baseline comparison: the human deleted the popularity
model, and it must not be recomputed or compared against here.

## Decision: reproducibility

Fixed seed `42` for XGBoost (`random_state=42`), deterministic chronological
split, `max_depth=6`, and all hyperparameters (`max_depth`, `n_estimators`,
`learning_rate`, `scale_pos_weight`) logged as MLflow params.

## Decision: MLflow `test` alias only, registry `xgboost-v1`

The run is logged with tags `code_version` (git sha), `data_version` (data
hash), `intent` (`xgboost-binary-v1-gte2`), metrics `precision@10` (primary) /
`recall@10` / `NDCG@10`, and the model registered under `xgboost-v1` with the
`test` alias. No `Staging`/`Production` promotion at this stage (that happens
only after the human gate and `mle-engineer` implementation). The `intent` tag
carries the `-gte2` suffix to distinguish this threshold-retrain run from the
original `xgboost-binary-v1` runs.

## Rejected alternative

- **Keep the `>= 3` cutoff.** Rejected: the human's directive is to retrain at
  `>= 2`; the whole point of this task is the threshold change.

- **Popularity baseline comparison.** Rejected/removed: the human deleted the
  popularity model; no popularity baseline may be recomputed or reported.

- **Pairwise/learning-to-rank loss** (e.g. `rank:pairwise`). Rejected for this
  validation step: the idea remains a *pointwise* binary classifier ranked by
  predicted probability; pairwise ranking is a separate follow-on hypothesis.

- **Embeddings / matrix factorization features.** Rejected: XGBoost is the
  tabular proof; embedding-derived features are out of scope for this idea.
