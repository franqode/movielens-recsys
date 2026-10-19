# Conventions

## Metrics vocabulary (fixed)

- Rating prediction: `RMSE`, `MAE`.
- Ranking: `precision@k`, `recall@k`, `NDCG@k`, `hit-rate` (default k=10).

Do not invent new metric names without updating this file and AGENTS.md.

## Naming

- Model registry names: `"<model>/v<N>"` (e.g. `svd/v2`), mapping 1:1 to
  `src/movielens/models/<model>/v<N>/`.
- Models: `popularity`, `svd`, `als`, `knn_item`, `ncf`.
- Experiments (MLflow): one stable experiment per model family.
- Plan ids: kebab-case (`ncf-v1`, `svd-tune-k`).

## Shared entrypoints

Every `src/movielens/models/<model>/v<N>/recommend.py` exposes the same signature
so the app is model-agnostic. The exact signature is defined in
`src/movielens/recommend.py`.

## Git

- Model code, specs, memory, and progress are git-versioned.
- `data/` and `mlflow/` are gitignored.
- Tag releases per model version (`git tag svd-v2`).

## Style

- No code comments unless asked.
- Match the existing style in each file.
- Validation phase: notebooks are self-contained (all logic inline, full
  data-science detail). Repo implementation phase: notebooks stay thin, real
  logic lives in `src/`.
- Reproducible: fixed seeds, logged hyperparameters, deterministic splits.

## MLflow tags

Every run is tagged with `code_version` (git sha), `data_version` (data hash),
and `intent` (the idea being tested).

## MLflow aliases

- Validation/prototype models are registered under the `test` alias.
- A model is promoted to `Staging` (and later `Production`) only after the
  notebook-validation human gate passes.
