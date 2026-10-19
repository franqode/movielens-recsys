# Tasks — svd (prove-all-models-gte4, task t8)

Discrete checklist for assembling the validation notebook. Mark each `[x]` as it
is completed. Maps to plan tasks t8 (spec) and t9 (notebook, `test` alias).

## Load + EDA

- [ ] Load ratings only (`userId, movieId, rating, timestamp`) into the
      notebook (self-contained, no `src/` split; no tabular user/item features).
- [ ] EDA: print `n_users`, `n_movies`, `n_ratings`, sparsity; plot the raw
      rating distribution and the relevance threshold (`rating >= 4` vs not).

## Split

- [ ] Chronological 80/10/10 split by timestamp (train / validation / test)
      under a fixed seed.
- [ ] Fit SVD on train (earliest 80%) ratings only; validation/test (last 20%)
      reserved for held-out evaluation.

## Train SVD

- [ ] Fit `surprise.SVD(n_factors=100, n_epochs=20, biased=True, lr_all=0.005,
      reg_all=0.02, random_state=<fixed>)` on the train rating matrix.
- [ ] Log hyperparameters (`n_factors`, `n_epochs`, `biased`, `lr_all`,
      `reg_all`, `random_state`) as MLflow params.

## Evaluate (ranking, k=10)

- [ ] Define per-test-user relevant set = held-out test items with `rating >= 4`.
- [ ] Define per-test-user candidate pool = items not rated by that user in train.
- [ ] Score each candidate by SVD predicted rating; rank descending; take top 10.
- [ ] Exclude test users with empty relevant set.
- [ ] Compute mean `precision@10` (primary), `NDCG@10`, `recall@10`,
      `hit-rate@10` over evaluated test users.

## Log to MLflow + record

- [ ] Log run to MLflow: metrics (precision@10, NDCG@10, recall@10, hit-rate@10)
      + model artifact, registry name `svd-v1`.
- [ ] Tag run: `code_version` (git sha), `data_version` (data hash),
      `intent = svd-v1-gte4`.
- [ ] Register model under the `test` alias only (no Staging/Production).
- [ ] Append run id + metrics + hyperparameters to `memory/svd/experiments.md`.

Note: the inline popularity baseline (`>= 4`) comparison is intentionally NOT in
this notebook — it is added as the shared step t10 across all four notebooks.
