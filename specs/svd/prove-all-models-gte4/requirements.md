# Requirements — svd (prove-all-models-gte4, task t8)

Notebook-validation spec for a surprise SVD recommender, reframed from RMSE
(`memory/svd/ideas.md` `svd-vs-mean`) to ranking at the `rating >= 4` relevance
threshold. The notebook proves SVD produces a `precision@10` (primary) and
`NDCG@10` / `recall@10` / `hit-rate@10` (secondary) ranking result on a
chronological 80/10/10 split. The popularity-baseline comparison is intentionally
**out of scope** for this notebook (it is a shared step, plan task t10). Every
R<n> maps to a metric/test (stated inline after `→`).

## Input data

- R1: WHEN the notebook loads the data, THE system SHALL use ratings only
  (`userId`, `movieId`, `rating`, `timestamp`) and SHALL NOT construct or ingest
  any user/item tabular features (no age, gender, occupation, genres,
  release_year).
  → test: feature/build code consumes only the ratings table; no tabular
    feature columns are produced.

## Model

- R2: WHEN training, THE system SHALL fit `surprise.SVD` with the default
  hyperparameters `n_factors=100`, `n_epochs=20`, `biased=True`,
  `lr_all=0.005`, `reg_all=0.02`, plus a fixed `random_state` (seed) for
  reproducibility.
  → test: model config shows `n_factors=100`, `n_epochs=20`, `biased=True`,
    `lr_all=0.005`, `reg_all=0.02`, and a set `random_state`.

- R3: WHEN training, THE system SHALL log all hyperparameters (`n_factors`,
  `n_epochs`, `biased`, `lr_all`, `reg_all`, `random_state`) as MLflow params so
  the run is reproducible.
  → test: all six hyperparameters present as MLflow params.

## Split

- R4: WHEN splitting, THE system SHALL sort interactions chronologically by
  timestamp and SHALL produce global 80/10/10 train/validation/test sets under a
  fixed seed.
  → test: split sizes are 80%/10%/10%; max train timestamp ≤ min validation
    timestamp ≤ min test timestamp; identical split on re-run with the same seed.

- R5: WHEN training, THE system SHALL fit SVD on train (earliest 80%) ratings
  only, and SHALL use validation/test (last 20%) only for held-out evaluation.
  → test: model is fit on train-only ratings; held-out test items are never in
    the train ratings.

## Evaluation protocol (ranking, k=10)

- R6: WHEN evaluating a test user, THE system SHALL define the relevant set as
  the user's held-out test items with `rating >= 4`.
  → test: relevant set for each test user is exactly their test ratings with
    value >= 4.

- R7: WHEN evaluating a test user, THE system SHALL define the candidate pool as
  all items the user did NOT rate in train, SHALL score each candidate by its
  SVD predicted rating, SHALL rank candidates descending by score, and SHALL
  take the top 10.
  → test: candidates exclude all train-rated items; top-10 produced per user by
    descending predicted rating.

- R8: WHEN aggregating metrics, THE system SHALL exclude test users whose
  relevant set is empty.
  → test: every evaluated test user has `|relevant| >= 1`; the evaluated-user
    set is identical across all reported metrics.

- R9: WHEN scoring, THE system SHALL compute `precision@10` as the primary
  metric (optimization target), and SHALL also compute `NDCG@10`, `recall@10`,
  and `hit-rate@10`, each reported as the mean over evaluated test users.
  → metric: `precision@10` (primary), `NDCG@10`, `recall@10`, `hit-rate@10`
    (all mean over test users).

## MLflow logging

- R10: WHEN logging the run, THE system SHALL register the model under the
  MLflow `test` alias with registry name `svd-v1`, and SHALL NOT promote it to
  `Staging` or `Production`.
  → test: model `svd-v1` has `test` alias; no `Staging`/`Production` alias set.

- R11: WHEN logging the run, THE system SHALL tag it with `code_version` (git
  sha), `data_version` (data hash), and `intent` (`svd-v1-gte4`).
  → test: all three tags present on the MLflow run.

- R12: WHEN the run completes, THE system SHALL record the run id, metrics
  (`precision@10`, `NDCG@10`, `recall@10`, `hit-rate@10`), and hyperparameters
  in `memory/svd/experiments.md`.
  → test: an entry exists in `experiments.md` with run id, metrics, and
    hyperparameters.
