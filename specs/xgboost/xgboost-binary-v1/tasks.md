# Tasks — xgboost-binary-v1

Discrete checklist for assembling the validation notebook. Mark each `[x]` as it
is completed. Maps to plan tasks t2–t7.

## Load & frame (plan t2)

- [x] Load ratings (+ users/movies) into the notebook (self-contained, no `src/`).
- [x] Keep all ratings 1–5; map `1, 2 -> 0` and `3, 4, 5 -> 1`.
- [x] Print label counts and ratio (class balance); note the imbalance
      (positive 3+4+5-star dominates 1+2-star).
- [x] EDA: rating distribution plot, class-balance plot, and table of
      n_users, n_movies, n_ratings, sparsity.

## Features (plan t3)

- [x] Build user features: age, gender one-hot, occupation one-hot.
- [x] Build item features: genres multi-hot, release_year.
- [x] Build interaction features from train-fold stats only:
      user_mean_rating, item_mean_rating, user_rating_count, item_rating_count.
- [x] Confirm no embedding-derived columns and no leakage (interaction stats
      computed on train folds only).

## Split & evaluation setup (plan t4)

- [x] Chronological 80/10/10 split (train/validation/test) by timestamp.
- [x] Define relevant set = held-out positive (3-, 4-, or 5-star) items per test user.
- [x] Define candidate pool = movies unseen by each test user in train
      (optionally capped for speed).

## Train (plan t5)

- [x] Train XGBoost with `objective: binary:logistic`, fixed seed 42.
- [x] Log hyperparameters: max_depth, n_estimators, learning_rate,
      scale_pos_weight.
- [x] Report feature importance (gain and/or weight).

## Evaluate (plan t6)

- [x] Compute per-user precision@10 and recall@10; report mean over test users.
- [x] Compute popularity baseline (top-10 by rating count) precision@10 /
      recall@10 on the same users and candidate pool.
- [x] Compare model vs baseline (report deltas).

## Log & record (plan t7)

- [x] Log run to MLflow: metrics (precision@10, recall@10) + model artifact.
- [x] Tag run: code_version (git sha), data_version (data hash),
      intent = xgboost-binary-v1.
- [x] Register model under the `test` alias (no Staging/Production).
- [x] Append run id + metrics + hyperparams to memory/xgboost/experiments.md.
