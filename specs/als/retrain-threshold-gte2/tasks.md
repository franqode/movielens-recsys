# Tasks — als-v1 retrain at threshold >= 2

Discrete checklist for assembling the validation notebook. Mark each `[x]` as it
is completed. Maps to plan tasks t6 (spec) → t7 (notebook).

## Build implicit matrix (threshold >= 2)

- [ ] Load ratings only (`userId, movieId, rating, timestamp`) into the
      notebook (self-contained, no `src/` split; no tabular user/item features).
- [ ] EDA: print `n_users`, `n_movies`, `n_ratings`, sparsity; plot raw rating
      distribution and the positive (>=2) vs non-positive/unobserved imbalance.
- [ ] Build implicit user-item confidence matrix: observed `1 + 40 * rating`,
      unobserved `0`; relevance/binarization threshold `rating >= 2`.

## Split + relevant set + candidate pool

- [ ] Chronological 80/10/10 split by timestamp (train / validation / test).
- [ ] Fit matrix built from train only.
- [ ] Define per-test-user relevant set = held-out test items with `rating >= 2`.
- [ ] Define per-test-user candidate pool = items not rated by that user in train.
- [ ] Exclude test users with empty relevant set.

## Train ALS

- [ ] Fit `implicit.als.AlternatingLeastSquares(factors=64, alpha=40,
      regularization=0.1, iterations=15, random_state=<fixed>)`.
- [ ] Log hyperparameters (factors, alpha, regularization, iterations,
      random_state) for the run.

## Evaluate (no baseline)

- [ ] Score candidates per test user; rank desc; take top-10.
- [ ] Compute mean NDCG@10 (primary), precision@10, recall@10, hit-rate@10 over
      evaluated test users.

## Log to MLflow + record

- [ ] Log run to MLflow: metrics (NDCG@10, precision@10, recall@10, hit-rate@10)
      + model artifact, registry name `als-v1`.
- [ ] Tag run: `code_version` (git sha), `data_version` (data hash),
      `intent = als-v1-gte2`.
- [ ] Register model under the `test` alias only (no Staging/Production).
- [ ] Append run id + metrics + hyperparameters to `memory/als/experiments.md`.
