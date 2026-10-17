# MovieLens Recommender Systems Lab — Harness

You are working inside a Spec-Driven Development (SDD) harness for a MovieLens
recommender-systems lab. This file is the *map*; the rules live in the files it
points to. Read on demand, don't load everything at once.

## What this project is

A reproducible recommender-systems lab on MovieLens (ml-latest-small): EDA,
trained models tracked with MLflow, and a prototype app that serves
recommendations from all models at their latest version.

## How work flows (SDD)

Ideas become plans, plans become tasks, tasks may need a spec, then code, then
review. Full process: `docs/specs.md`. Completion criteria per phase:
`CHECKPOINTS.md`.

```
data-scientist (ideate) → lead (accept/reject, plan+task) →
  sdd=true → spec_author (EARS) → HUMAN GATE →
  sdd=false ─────────────────────────────→ in_progress:
  data-engineer → mle-engineer → HUMAN GATE → mlops-engineer → reviewer → done
```

## Agents

Defined in `.opencode/agents/`. One primary: `lead`. Subagents:
`data-scientist`, `spec_author`, `data-engineer`, `mle-engineer`, `reviewer`,
`mlops-engineer`. See `docs/architecture.md` for the role/ownership matrix.

## Where things live

| Concern | Location |
|---|---|
| Global task tracker | `feature_list.json` |
| Ideas (per model) | `memory/<model>/ideas.md` |
| Plans/tasks (per model) | `memory/<model>/plans/<plan-id>.md` |
| Experiment runs (per model) | `memory/<model>/experiments.md` |
| SDD specs | `specs/<model>/<plan-id>/` |
| Progress trace | `progress/<model>/<plan-id>/` |
| Model code (git-versioned) | `src/movielens/models/<model>/v<N>/` |
| Shared code | `src/movielens/` |
| Model weights | `mlflow/` (gitignored) |
| Serving app | `app/` |

## Hard rules (non-negotiable)

- MLflow is the single source of truth for experiments. Every run logs metrics
  + the model artifact, tagged with `code_version` (git sha), `data_version`,
  and `intent`.
- The app loads models via `mlflow.pyfunc.load_model("models:/<model>/v<N>/<stage>")`.
  Never copy model binaries into the app.
- Every model exposes one predict/recommend entrypoint with a shared signature.
- Metrics vocabulary is fixed (see `docs/conventions.md`): RMSE/MAE (rating),
  precision@k, recall@k, NDCG@k, hit-rate (ranking).
- No code comments unless asked. Match existing style.
- One `in_progress` task at a time (enforced by `init.sh`).
- Reviewers and leaders never edit code; implementers never self-approve.

## Stack

pandas, scikit-surprise (SVD/KNN), implicit (ALS), PyTorch (NCF), mlflow,
fastapi + uvicorn.
