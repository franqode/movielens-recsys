# Checkpoints

What must be true before each transition in the SDD lifecycle. The `lead`
enforces these; the `reviewer` verifies the final one.

## Idea → accepted

- Idea recorded in `memory/<model>/ideas.md` with status `proposed`.
- `lead` set status `accepted` (or `rejected`) and created a plan in
  `memory/<model>/plans/<plan-id>.md` with discrete tasks, each with an `owner`
  agent and an `sdd: true|false` flag.

## → `spec_ready` (only when a task has `sdd: true`)

- `specs/<model>/<plan-id>/requirements.md` exists, EARS strict, numbered R1, R2, ...
- `specs/<model>/<plan-id>/design.md` exists (decision + rejected alternative).
- `specs/<model>/<plan-id>/tasks.md` exists (discrete checklist).
- Every R<n> maps to a metric/test (see `docs/verification.md`).
- Human approved the spec (the `lead` asked and received approval).

## → `in_progress`

- Exactly one feature has `status: "in_progress"` in `feature_list.json`.
- If `sdd: false`, the plan still lists concrete tasks (no spec needed).

## → notebook validation gate (before repo implementation)

- `spec_author` wrote a spec describing how to assemble the notebook
  (`specs/<model>/<plan-id>/`).
- A self-contained notebook exists with all logic inline (no `src/` split yet)
  and full data-science detail: EDA, class balance, feature importance,
  metrics, and a baseline comparison.
- The trained model is logged to MLflow under the `test` alias — not
  `Staging`/`Production`.
- Human approves the notebook findings before the `mle-engineer` promotes the
  logic into `src/` and the model to `Staging`.

## → human gate (model approval)

- Model code exists at `src/movielens/models/<model>/v<N>/` with
  `model.py`, `evaluate.py`, `recommend.py`.
- Run logged to MLflow with tags `code_version`, `data_version`, `intent`.
- `memory/<model>/experiments.md` updated: run_id, code_version, data_version, metrics.
- Human approves the metrics before any serving.

## → `done` (via `reviewer`)

- `reviewer` verified every task in the plan/spec is successfully completed
  (`[x]`, deliverable exists and is correct, by the task's `owner`).
- Every R<n> mapped to a metric/test (traceability holds).
- If serving is in scope, it loads `models:/<model>/v<N>/Staging` (no binaries
  in `app/`).
- `progress/<model>/<plan-id>/review_<plan-id>.md` written with pass/fail per task.
- Only the `lead` flips `status` to `done` after reviewer sign-off.
