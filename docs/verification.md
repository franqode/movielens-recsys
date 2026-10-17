# Verification

How to prove a task/feature is done correctly.

## init.sh

Run `./init.sh` — must exit green. It validates:

- `feature_list.json` exists and is well-formed.
- all statuses are valid and each feature has an `sdd` flag.
- at most one feature is `in_progress`.

## Traceability (R<n> → metric)

For every requirement R<n> in `specs/<model>/<plan-id>/requirements.md`, there
must be a metric/test that proves it. The `mle-engineer` records the mapping in
`progress/<model>/<plan-id>/impl_<plan-id>.md`; the `reviewer` checks it.

Example:

```
R1: "WHEN ranking N items, the system SHALL reach NDCG@10 >= 0.30."
    → metric: ndcg@10, recorded in memory/<model>/experiments.md
```

## MLflow

- Every run is logged with metrics + the model artifact.
- Tags present: `code_version` (git sha), `data_version`, `intent`.
- The model is registered under `"<model>/v<N>"` at `Staging`.
- `Production` is set only after the reviewer's sign-off.

## Serving

- `app/` loads via `mlflow.pyfunc.load_model("models:/<model>/v<N>/Staging")`.
- No model binaries copied into `app/`.
- The app serves all models at their latest `v<N>`.

## Done checklist (reviewer)

- every task `[x]`;
- every R<n> mapped to a metric/test;
- run logged in MLflow + recorded in `memory/<model>/experiments.md`;
- serving correct;
- `progress/<model>/<plan-id>/review_<plan-id>.md` written.
