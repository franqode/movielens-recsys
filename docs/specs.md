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

1. **Spec gate** (`spec_ready`): the human reads the three spec files and
   approves (or requests changes) before any code is written.
2. **Model gate** (after training): the human approves the trained model's
   metrics before `mlops-engineer` serves it.

## Traceability

Every `R<n>` maps to a metric/test. The `reviewer` rejects if any R<n> is
unmapped. See `docs/verification.md`.
