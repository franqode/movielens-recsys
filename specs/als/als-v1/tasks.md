# Tasks — als-v1

Discrete checklist for assembling the validation notebook. Mark each `[x]` as it
is completed. Maps to plan tasks t2–t6.

## Build implicit matrix (plan t2)

- [x] Load ratings only (`userId, movieId, rating, timestamp`) into the
      notebook (self-contained, no `src/` split; no tabular user/item features).
- [x] EDA: print `n_users`, `n_movies`, `n_ratings`, sparsity; plot raw rating
      distribution and the positive (>=4) vs non-positive/unobserved imbalance.
- [x] Build implicit user-item confidence matrix: observed `1 + 40 * rating`,
      unobserved `0`; relevance/binarization threshold `rating >= 4`.

## Split + relevant set + candidate pool (plan t3)

- [x] Chronological 80/10/10 split by timestamp (train / validation / test).
- [x] Fit matrix built from train only.
- [x] Define per-test-user relevant set = held-out test items with `rating >= 4`.
- [x] Define per-test-user candidate pool = items not rated by that user in train.
- [x] Exclude test users with empty relevant set (applied to model and all
      baselines).

## Train ALS (plan t4)

- [x] Fit `implicit.als.AlternatingLeastSquares(factors=64, alpha=40,
      regularization=0.1, iterations=15, random_state=<fixed>)`.
- [x] Log hyperparameters (factors, alpha, regularization, iterations,
      random_state) for the run.

## Evaluate vs baseline (plan t5)

- [x] Score candidates per test user; rank desc; take top-10.
- [x] Compute mean NDCG@10 (primary), precision@10, recall@10, hit-rate@10 over
      evaluated test users.
- [x] Compute inline popularity baseline (top-10 by train rating count) metrics
      on the same users and candidate pool.
- [x] Compare ALS vs `xgboost-v1` v8 (T=4: NDCG@10=0.057167, precision@10=0.055219,
      recall@10=0.015145); report ALS NDCG@10 >= baseline (primary) plus deltas.
- [x] Compare ALS hit-rate@10 vs inline popularity (xgboost never logged
      hit-rate@10).

## Log to MLflow + record (plan t6)

- [x] Log run to MLflow: metrics (NDCG@10, precision@10, recall@10, hit-rate@10)
      + model artifact, registry name `als-v1`.
- [x] Tag run: `code_version` (git sha), `data_version` (data hash),
      `intent = als-implicit-beats-test-baseline`.
- [x] Register model under the `test` alias only (no Staging/Production).
- [x] Append run id + metrics + hyperparameters to `memory/als/experiments.md`.
