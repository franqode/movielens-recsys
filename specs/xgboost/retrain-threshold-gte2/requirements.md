# Requirements — xgboost-binary-v1 @ `rating >= 2` (retrain-threshold-gte2)

Notebook-validation spec for retraining the binary XGBoost recommendation model
with the positive-label cutoff moved from `>= 3` to `>= 2`. Every R<n> maps to a
metric/test (stated inline after `→`). The ONLY change from the prior
`xgboost-binary-v1` spec is the label binarization threshold and the removal of
the popularity baseline; all other design decisions are unchanged.

## Data framing

- R1: WHEN the notebook loads the ratings data, THE system SHALL retain ALL
  ratings whose value is in `{1, 2, 3, 4, 5}` (nothing dropped) and SHALL map
  `1 -> 0` and `2 -> 1`, `3 -> 1`, `4 -> 1`, `5 -> 1` to form a binary label
  (i.e. `rating >= 2 -> 1`, `rating < 2 -> 0`).
  → test: label set equals `{0, 1}`; count of dropped ratings == 0 (ratings 1–5
    all retained); rating 1 maps to 0, ratings 2/3/4/5 map to 1.

- R2: WHEN the notebook computes class balance, THE system SHALL report the
  count and proportion of label 1 (2-star + 3-star + 4-star + 5-star) versus
  label 0 (1-star), and the notebook SHALL note that positive dominates
  negative, with the positive ratio expected near ~0.94.
  → metric: `label_1_count`, `label_0_count`, `label_1_ratio` printed in EDA;
    `label_1_ratio` ≈ 0.94.

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

- R5: WHEN building features, THE system SHALL produce the same 47 tabular
  features (no embeddings) as the prior `xgboost-binary-v1` spec, of three
  kinds: user (age, gender one-hot, occupation one-hot), item (genres multi-hot,
  release_year), and interaction (user_mean_rating, item_mean_rating,
  user_rating_count, item_rating_count).
  → test: feature matrix has 47 columns including all listed features; no
    embedding columns present.

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
  `objective: binary:logistic`, `max_depth=6`, and a fixed random seed of 42.
  → test: model config shows `objective=binary:logistic`, `max_depth=6`,
    `seed=42` (or equivalent `random_state=42`).

- R9: WHEN training, THE system SHALL log the hyperparameters `max_depth`,
  `n_estimators`, `learning_rate`, and `scale_pos_weight` for the run.
  → test: all four hyperparameters recorded as MLflow params and reproducible
    from the notebook.

- R10: WHEN evaluating the trained model, THE system SHALL report feature
  importance (gain and/or weight) for the top contributing features.
  → test: feature-importance table/plot rendered in the notebook.

## Evaluation (ranking, k=10)

- R11: WHEN ranking for a test user, THE system SHALL define the relevant set
  as the user's held-out positive (rating >= 2) items, the candidate pool as the
  full catalog minus items rated by that user in train (optionally capped for
  speed), and SHALL rank candidates by predicted P(positive) descending.
  → test: for each test user, `|relevant| ≥ 1` (users with no held-out positive
    items are excluded from the mean), and candidates exclude all train-rated
    items.

- R12: WHEN scoring the ranking, THE system SHALL compute `precision@10 =
  |top10 ∩ relevant| / 10`, `recall@10 = |top10 ∩ relevant| / |relevant|`, and
  `NDCG@10`, and SHALL report the mean over test users.
  → metric: `precision@10` (mean, primary), `recall@10` (mean), `NDCG@10`
    (mean).

## MLflow logging

- R13: WHEN logging the run, THE system SHALL register the trained model under
  the `test` alias in registry `xgboost-v1` and SHALL NOT promote it to
  `Staging` or `Production`.
  → test: MLflow model registered as `xgboost-v1` with `test` alias; no
    `Staging`/`Production` alias set.

- R14: WHEN logging the run, THE system SHALL tag it with `code_version`
  (git sha), `data_version` (data hash), and `intent`
  (`xgboost-binary-v1-gte2`).
  → test: all three tags present on the MLflow run.

- R15: WHEN the run completes, THE system SHALL record the run id, metrics
  (`precision@10`, `recall@10`, `NDCG@10`), and hyperparameters in
  `memory/xgboost/experiments.md`.
  → test: an entry exists in `experiments.md` with run id and metrics.
