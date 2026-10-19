# MovieLens Recommender Systems Lab — Harness

You are working inside a Spec-Driven Development (SDD) harness for a MovieLens
recommender-systems lab. This file is the *map*; the rules live in the files it
points to. Read on demand, don't load everything at once.

## What this project is

A reproducible recommender-systems lab on MovieLens (ml-latest-small): EDA,
trained models tracked with MLflow, and a prototype app that serves
recommendations from all models at their latest version.

## How work flows (SDD)

The `data-scientist` works on demand, only when the human asks: either
**generate ideas**, or **validate the human's idea**. Validation happens in a
notebook. Nothing is implemented in `src/` or served until the human approves
the notebook's findings.

```
human asks ──► data-scientist (generate ideas | validate the human's idea)
   └─► (validation: if a doubt, data-scientist asks through lead → loop until clear)
   └─► lead builds the plan (tasks + owner + sdd) ──► PLAN GATE (human approves the plan)
         └─► spec_author: spec of how to assemble the notebook (if sdd:true)
               └─► notebook validation (self-contained, full DS detail, model → test alias)
                     └─► HUMAN GATE (human approves the notebook) ──► mle-engineer implements into src/ + Staging
                           └─► mlops-engineer → reviewer → done
```

Full process: `docs/specs.md`. Completion criteria per phase: `CHECKPOINTS.md`.

## Clarifying a human's idea (validation requests)

When the human asks to validate an idea, the `data-scientist` investigates it.
If it has a doubt (scope, features, metrics, baseline), it asks through the
`lead`, in a loop, until everything is clear. Once clear, the `data-scientist`
hands the clarified idea to the `lead`, who routes to `spec_author` to write the
spec of how to assemble the notebook.

## Plan approval (before implementation)

After the `data-scientist` has everything clear, it hands the information to the
`lead`, who builds the plan: discrete tasks, each with an `owner` and an
`sdd: true|false` flag. The human must approve the plan before any
implementation:

1. **Not approved** → the `lead` asks why (or the human tells why).
   - **Directive / order** correction → the `lead` resolves the plan directly.
   - **Technical question** → the `lead` delegates to the `data-scientist`, who
     answers the `lead`, and the `lead` communicates the answer to the human,
     looping until the question is resolved.
   - Modify the plan if required, then ask again for approval.
2. **Approved** → the `lead` asks whether the human wants to implement.
   - **Yes** → implement, routing each task to its owner.
   - **No** → end the conversation / session.

## Notebook validation (before any implementation)

1. **Spec first.** Before writing the notebook, the `spec_author` writes a spec
   describing *how to assemble the notebook* (what to analyze, what features,
   what metrics, what baseline).
2. **Self-contained notebook.** All logic lives inside the notebook (no `src/`
   split yet), with full data-science detail: EDA, class balance, feature
   importance, metrics, and a baseline comparison.
3. **`test` alias.** The trained model is logged to MLflow under the `test`
   alias — never `Staging`/`Production` at this stage.
4. **HUMAN GATE.** The human reads the notebook and its validation results and
   approves. Only then does the `mle-engineer` implement the logic into `src/`
   and promote the model to `Staging` for serving.

## Agents

Defined in `.opencode/agents/`. One primary: `lead`. Subagents:
`data-scientist`, `spec_author`, `data-engineer`, `mle-engineer`, `reviewer`,
`mlops-engineer`. See `docs/architecture.md` for the role/ownership matrix.

## The lead routes tasks

The `lead` is the router: the human asks, the `lead` reads, plans, and delegates.
A plan is written *before* any investigation or implementation, and every task
names its `owner` agent (see `memory/README.md`). The `lead` routes each task to
its owner and records `current_owner` in `feature_list.json`:

- generate / validate ideas → `data-scientist`
- build a feature → `data-engineer`
- deploy a model to production (`src/`) → `mle-engineer`
- serve a model → `mlops-engineer`
- a task flagged `sdd: true` gets a spec from `spec_author` first, independent of its owner

Cross-agent requests go through the `lead` (e.g. `data-scientist` needs a
feature → `lead` → `data-engineer`).

Any question the human asks about a notebook (or about the data-science work)
is redirected to the `data-scientist`, who reviews the question and answers the
`lead`; the `lead` communicates the data-scientist's answer to the human. The
`lead` does not answer notebook questions itself.

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
- New/exploratory models are validated in a self-contained notebook first and
  logged under the `test` alias; repo implementation (`src/`) and `Staging`
  promotion happen only after human approval of the notebook findings.
- Every plan task names an `owner` agent; the `lead` routes the task to that
  owner (and records `current_owner` in `feature_list.json`).
- The human talks only through the `lead`, never directly with a subagent; every
  question, answer, and approval flows through the `lead`.

## Stack

pandas, scikit-surprise (SVD/KNN), implicit (ALS), PyTorch (NCF), mlflow,
fastapi + uvicorn.
