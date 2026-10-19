# plan: xgboost-user-item-cross-terms

- idea: xgboost-user-item-cross-terms
- status: pending
- sdd: true
- goal: prove in a notebook that adding user-item cross terms (multiplicative
  interaction features) to the pointwise XGBoost recommender beats the current
  tabular model and the popularity baseline on precision@10.

## Design decisions

- Base (unchanged): pointwise XGBoost, 47 tabular features, framing
  `{1,2 -> 0, 3,4,5 -> 1}` (keep all ratings), chronological 80/10/10 split,
  seed 42, `max_depth=6` (no hyperparameter change).
- New prerequisite feature `user_genre_affinity[g]` (18 values): shrunk
  mean-rating deviation per (user, genre), computed on training folds only
  (leakage guard), fallback 0.0 for unseen (user, genre):
  `affinity[u,g] = (sum over u's train ratings in genre g of (rating - global_mean)) / (count_u,g + 5)`.
- New cross terms (24):
  - `um_x_im` = user_mean_rating x item_mean_rating
  - `um_x_ic` = user_mean_rating x item_rating_count
  - `uc_x_im` = user_rating_count x item_mean_rating
  - `uc_x_ic` = user_rating_count x item_rating_count
  - `age_x_year` = age x release_year
  - `genre_affinity_score` = sum_g affinity[g] x genre[g] (single dot-product)
  - `aff_x_genre_{g}` = affinity[g] x genre[g] (18, one per genre)
- Standalone affinity: also add the 18 `user_genre_affinity[g]` values as
  standalone features.
- Total features: 47 + 24 + 18 = 89.
- No scaling (XGBoost is monotonic-scale invariant). Skip demographic x item
  terms (age x item_mean_rating, age x item_rating_count).
- Evaluation: single ablation. Same split/seed/metrics as the current notebook.
  Compare vs (a) the current `test`-alias run `fdab1c40799f460db34a2ec60e8c9774`
  (v7) and (b) the popularity baseline.
- Metrics: precision@10 (primary), recall@10 and NDCG@10 (secondary).
- MLflow: log under `test` alias, `intent=xgboost-user-item-cross-terms`, tags
  `code_version`/`data_version`.

## tasks

- [x] t1 write spec of how to assemble the notebook                               owner: spec_author     sdd: true
- [x] t2 build user_genre_affinity + cross-term features (89 total)               owner: data-scientist  sdd: false
- [x] t3 train XGBoost (seed 42, max_depth=6, logged hyperparams)                 owner: data-scientist  sdd: false
- [x] t4 evaluate precision@10 / recall@10 / NDCG@10 vs baseline + prior run      owner: data-scientist  sdd: false
- [x] t5 log run to MLflow under `test` alias; update experiments.md              owner: data-scientist  sdd: false

After the notebook-validation HUMAN GATE passes, implementation follows (a
follow-on plan): `mle-engineer` implements into `src/` + `Staging`, then
`mlops-engineer` serves, then `reviewer` verifies completion.
