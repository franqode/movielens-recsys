# Spec-Driven Development process

Ideas become plans, plans become tasks, tasks may need a spec, then code, then
review. State lives on disk, never in chat.

## Lifecycle

```
pending ──(sdd=true)──► spec_ready ──(human approves)──► in_progress ──► done
   │                         │
   │                         └── reject → back to pending
   └──(sdd=false)──────────────────────────────────► in_progress
```

The `sdd` flag decides whether a task needs a written spec.

- `sdd: true` — new model, new hypothesis, new feature, cross-agent change.
- `sdd: false` — trivial/tactical change (tune a hyperparameter, re-run a baseline).

The `sdd` flag is independent of the task's `owner` agent: any task flagged
`sdd: true` gets a spec from `spec_author` first, whoever its owner is.

## EARS notation

Requirements are written in EARS (Easy Approach to Requirements Syntax), strict:

- `WHEN <trigger>, THE system SHALL <response>.`
- `WHILE <state>, THE system SHALL <response>.`

Number them R1, R2, ... Each must be traceable to a metric/test.

## The three spec files (`specs/<model>/<plan-id>/`)

- `requirements.md` — what must hold (EARS, numbered R1...), including target metrics.
- `design.md` — technical decisions + the rejected alternative and why.
- `tasks.md` — discrete checklist steps the implementer marks `[x]`.

## Approval gates

1. **Plan gate** (before implementation): the human approves the plan. If not
   approved, the `lead` asks why. A **directive/order** correction is resolved by
   the `lead` directly; a **technical question** is delegated to the
   `data-scientist`, who answers the `lead`, and the `lead` relays to the human
   in a loop until resolved. The plan is modified if required and re-submitted.
   Once approved, the `lead` asks whether the human wants to implement (no → end
   the session).
2. **Notebook validation gate**: the human reads the validation notebook and
   approves its findings before any repo implementation.
3. **Model gate** (after `mle-engineer` implementation): the human approves the
   implemented model's metrics before `mlops-engineer` serves it.

## Notebook validation phase (before repo implementation)

The `data-scientist` validates the human's idea in a notebook. Before any repo
implementation:

0. **Clarify first.** If the `data-scientist` has a doubt about the human's idea
   (scope, features, metrics, baseline), it asks through the `lead` in a loop
   until clear; then hands the clarified idea to the `lead` to route to
   `spec_author`.
1. **Spec first.** Before writing the notebook, the `spec_author` writes a spec
   describing *how to assemble the notebook* (what to analyze, what features,
   what metrics, what baseline).
2. **Self-contained notebook.** All logic lives inside the notebook (no `src/`
   split yet), with full data-science detail: EDA, class balance, feature
   importance, metrics, and a baseline comparison.
3. **`test` alias.** The trained model is logged to MLflow under the `test`
   alias — never `Staging`/`Production` at this stage.
4. **Notebook validation gate.** The human reads the notebook findings and
   approves. Only then does the `mle-engineer` implement the logic into `src/`
   and promote the model to `Staging` for serving.

## Traceability

Every `R<n>` maps to a metric/test. The `reviewer` rejects if any R<n> is
unmapped. See `docs/verification.md`.
