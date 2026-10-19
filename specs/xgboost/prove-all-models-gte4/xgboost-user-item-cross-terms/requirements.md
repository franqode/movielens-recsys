# Requirements — xgboost-user-item-cross-terms @ rating >= 4

Notebook-validation spec for the pointwise XGBoost recommender with user-item
cross terms (89 features), retrained at a single fixed threshold `rating >= 4`
as part of plan `prove-all-models-gte4` (task t4). Every R<n> maps to a
metric/test (stated inline after `→`).

This spec differs from the base `xgboost-user-item-cross-terms` spec only in the
label/relevance framing (single fixed `>= 4`, no threshold sweep) and in the
removal of the inline popularity baseline (that comparison is a separate shared
step, plan t10). All 89 features, the chronological split, seed, and model
hyperparameters are unchanged.

## Label framing (fixed `>= 4`, no sweep)

- R1: WHEN the notebook loads the ratings data, THE system SHALL retain ALL
  ratings in `{1, 2, 3, 4, 5}` (nothing dropped) and SHALL form a SINGLE fixed
  binary label `label = 1 if rating >= 4 else 0` (`1,2,3 -> 0`; `4,5 -> 1`).
  There SHALL be NO threshold sweep over `{2, 3, 4, 5}` — exactly one label
  column at the fixed cutoff `4`.
  → test: dropped-rating count == 0; exactly one label column whose values are
    `{0, 1}`, where `rating >= 4` maps to 1 and `rating < 4` maps to 0; no
    per-threshold loop exists in the notebook.

- R2: WHEN computing class balance, THE system SHALL report the `>= 4` label
  distribution (count of `label == 1` vs `label == 0`), the
  positive/negative ratio, and the single `scale_pos_weight` value derived from
  that imbalance.
  → test: label-1 count, label-0 count, ratio, and `scale_pos_weight` reported;
    `scale_pos_weight == n_negative / n_positive` for the `>= 4` split.

## Base features (unchanged)

- R3: WHEN building the base feature matrix, THE system SHALL reproduce the
  prior 47 tabular features: user (age, gender one-hot, occupation one-hot),
  item (genres multi-hot over 18 genres, release_year), and interaction
  (user_mean_rating, item_mean_rating, user_rating_count, item_rating_count).
  → test: base column count == 47 before any cross/affinity columns are added;
    the four interaction columns and 18 genre columns are present.

## Prerequisite feature: user_genre_affinity

- R4: WHEN computing `user_genre_affinity[g]`, THE system SHALL produce 18
  values (one per genre `g`) defined as the shrunk mean-rating deviation
  `affinity[u,g] = (sum over u's train ratings in genre g of (rating -
  global_mean)) / (count_u,g + 5)`, using `global_mean` = overall mean rating
  over training data.
  → test: 18 `user_genre_affinity[g]` columns produced; the formula uses
    shrinkage denominator `count + 5` and deviation-from-global-mean numerator.

- R5: WHILE computing `user_genre_affinity[g]`, THE system SHALL compute it from
  training folds only (leakage guard), and SHALL apply the same train-fold
  affinity to validation/test rows by user key.
  → test: affinity for a validation/test row is derived solely from that user's
    train-fold ratings, never from the row's own (or any val/test) rating.

- R6: WHEN a (user, genre) pair has no train-fold ratings, THE system SHALL
  assign `user_genre_affinity[g] = 0.0` (fallback).
  → test: unseen (user, genre) pairs evaluate to exactly 0.0.

## Cross terms (unchanged)

- R7: WHEN building cross terms, THE system SHALL produce the 24 interaction
  columns: `um_x_im` (user_mean_rating × item_mean_rating), `um_x_ic`
  (user_mean_rating × item_rating_count), `uc_x_im` (user_rating_count ×
  item_mean_rating), `uc_x_ic` (user_rating_count × item_rating_count),
  `age_x_year` (age × release_year), `genre_affinity_score` (dot product
  `sum_g affinity[u,g] × genre_item[g]`), and 18 `aff_x_genre_{g}`
  (`affinity[u,g] × genre_item[g]`, one per genre).
  → test: cross-term column count == 24; each named column present and computed
    as an element-wise product (or the dot product, for `genre_affinity_score`).

- R8: WHEN assembling the final feature matrix, THE system SHALL add the 18
  standalone `user_genre_affinity[g]` columns (not just the cross terms).
  → test: final column count == 89 (47 base + 24 cross + 18 standalone
    affinity).

## No-scaling / scope guard

- R9: WHEN assembling features, THE system SHALL apply NO scaling or
  normalization to any numeric feature, and SHALL NOT create demographic × item
  terms (e.g. age × item_mean_rating, age × item_rating_count, gender × item
  attributes).
  → test: no scaling step present; `age_x_item_mean_rating`,
    `age_x_item_rating_count`, and any gender/occupation × item columns absent.

## Split & evaluation design

- R10: WHEN splitting the data, THE system SHALL perform the same chronological
  (time-ordered) global 80/10/10 train/validation/test split as the prior
  notebook.
  → test: split sizes 80%/10%/10%; max train timestamp ≤ min validation
    timestamp ≤ min test timestamp.

- R11: WHEN ranking for a test user, THE system SHALL define the relevant set
  as the user's held-out items with `rating >= 4`, the candidate pool as the
  full catalog minus the user's train-rated items, and SHALL rank by predicted
  P(positive) descending; users with an empty relevant set SHALL be excluded
  from the mean.
  → test: `|relevant| ≥ 1` for every user included in the mean; candidates
    exclude all train-rated items.

- R12: WHEN scoring the ranking at k=10, THE system SHALL compute
  `precision@10 = |top10 ∩ relevant| / 10` (PRIMARY, optimization target),
  `recall@10 = |top10 ∩ relevant| / |relevant|` and `NDCG@10` (secondary), and
  SHALL report the mean over included test users.
  → metric: `precision@10` (mean, primary), `recall@10` (mean), `NDCG@10`
    (mean).

- R13: WHEN evaluating, THE system SHALL NOT compute an inline popularity
  baseline inside this notebook — the popularity baseline comparison is a
  separate shared step (plan t10) applied uniformly across all four models.
  → test: no popularity-baseline ranking/computation or model-vs-baseline
    deltas present in this notebook.

## Feature importance & model config

- R14: WHEN the model is evaluated, THE system SHALL report feature importance
  (gain and/or weight) for the top contributing features, highlighting whether
  the new cross/affinity terms are among the top contributors.
  → test: feature-importance table/plot rendered, including the cross/affinity
    columns.

- R15: WHEN training, THE system SHALL fit an XGBoost binary classifier with
  `objective: binary:logistic`, fixed seed 42, and `max_depth=6` (unchanged
  hyperparameters from the prior notebook).
  → test: model config shows `objective=binary:logistic`, `random_state=42`,
    `max_depth=6`.

- R16: WHEN training, THE system SHALL log the hyperparameters `max_depth`,
  `n_estimators`, `learning_rate`, and `scale_pos_weight` for the run.
  → test: all four hyperparameters recorded as MLflow params and reproducible;
    `scale_pos_weight` is the single value derived from the `>= 4` imbalance.

## MLflow logging

- R17: WHEN logging the run, THE system SHALL register the trained model under
  the `test` alias in the `xgboost-v1` registry and SHALL NOT promote it to
  `Staging` or `Production`.
  → test: MLflow model in registry `xgboost-v1` has the `test` alias; no
    `Staging`/`Production` alias set.

- R18: WHEN logging the run, THE system SHALL tag it with `code_version` (git
  sha), `data_version` (data hash), and `intent=xgboost-user-item-cross-terms-gte4`.
  → test: all three tags present on the MLflow run, with the `gte4` intent.

- R19: WHEN the run completes, THE system SHALL record the run id, the metrics
  (`precision@10`, `recall@10`, `NDCG@10`), the fixed threshold `>= 4`, and
  hyperparameters in `memory/xgboost/experiments.md`.
  → test: an entry exists in `experiments.md` with run id, metrics, threshold
    `>= 4`, and hyperparameters.
