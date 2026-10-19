# Requirements — als-v1 retrain at threshold >= 2

Notebook-validation spec for retraining the implicit-feedback ALS recommender
(`als-v1`) with the positive/relevance cutoff moved from `rating >= 4` to
`rating >= 2`. There is NO baseline comparison: the single evaluation is the ALS
model's own metrics at threshold >= 2. Every R<n> maps to a metric/test (stated
inline after `→`).

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
    cells are `0`; a 2-star cell is `81`, a 4-star cell is `161`, a 5-star cell
    is `201`.

- R3: WHEN binarizing for relevance, THE system SHALL treat a rating as
  positive (relevant) iff `rating >= 2`, and non-positive otherwise.
  → test: the relevance mask equals `rating >= 2`; a 1-star is non-relevant, a
    2-star is relevant.

## EDA

- R4: WHEN performing EDA, THE system SHALL report `n_users`, `n_movies`,
  `n_ratings`, and matrix sparsity = observed / (users × movies), and SHALL note
  the positive (rating >= 2) vs unobserved/non-positive imbalance.
  → metric: `n_users`, `n_movies`, `n_ratings`, `sparsity`; count + ratio of
    positive cells vs the rest of the matrix.

- R5: WHEN performing EDA, THE system SHALL visualize the rating distribution
  (raw ratings) and the implicit signal (positive >=2 vs non-positive /
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
  the user's held-out test items with `rating >= 2`.
  → test: relevant set for each test user is exactly their test ratings with
    value >= 2.

- R11: WHEN evaluating a test user, THE system SHALL define the candidate pool
  as all items the user did NOT rate in train, SHALL score them with the fitted
  ALS model, SHALL rank descending by score, and SHALL take the top 10.
  → test: candidates exclude all train-rated items; top-10 produced per user.

- R12: WHEN aggregating metrics, THE system SHALL exclude test users whose
  relevant set is empty, applied identically across the single evaluation.
  → test: every evaluated test user has `|relevant| >= 1`.

- R13: WHEN scoring, THE system SHALL compute `NDCG@10` as the primary metric,
  and SHALL also compute `precision@10`, `recall@10`, and `hit-rate@10`, each
  reported as the mean over evaluated test users.
  → metric: `NDCG@10` (primary), `precision@10`, `recall@10`, `hit-rate@10`
    (all mean over test users).

## MLflow logging

- R14: WHEN logging the run, THE system SHALL register the model under the
  MLflow `test` alias with registry name `als-v1`, and SHALL NOT promote it to
  `Staging` or `Production`.
  → test: model `als-v1` has `test` alias; no `Staging`/`Production` alias set.

- R15: WHEN logging the run, THE system SHALL tag it with `code_version` (git
  sha), `data_version` (data hash), and `intent` (`als-v1-gte2`).
  → test: all three tags present on the MLflow run.

- R16: WHEN the run completes, THE system SHALL record the run id, metrics
  (`NDCG@10`, `precision@10`, `recall@10`, `hit-rate@10`), and hyperparameters
  in `memory/als/experiments.md`.
  → test: an entry exists in `experiments.md` with run id, metrics, and
    hyperparameters.
