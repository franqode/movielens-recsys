# Requirements — als-v1

Notebook-validation spec for an implicit-feedback ALS recommender. The notebook
proves that ALS with confidence weighting beats the current MLflow `test`-alias
model (`xgboost-v1` v8) on NDCG@10 (primary) and precision@10 / recall@10 /
hit-rate@10. Every R<n> maps to a metric/test (stated inline after `→`).

## Input data

- R1: WHEN the notebook loads the data, THE system SHALL use ratings only
  (`userId`, `movieId`, `rating`, `timestamp`) and SHALL NOT construct or ingest
  any user/item tabular features (no age, gender, occupation, genres,
  release_year).
  → test: feature/build code consumes only the ratings table; no tabular
    feature columns are produced.

- R2: WHEN building the implicit user-item matrix, THE system SHALL set the
  confidence weight of every observed `(userId, movieId)` pair to
  `1 + 40 * rating` and SHALL set every unobserved pair to `0`.
  → test: matrix value at an observed cell equals `1 + 40 * rating`; unobserved
    cells are `0`; a 4-star cell is `161`, a 5-star cell is `201`.

- R3: WHEN binarizing for relevance, THE system SHALL treat a rating as
  positive (relevant) iff `rating >= 4`, and non-positive otherwise.
  → test: the relevance mask equals `rating >= 4`; a 3-star is non-relevant, a
    4-star is relevant.

## EDA

- R4: WHEN performing EDA, THE system SHALL report `n_users`, `n_movies`,
  `n_ratings`, and matrix sparsity = observed / (users × movies), and SHALL note
  the positive (rating >= 4) vs unobserved/non-positive imbalance.
  → metric: `n_users`, `n_movies`, `n_ratings`, `sparsity`; count + ratio of
    positive cells vs the rest of the matrix.

- R5: WHEN performing EDA, THE system SHALL visualize the rating distribution
  (raw ratings) and the implicit signal (positive >=4 vs non-positive /
  unobserved).
  → test: at least one rating-distribution plot and one implicit-signal /
    imbalance plot rendered.

## Model

- R6: WHEN training, THE system SHALL fit
  `implicit.als.AlternatingLeastSquares` with `factors=64`, `alpha=40`,
  `regularization=0.1`, `iterations=15`, and a fixed `random_state` (seed) for
  reproducibility.
  → test: model object config shows `factors=64`, `alpha=40`,
    `regularization=0.1`, `iterations=15`, `random_state` set.

- R7: WHEN training, THE system SHALL log all hyperparameters (factors, alpha,
  regularization, iterations, random_state) as MLflow params so the run is
  reproducible.
  → test: all five hyperparameters present as MLflow params.

## Split

- R8: WHEN splitting, THE system SHALL sort interactions chronologically by
  timestamp and SHALL produce global 80/10/10 train/validation/test sets.
  → test: split sizes are 80%/10%/10%; max train timestamp ≤ min validation
    timestamp ≤ min test timestamp.

- R9: WHEN splitting, THE system SHALL use train (earliest 80%) to build the
  implicit matrix the model is fit on, and SHALL use validation/test (last 20%)
  only for held-out evaluation.
  → test: model is fit on train-only ratings; held-out test items are never in
    the train matrix.

## Evaluation protocol (ranking, k=10)

- R10: WHEN evaluating a test user, THE system SHALL define the relevant set as
  the user's held-out test items with `rating >= 4`.
  → test: relevant set for each test user is exactly their test ratings with
    value >= 4.

- R11: WHEN evaluating a test user, THE system SHALL define the candidate pool
  as all items the user did NOT rate in train, SHALL score them with the fitted
  ALS model, SHALL rank descending by score, and SHALL take the top 10.
  → test: candidates exclude all train-rated items; top-10 produced per user.

- R12: WHEN aggregating metrics, THE system SHALL exclude test users whose
  relevant set is empty, applied identically to the model and all baselines.
  → test: the set of evaluated test users is identical for model and every
    baseline; every evaluated user has `|relevant| >= 1`.

- R13: WHEN scoring, THE system SHALL compute `NDCG@10` as the primary metric,
  and SHALL also compute `precision@10`, `recall@10`, and `hit-rate@10`, each
  reported as the mean over evaluated test users.
  → metric: `NDCG@10` (primary), `precision@10`, `recall@10`, `hit-rate@10`
    (all mean over test users).

## Baseline comparison

- R14: WHEN comparing against the existing test-alias model, THE system SHALL
  report the `xgboost-v1` v8 baseline numbers matched to the rating >= 4
  relevance threshold: `NDCG@10=0.057167`, `precision@10=0.055219`,
  `recall@10=0.015145` (T=4), and SHALL state the ALS result alongside them.
  → metric: ALS `NDCG@10` / `precision@10` / `recall@10` vs the T=4 baseline
    values above.

- R15: WHEN the model beats the baseline, THE system SHALL report ALS
  `NDCG@10` >= baseline `NDCG@10` (the primary hypothesis success condition),
  plus the precision@10 / recall@10 deltas.
  → metric: ALS vs baseline `NDCG@10` delta (primary), and precision@10 /
    recall@10 deltas.

- R16: WHEN evaluating, THE system SHALL compute an inline popularity baseline
  (top-10 items by train rating count) on the same evaluated test users and
  candidate pool, and SHALL report its `NDCG@10` / `precision@10` / `recall@10` /
  `hit-rate@10` as a floor.
  → metric: popularity baseline metrics computed inline (not registered).

- R17: WHEN reporting `hit-rate@10`, THE system SHALL compare ALS against the
  recomputed inline popularity baseline only, because `xgboost-v1` never logged
  `hit-rate@10`.
  → metric: ALS `hit-rate@10` vs inline popularity `hit-rate@10`.

## MLflow logging

- R18: WHEN logging the run, THE system SHALL register the model under the
  MLflow `test` alias with registry name `als-v1`, and SHALL NOT promote it to
  `Staging` or `Production`.
  → test: model `als-v1` has `test` alias; no `Staging`/`Production` alias set.

- R19: WHEN logging the run, THE system SHALL tag it with `code_version` (git
  sha), `data_version` (data hash), and `intent`
  (`als-implicit-beats-test-baseline`).
  → test: all three tags present on the MLflow run.

- R20: WHEN the run completes, THE system SHALL record the run id, metrics
  (`NDCG@10`, `precision@10`, `recall@10`, `hit-rate@10`), and hyperparameters
  in `memory/als/experiments.md`.
  → test: an entry exists in `experiments.md` with run id, metrics, and
    hyperparameters.
