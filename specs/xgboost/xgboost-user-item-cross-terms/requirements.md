# Requirements — xgboost-user-item-cross-terms

Notebook-validation spec that extends the pointwise XGBoost recommender with
user-item cross terms (multiplicative interaction features). Every R<n> maps to
a metric/test (stated inline after `→`).

## Base (unchanged) framing & features

- R1: WHEN the notebook loads the ratings data, THE system SHALL retain ALL
  ratings in `{1, 2, 3, 4, 5}` (nothing dropped) and, for a candidate threshold
  `T ∈ {2, 3, 4, 5}`, SHALL form a binary label `label = 1 if rating >= T else
  0` (so T=2 → `{1→0, 2,3,4,5→1}`; T=3 → `{1,2→0, 3,4,5→1}`; T=4 → `{1,2,3→0,
  4,5→1}`; T=5 → `{1,2,3,4→0, 5→1}`). The threshold T is a variable analyzed
  over `{2, 3, 4, 5}`, not a single fixed cut.
  → test: dropped-rating count == 0 for every T; for each T the label set equals
    `{0, 1}` and `rating >= T` maps to 1, `rating < T` maps to 0.

- R-threshold: WHEN the notebook evaluates the cross-terms model, THE system
  SHALL train + evaluate at EACH threshold `T ∈ {2, 3, 4, 5}`, SHALL report
  `precision@10` / `recall@10` / `NDCG@10` for each T, and SHALL identify the
  best threshold by the primary metric `precision@10` (ties broken by higher
  `NDCG@10`).
  → metric: per-threshold table of `precision@10`/`recall@10`/`NDCG@10`; a
    single "best threshold" value reported.

- R2: WHEN building the base feature matrix, THE system SHALL reproduce the
  prior 47 tabular features: user (age, gender one-hot, occupation one-hot),
  item (genres multi-hot over 18 genres, release_year), and interaction
  (user_mean_rating, item_mean_rating, user_rating_count, item_rating_count).
  → test: base column count == 47 before any cross/affinity columns are added;
    the four interaction columns and 18 genre columns are present.

## New prerequisite feature: user_genre_affinity

- R3: WHEN computing `user_genre_affinity[g]`, THE system SHALL produce 18
  values (one per genre `g`) defined as the shrunk mean-rating deviation
  `affinity[u,g] = (sum over u's train ratings in genre g of (rating -
  global_mean)) / (count_u,g + 5)`, using `global_mean` = overall mean rating
  over training data.
  → test: 18 `user_genre_affinity[g]` columns produced; the formula uses
    shrinkage denominator `count + 5` and deviation-from-global-mean numerator.

- R4: WHILE computing `user_genre_affinity[g]`, THE system SHALL compute it from
  training folds only (leakage guard), and SHALL apply the same train-fold
  affinity to validation/test rows by user key.
  → test: affinity for a validation/test row is derived solely from that user's
    train-fold ratings, never from the row's own (or any val/test) rating.

- R5: WHEN a (user, genre) pair has no train-fold ratings, THE system SHALL
  assign `user_genre_affinity[g] = 0.0` (fallback).
  → test: unseen (user, genre) pairs evaluate to exactly 0.0.

## New cross terms

- R6: WHEN building cross terms, THE system SHALL produce the 24 interaction
  columns: `um_x_im` (user_mean_rating × item_mean_rating), `um_x_ic`
  (user_mean_rating × item_rating_count), `uc_x_im` (user_rating_count ×
  item_mean_rating), `uc_x_ic` (user_rating_count × item_rating_count),
  `age_x_year` (age × release_year), `genre_affinity_score` (dot product
  `sum_g affinity[u,g] × genre_item[g]`), and 18 `aff_x_genre_{g}`
  (`affinity[u,g] × genre_item[g]`, one per genre).
  → test: cross-term column count == 24; each named column present and computed
    as an element-wise product (or the dot product, for `genre_affinity_score`).

- R7: WHEN assembling the final feature matrix, THE system SHALL add the 18
  standalone `user_genre_affinity[g]` columns (not just the cross terms).
  → test: final column count == 89 (47 base + 24 cross + 18 standalone
    affinity).

## No-scaling / scope guard

- R8: WHEN assembling features, THE system SHALL apply NO scaling or
  normalization to any numeric feature, and SHALL NOT create demographic × item
  terms (e.g. age × item_mean_rating, age × item_rating_count, gender × item
  attributes).
  → test: no scaling step present; `age_x_item_mean_rating`,
    `age_x_item_rating_count`, and any gender/occupation × item columns absent.

## Split & evaluation design

- R9: WHEN splitting the data, THE system SHALL perform the same chronological
  (time-ordered) global 80/10/10 train/validation/test split as the prior
  notebook.
  → test: split sizes 80%/10%/10%; max train timestamp ≤ min validation
    timestamp ≤ min test timestamp.

- R10: WHEN ranking for a test user at threshold T, THE system SHALL define the
  relevant set as the user's held-out items with `rating >= T` (positive under
  T), the candidate pool as the full catalog minus the user's train-rated
  items, and SHALL rank by predicted P(positive) descending; users with an
  empty relevant set SHALL be excluded from the mean (per T).
  → test: `|relevant| ≥ 1` for every user included in the mean; candidates
    exclude all train-rated items.

- R11: WHEN scoring the ranking at k=10 for each threshold T, THE system SHALL
  compute `precision@10 = |top10 ∩ relevant| / 10` (primary), `recall@10 =
  |top10 ∩ relevant| / |relevant|` and `NDCG@10` (secondary), and SHALL report
  the mean over included test users for each T.
  → metric: per-threshold `precision@10` (mean, primary), `recall@10` (mean),
    `NDCG@10` (mean).

- R12: WHEN evaluating at each threshold T, THE system SHALL compute the
  popularity baseline (top-10 by rating count) on the same test users,
  candidate pool, and relevant sets, and SHALL compare model vs baseline on all
  three metrics per T.
  → metric: per-threshold baseline `precision@10`, `recall@10`, `NDCG@10`;
    model-vs-baseline deltas reported for each T.

- R13: WHEN comparing against the prior run, THE system SHALL report the model's
  per-threshold metrics alongside the prior `test`-alias run
  `fdab1c40799f460db34a2ec60e8c9774` (v7) `precision@10`/`recall@10`/`NDCG@10`,
  using the same split, seed, and metrics, with the comparison stated at the
  best threshold (and, if informative, across all four thresholds).
  → test: prior run id referenced and its three ranking metrics quoted for
    comparison.

- R14: WHEN the model is evaluated (at the best threshold), THE system SHALL
  report feature importance (gain and/or weight) for the top contributing
  features, highlighting whether the new cross/affinity terms are among the top
  contributors.
  → test: feature-importance table/plot rendered, including the cross/affinity
    columns.

## Model & reproducibility

- R15: WHEN training, THE system SHALL fit an XGBoost binary classifier with
  `objective: binary:logistic`, fixed seed 42, and `max_depth=6` (unchanged
  hyperparameters from the prior notebook).
  → test: model config shows `objective=binary:logistic`, `random_state=42`,
    `max_depth=6`.

- R16: WHEN training at each threshold T, THE system SHALL log the
  hyperparameters `max_depth`, `n_estimators`, `learning_rate`, and
  `scale_pos_weight` for the run.
  → test: all four hyperparameters recorded as MLflow params and reproducible;
    `scale_pos_weight` set per threshold T (imbalance varies with T).

## MLflow logging

- R17: WHEN logging the run, THE system SHALL register the trained model (at the
  best threshold) under the `test` alias and SHALL NOT promote it to `Staging`
  or `Production`.
  → test: MLflow model has `test` alias; no `Staging`/`Production` alias set.

- R18: WHEN logging the run, THE system SHALL tag it with `code_version` (git
  sha), `data_version` (data hash), and `intent=xgboost-user-item-cross-terms`.
  → test: all three tags present on the MLflow run.

- R19: WHEN the run completes, THE system SHALL record the run id, the
  per-threshold metrics (`precision@10`, `recall@10`, `NDCG@10`), the identified
  best threshold, and hyperparameters in `memory/xgboost/experiments.md`.
  → test: an entry exists in `experiments.md` with run id, per-threshold
    metrics, best threshold, and hyperparameters.
