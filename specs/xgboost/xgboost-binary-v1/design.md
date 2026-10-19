# Design — xgboost-binary-v1

Technical decisions for assembling the validation notebook. The notebook is
self-contained (all logic inline, no `src/` split) and produces a binary XGBoost
recommendation model validated under the MLflow `test` alias.

## Decision: pointwise binary framing `{1, 2 -> 0, 3, 4, 5 -> 1}`

Keep ALL ratings in `{1, 2, 3, 4, 5}`, map `1 -> 0`, `2 -> 0` and `3 -> 1`,
`4 -> 1`, `5 -> 1`, and train a pointwise binary classifier
(`objective: binary:logistic`). Ranking is produced by sorting candidates by
predicted `P(positive)` descending, per user.

Rationale: 3-, 4-, and 5-star are treated as positive and 1- and 2-star as
negative, using the full rating range with no data dropped; a pointwise
classifier over this set is a cheap, interpretable proof of a ranking model with
no embedding training. This is exactly the human's revised framing
(`xgboost-binary-v1`).

## Decision: tabular features only (no embeddings)

- user: `age`, `gender` (one-hot), `occupation` (one-hot).
- item: `genres` (multi-hot), `release_year`.
- interaction: `user_mean_rating`, `item_mean_rating`, `user_rating_count`,
  `item_rating_count`.

Rationale: XGBoost works on tabular features; avoiding embeddings keeps the
proof simple and interpretable, and the interaction statistics give the
classifier user/item popularity signals.

## Decision: leakage guard on interaction statistics

`user_mean_rating`, `item_mean_rating`, `user_rating_count`, `item_rating_count`
are computed from training folds only and mapped onto validation/test rows by
user/item key. This prevents the model from seeing its own target through the
aggregate (a row's rating must not be counted into its own mean).

## Decision: chronological 80/10/10 split

Sort by timestamp, take the earliest 80% as train, next 10% as validation, last
10% as test. This respects the temporal nature of recommendation and prevents
future information leaking into training. Test users' held-out positive
(3-, 4-, or 5-star) items are the ground-truth relevant set for ranking
evaluation.

## Decision: ranking evaluation with popularity baseline

For each test user:
- relevant set = held-out positive (3-, 4-, or 5-star) movies (in test).
- candidate pool = movies not rated by that user in train (optionally capped for
  speed).
- rank candidates by predicted `P(positive)` descending, take top 10.
- `precision@10 = |top10 ∩ relevant| / 10`; `recall@10 = |top10 ∩ relevant| / |relevant|`.

Report the mean over test users (excluding users with empty relevant sets), and
compare against a popularity baseline (top-10 movies by rating count) computed
on the same users and candidate pool.

## Decision: class imbalance handling

Positive (3-star + 4-star + 5-star) dominates negative (1-star + 2-star). We
keep logistic objective and record `scale_pos_weight` explicitly so the
imbalance is visible and tunable; we do not down/up-sample at this stage.

## Decision: reproducibility

Fixed seed `42` for XGBoost (`random_state=42`), deterministic chronological
split, and all hyperparameters (`max_depth`, `n_estimators`, `learning_rate`,
`scale_pos_weight`) logged as MLflow params.

## Decision: MLflow `test` alias only

The run is logged with tags `code_version` (git sha), `data_version` (data
hash), `intent` (`xgboost-binary-v1`), metrics `precision@10`/`recall@10`, and
the model registered under `test`. No `Staging`/`Production` promotion at this
stage (that happens only after the human gate and `mle-engineer` implementation).

## Rejected alternative

- **Keep only `{1, 4, 5}`** (map `1 -> 0`, `4 -> 1`, `5 -> 1`, dropping 2 and
  3). Rejected because the human now wants the `{1, 2 -> 0, 3, 4, 5 -> 1}`
  framing: keeping all ratings and treating 1-/2-star as negative and
  3-/4-/5-star as positive uses the full rating range with no data dropped,
  broadening both classes beyond the single extreme ratings and matching the
  revised hypothesis.

- **Pairwise/learning-to-rank loss** (e.g. `rank:pairwise`). Rejected for this
  validation step: the idea is a *pointwise* binary classifier ranked by
  predicted probability; pairwise ranking is a follow-on hypothesis, not part of
  `xgboost-binary-v1`.

- **Embeddings / matrix factorization features**. Rejected: XGBoost is the
  tabular proof; embedding-derived features are out of scope for this idea.
