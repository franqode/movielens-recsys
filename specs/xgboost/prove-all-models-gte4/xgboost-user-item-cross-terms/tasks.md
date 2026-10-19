# Tasks — xgboost-user-item-cross-terms @ rating >= 4

Discrete checklist for assembling the validation notebook (plan task t4). Mark
each `[x]` as it is completed.

## Load & frame

- [x] Load ratings (+ users/movies) into the notebook (self-contained, no `src/`).
- [x] Keep all ratings 1–5; build a SINGLE fixed binary label
      `label = 1 if rating >= 4 else 0` (`1,2,3 -> 0`; `4,5 -> 1`). No threshold
      sweep.
- [x] Report `>= 4` class balance: label-1 count, label-0 count, ratio, and the
      derived `scale_pos_weight = n_negative / n_positive`.

## Features

- [x] Reproduce the 47 base features (user age/gender/occupation; item
      genres/release_year; interaction user_mean_rating, item_mean_rating,
      user_rating_count, item_rating_count) with train-fold-only interaction
      stats (leakage guard).
- [x] Compute `global_mean` over training ratings.
- [x] Compute `user_genre_affinity[g]` (18 values) via shrunk mean-rating
      deviation `(sum(rating - global_mean)) / (count + 5)`, train-fold only,
      fallback 0.0 for unseen (user, genre).
- [x] Build 24 cross terms: `um_x_im`, `um_x_ic`, `uc_x_im`, `uc_x_ic`,
      `age_x_year`, `genre_affinity_score` (dot product), 18 `aff_x_genre_{g}`.
- [x] Add the 18 standalone `user_genre_affinity[g]` columns.
- [x] Confirm final feature count == 89 (47 + 24 + 18); no scaling; no
      demographic × item terms.

## Split & evaluation setup

- [x] Chronological 80/10/10 split (train/validation/test) by timestamp.
- [x] Define relevant set = held-out items with `rating >= 4` per test user.
- [x] Define candidate pool = full catalog minus train-rated items per test user;
      exclude empty-relevant users from the mean.

## Train

- [x] Train XGBoost with `objective: binary:logistic`, seed 42, `max_depth=6`
      (single fixed-threshold run).
- [x] Log hyperparameters: max_depth, n_estimators, learning_rate,
      scale_pos_weight (single value from the `>= 4` imbalance).
- [x] Report feature importance (gain and/or weight); highlight cross/affinity
      columns.

## Evaluate

- [x] Compute per-user precision@10 (primary), recall@10, NDCG@10; report mean
      over included test users.
- [x] Confirm NO popularity-baseline computation or model-vs-baseline deltas are
      produced in this notebook (baseline is a separate shared step, plan t10).

## Log & record

- [x] Log run to MLflow: metrics (precision@10, recall@10, NDCG@10),
      hyperparameters, + model artifact.
- [x] Tag run: code_version (git sha), data_version (data hash),
      intent = xgboost-user-item-cross-terms-gte4.
- [x] Register model under the `test` alias in registry `xgboost-v1` (no
      Staging/Production).
- [x] Append run id + metrics + fixed threshold `>= 4` + hyperparams to
      memory/xgboost/experiments.md.
