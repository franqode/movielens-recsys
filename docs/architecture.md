# Architecture

The harness is a Spec-Driven Development (SDD) pipeline for a MovieLens
recommender-systems lab. One primary agent (`lead`) orchestrates six subagents.

## Agents

| Agent | Mode | SDD role | Owns |
|---|---|---|---|
| `lead` | primary | leader | `feature_list.json`, `memory/<model>/plans/`, `progress/` |
| `data-scientist` | subagent | ideator | `memory/<model>/ideas.md`, EDA notebooks |
| `spec_author` | subagent | spec author | `specs/<model>/<plan-id>/` |
| `data-engineer` | subagent | implement (features) | `src/movielens/features.py`, `data/processed/` |
| `mle-engineer` | subagent | implementer | `src/movielens/models/<model>/v<N>/`, `memory/<model>/experiments.md` |
| `reviewer` | subagent | reviewer (read-only) | `progress/<model>/<plan-id>/review_*.md` |
| `mlops-engineer` | subagent | implement (serving) | `src/movielens/mlflow_utils.py`, `app/` |

## Separation rules

- `lead` never edits code.
- `data-scientist` proposes/specs but does not train.
- `mle-engineer` trains but does not self-approve.
- `reviewer` verifies but never edits code (`edit: deny`).
- `mlops-engineer` serves only after the reviewer's sign-off.

## Directory map

| Concern | Location |
|---|---|
| Global tracker | `feature_list.json` |
| Ideas (per model) | `memory/<model>/ideas.md` |
| Plans (per model) | `memory/<model>/plans/<plan-id>.md` |
| Experiments (per model) | `memory/<model>/experiments.md` |
| SDD specs | `specs/<model>/<plan-id>/` |
| Progress | `progress/<model>/<plan-id>/` |
| Model code | `src/movielens/models/<model>/v<N>/` |
| Weights | `mlflow/` (gitignored) |
| Serving | `app/` |

## feature_list.json entry shape

```json
{
  "id": "ncf-v1",
  "model": "ncf",
  "intent": "train NCF baseline",
  "sdd": true,
  "status": "pending",
  "data_version": null,
  "run_id": null,
  "plan": "memory/ncf/plans/ncf-v1.md"
}
```

Statuses: `pending` → `spec_ready` (sdd=true only) → `in_progress` → `done`.

## Versioning

| Thing | Versioned by |
|---|---|
| Model code | git (`v<N>` dirs + commits/tags) |
| Weights | MLflow `run_id` |
| Data | `data_version` hash |
| Experiment record | `run_id` + `code_version` + `data_version` |
