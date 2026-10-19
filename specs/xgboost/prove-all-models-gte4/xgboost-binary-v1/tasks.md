# Tasks — xgboost-binary-v1 @ `rating >= 4` (prove-all-models-gte4)

Discrete checklist for assembling the validation notebook. Mark each `[x]` as it
is completed. Maps to plan tasks t2/t3 of `prove-all-models-gte4`.

## Load & frame (plan t2)

- [ ] Load ratings (+ users/movies) into the notebook (self-contained, no `src/`).
- [ ] Keep all ratings 1–5; map `rating >= 4 -> 1` and `rating < 4 -> 0`
      (i.e. `1, 2, 3 -> 0`; `4, 5 -> 1`).
- [ ] Print label counts and ratio (class balance); note the imbalance
      (positive 4+5-star ≈ 57.5%, negative 1+2+3-star ≈ 42.5%).
- [ ] EDA: rating distribution plot, class-balance plot, and table of
      n_users, n_movies, n_ratings, sparsity.

## Features (plan t2)

- [ ] Build user features: age, gender one-hot, occupation one-hot.
- [ ] Build item features: genres multi-hot, release_year.
- [ ] Build interaction features from train-fold stats only:
      user_mean_rating, item_mean_rating, user_rating_count, item_rating_count.
- [ ] Confirm the feature matrix has the same 47 columns as the prior spec
      (no embedding-derived columns) and no leakage (interaction stats computed
      on train folds only).

## Split & evaluation setup (plan t2)

- [ ] Chronological 80/10/10 split (train/validation/test) by timestamp.
- [ ] Define relevant set = held-out positive (`rating >= 4`) items per test user.
- [ ] Define candidate pool = full catalog minus items rated by each test user
      in train (optionally capped for speed).

## Train (plan t2)

- [ ] Train XGBoost with `objective: binary:logistic`, `max_depth=6`, seed 42.
- [ ] Log hyperparameters: max_depth, n_estimators, learning_rate,
      scale_pos_weight.
- [ ] Report feature importance (gain and/or weight).

## Evaluate (plan t2)

- [ ] Compute per-user precision@10 (primary), NDCG@10, and recall@10; report
      mean over test users.
- [ ] Do NOT compute any popularity baseline (deferred to shared plan step t10).

## Log & record (plan t2)

- [ ] Log run to MLflow: metrics (precision@10, NDCG@10, recall@10) + model
      artifact.
- [ ] Tag run: code_version (git sha), data_version (data hash),
      intent = xgboost-binary-v1-gte4.
- [ ] Register model `xgboost-v1` under the `test` alias (no Staging/Production).
- [ ] Append run id + metrics + hyperparams to memory/xgboost/experiments.md.
