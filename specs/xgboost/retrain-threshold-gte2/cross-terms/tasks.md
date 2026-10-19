# Tasks — xgboost-user-item-cross-terms (retrain at threshold >= 2)

Discrete checklist for assembling the validation notebook. Mark each `[x]` as it
is completed. Maps to plan tasks t4/t5 of `retrain-threshold-gte2`.

## Load & frame

- [ ] Load ratings (+ users/movies) into the notebook (self-contained, no `src/`).
- [ ] Keep all ratings 1–5; build a single binary label `rating >= 2 -> 1`
      (rating 1 -> 0; ratings 2,3,4,5 -> 1). No threshold sweep.
- [ ] Print label counts and ratio (class balance); note positive ≈94%,
      negative ≈6%.
- [ ] Reproduce the 47 base features (user age/gender/occupation; item
      genres/release_year; interaction user_mean_rating, item_mean_rating,
      user_rating_count, item_rating_count) with train-fold-only interaction
      stats (leakage guard).

## Affinity + cross-term features

- [ ] Compute `global_mean` over training ratings.
- [ ] Compute `user_genre_affinity[g]` (18 values) via shrunk mean-rating
      deviation `(sum(rating - global_mean)) / (count + 5)`, train-fold only,
      fallback 0.0 for unseen (user, genre).
- [ ] Build 24 cross terms: `um_x_im`, `um_x_ic`, `uc_x_im`, `uc_x_ic`,
      `age_x_year`, `genre_affinity_score` (dot product), 18 `aff_x_genre_{g}`.
- [ ] Add the 18 standalone `user_genre_affinity[g]` columns.
- [ ] Confirm final feature count == 89 (47 + 24 + 18); no scaling; no
      demographic × item terms.

## Split & evaluation setup

- [ ] Chronological 80/10/10 split (train/validation/test) by timestamp.
- [ ] Define relevant set = held-out items with `rating >= 2` per test user.
- [ ] Define candidate pool = full catalog minus train-rated items per test user;
      exclude empty-relevant users from the mean.

## Train

- [ ] Train XGBoost with `objective: binary:logistic`, seed 42, `max_depth=6`
      (single model at the fixed threshold).
- [ ] Log hyperparameters: max_depth, n_estimators, learning_rate,
      scale_pos_weight (≈ negative/positive ratio ≈ 0.064).
- [ ] Report feature importance (gain and/or weight); highlight cross/affinity
      columns.

## Evaluate (no baseline, no prior-run comparison)

- [ ] Compute per-user precision@10 (primary), recall@10, NDCG@10; report mean
      over included test users.
- [ ] Confirm NO popularity baseline is computed and NO prior `test`-alias run is
      referenced or compared against.

## Log & record

- [ ] Log run to MLflow: metrics (precision@10, recall@10, NDCG@10) + model
      artifact.
- [ ] Tag run: code_version (git sha), data_version (data hash),
      intent = xgboost-user-item-cross-terms-gte2.
- [ ] Register model in the `xgboost-v1` registry under the `test` alias
      (no Staging/Production).
- [ ] Append run id + metrics + threshold (>= 2) + hyperparams to
      memory/xgboost/experiments.md.
