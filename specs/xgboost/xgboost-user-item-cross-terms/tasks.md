# Tasks — xgboost-user-item-cross-terms

Discrete checklist for assembling the validation notebook. Mark each `[x]` as it
is completed. Maps to plan tasks t2–t5.

## Load & frame (plan t2)

- [ ] Load ratings (+ users/movies) into the notebook (self-contained, no `src/`).
- [ ] Keep all ratings 1–5; build binary labels for each threshold
      `T ∈ {2, 3, 4, 5}` as `label = 1 if rating >= T else 0` (T=2 → `{1→0,
      2,3,4,5→1}`; T=3 → `{1,2→0, 3,4,5→1}`; T=4 → `{1,2,3→0, 4,5→1}`; T=5 →
      `{1,2,3,4→0, 5→1}`).
- [ ] Reproduce the 47 base features (user age/gender/occupation; item
      genres/release_year; interaction user_mean_rating, item_mean_rating,
      user_rating_count, item_rating_count) with train-fold-only interaction
      stats (leakage guard).

## Affinity + cross-term features (plan t2)

- [ ] Compute `global_mean` over training ratings.
- [ ] Compute `user_genre_affinity[g]` (18 values) via shrunk mean-rating
      deviation `(sum(rating - global_mean)) / (count + 5)`, train-fold only,
      fallback 0.0 for unseen (user, genre).
- [ ] Build 24 cross terms: `um_x_im`, `um_x_ic`, `uc_x_im`, `uc_x_ic`,
      `age_x_year`, `genre_affinity_score` (dot product), 18 `aff_x_genre_{g}`.
- [ ] Add the 18 standalone `user_genre_affinity[g]` columns.
- [ ] Confirm final feature count == 89 (47 + 24 + 18); no scaling; no
      demographic × item terms.

## Split & evaluation setup (plan t2/t4)

- [ ] Chronological 80/10/10 split (train/validation/test) by timestamp.
- [ ] Define relevant set per threshold T = held-out items with `rating >= T`
      per test user.
- [ ] Define candidate pool = full catalog minus train-rated items per test user;
      exclude empty-relevant users from the mean.

## Train (plan t3)

- [ ] Train XGBoost per threshold T with `objective: binary:logistic`, seed 42,
      `max_depth=6`.
- [ ] Log hyperparameters per threshold: max_depth, n_estimators, learning_rate,
      scale_pos_weight (scale_pos_weight varies with T).
- [ ] Report feature importance (gain and/or weight) for the best-threshold
      model; highlight cross/affinity columns.

## Evaluate (plan t4)

- [ ] For each threshold `T ∈ {2, 3, 4, 5}`: compute per-user precision@10
      (primary), recall@10, NDCG@10; report mean over included test users.
- [ ] For each threshold, compute popularity baseline (top-10 by rating count)
      on the same users, candidate pool, and relevant sets; report the same
      three metrics.
- [ ] Compare model vs prior `test`-alias run `fdab1c40799f460db34a2ec60e8c9774`
      (v7) and vs popularity baseline at each threshold; report deltas.
- [ ] Identify the best threshold by precision@10 (ties broken by higher
      NDCG@10); report the per-threshold table and the best threshold.

## Log & record (plan t5)

- [ ] Log run to MLflow: per-threshold metrics (precision@10, recall@10, NDCG@10),
      best threshold, + model artifact.
- [ ] Tag run: code_version (git sha), data_version (data hash),
      intent = xgboost-user-item-cross-terms.
- [ ] Register model under the `test` alias (no Staging/Production).
- [ ] Append run id + per-threshold metrics + best threshold + hyperparams to
      memory/xgboost/experiments.md.
