# Requirements — xgboost-binary-v1

Notebook-validation spec for a binary XGBoost recommendation model. Every R<n>
maps to a metric/test (stated inline after `→`).

## Data framing

- R1: WHEN the notebook loads the ratings data, THE system SHALL retain ALL
  ratings whose value is in `{1, 2, 3, 4, 5}` (nothing dropped) and SHALL map
  `1 -> 0`, `2 -> 0` and `3 -> 1`, `4 -> 1`, `5 -> 1` to form a binary label.
  → test: label set equals `{0, 1}`; count of dropped ratings == 0 (ratings 1–5
    all retained); ratings 1 and 2 map to 0, ratings 3/4/5 map to 1.

- R2: WHEN the notebook computes class balance, THE system SHALL report the
  count and proportion of label 1 (3-star + 4-star + 5-star) versus label 0
  (1-star + 2-star), and the notebook SHALL note that positive (3 + 4 + 5)
  dominates negative (1 + 2).
  → metric: `label_1_count`, `label_0_count`, `label_1_ratio` printed in EDA.

## EDA

- R3: WHEN assembling the notebook, THE system SHALL report the following
  dataset statistics: number of users, number of movies, number of (filtered)
  ratings, and matrix sparsity (observed / (users × movies)).
  → test: `n_users`, `n_movies`, `n_ratings`, `sparsity` values present in EDA.

- R4: WHEN performing EDA, THE system SHALL visualize the rating distribution
  (original ratings) and the filtered binary-label distribution.
  → test: at least one rating-distribution plot and one class-balance plot
    rendered.

## Features

- R5: WHEN building features, THE system SHALL produce only tabular features
  (no embeddings) of three kinds: user (age, gender one-hot, occupation
  one-hot), item (genres multi-hot, release_year), and interaction
  (user_mean_rating, item_mean_rating, user_rating_count, item_rating_count).
  → test: feature matrix columns include all listed features; no embedding
    columns present.

- R6: WHILE computing interaction statistics (means and counts), THE system
  SHALL compute them on training folds only, and SHALL apply the same fold
  statistics to validation/test folds, to prevent target leakage.
  → test: interaction stats for a validation/test row are derived from the
    corresponding train-fold aggregates, not from the row's own rating.

## Split

- R7: WHEN splitting the data, THE system SHALL perform a chronological
  (time-ordered) split into global 80/10/10 train/validation/test sets.
  → test: split sizes are 80%/10%/10%; max train timestamp ≤ min validation
    timestamp ≤ min test timestamp.

## Model

- R8: WHEN training, THE system SHALL fit an XGBoost binary classifier with
  `objective: binary:logistic` and a fixed random seed of 42.
  → test: model config shows `objective=binary:logistic`, `seed=42` (or
    equivalent `random_state=42`).

- R9: WHEN training, THE system SHALL log the hyperparameters `max_depth`,
  `n_estimators`, `learning_rate`, and `scale_pos_weight` for the run.
  → test: all four hyperparameters recorded as MLflow params and reproducible
    from the notebook.

- R10: WHEN evaluating the trained model, THE system SHALL report feature
  importance (gain and/or weight) for the top contributing features.
  → test: feature-importance table/plot rendered in the notebook.

## Evaluation (ranking, k=10)

- R11: WHEN ranking for a test user, THE system SHALL define the relevant set
  as the user's held-out positive (3-, 4-, or 5-star) items, the candidate pool as movies unseen by
  that user in train (optionally capped for speed), and SHALL rank candidates
  by predicted P(positive) descending.
  → test: for each test user, `|relevant| ≥ 1` (users with no held-out positive
    items are excluded from the mean), and candidates exclude all train-rated
    items.

- R12: WHEN scoring the ranking, THE system SHALL compute `precision@10 =
  |top10 ∩ relevant| / 10` and `recall@10 = |top10 ∩ relevant| / |relevant|`
  and SHALL report the mean over test users.
  → metric: `precision@10` (mean), `recall@10` (mean).

- R13: WHEN evaluating, THE system SHALL compute the same `precision@10` and
  `recall@10` for a popularity baseline (top-10 by rating count) on the same
  test users and candidate pool, and SHALL compare model vs baseline.
  → metric: baseline `precision@10` and `recall@10`; comparison reported.

- R14: WHEN the model beats the popularity baseline, THE system SHALL report
  model `precision@10` ≥ baseline `precision@10` and model `recall@10` ≥
  baseline `recall@10` (the hypothesis success condition).
  → metric: model vs baseline `precision@10` and `recall@10` deltas.

## MLflow logging

- R15: WHEN logging the run, THE system SHALL register the trained model under
  the `test` alias and SHALL NOT promote it to `Staging` or `Production`.
  → test: MLflow model has `test` alias; no `Staging`/`Production` alias set.

- R16: WHEN logging the run, THE system SHALL tag it with `code_version`
  (git sha), `data_version` (data hash), and `intent` (the idea id
  `xgboost-binary-v1`).
  → test: all three tags present on the MLflow run.

- R17: WHEN the run completes, THE system SHALL record the run id, metrics
  (`precision@10`, `recall@10`), and hyperparameters in
  `memory/xgboost/experiments.md`.
  → test: an entry exists in `experiments.md` with run id and metrics.
