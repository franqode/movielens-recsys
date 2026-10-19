# Tasks — als-v1 @ rating >= 4 (plan prove-all-models-gte4)

Discrete checklist for assembling the validation notebook. Mark each `[x]` as it
is completed. Maps to plan tasks t6 (spec) → t7 (notebook).

## Build implicit matrix (threshold >= 4)

- [ ] Load ratings only (`userId, movieId, rating, timestamp`) into the
      notebook (self-contained, no `src/` split; no tabular user/item features).
- [ ] EDA: print `n_users`, `n_movies`, `n_ratings`, sparsity; plot raw rating
      distribution and the positive (>=4) vs non-positive/unobserved imbalance.
- [ ] Build implicit user-item confidence matrix: observed `1 + 40 * rating`,
      unobserved `0`; relevance/binarization threshold `rating >= 4`.

## Split + relevant set + candidate pool

- [ ] Chronological 80/10/10 split by timestamp (train / validation / test).
- [ ] Fit matrix built from train only.
- [ ] Define per-test-user relevant set = held-out test items with `rating >= 4`.
- [ ] Define per-test-user candidate pool = items not rated by that user in train.
- [ ] Exclude test users with empty relevant set.

## Train ALS

- [ ] Fit `implicit.als.AlternatingLeastSquares(factors=64, alpha=40,
      regularization=0.1, iterations=15, random_state=<fixed>)`.
- [ ] Log hyperparameters (factors, alpha, regularization, iterations,
      random_state) for the run.

## Evaluate (no baseline)

- [ ] Score candidates per test user; rank desc; take top-10.
- [ ] Compute mean precision@10 (primary), NDCG@10, recall@10, hit-rate@10
      (secondary) over evaluated test users.

## Log to MLflow + record

- [ ] Log run to MLflow: metrics (precision@10, NDCG@10, recall@10, hit-rate@10)
      + model artifact, registry name `als-v1`.
- [ ] Tag run: `code_version` (git sha), `data_version` (data hash),
      `intent = als-v1-gte4`.
- [ ] Register model under the `test` alias only (no Staging/Production).
- [ ] Append run id + metrics + hyperparameters to `memory/als/experiments.md`.
