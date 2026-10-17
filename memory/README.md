# Memory

Per-model memory. Nothing in here is a binary artifact; it is all
human/agent-readable markdown, git-versioned.

## Layout

```
memory/<model>/
├── ideas.md            # intended ideas + status (proposed/accepted/rejected)
├── plans/<plan-id>.md  # accepted idea -> tasks (each sdd: true|false)
└── experiments.md      # runs: run_id, code_version, data_version, metrics
```

## ideas.md entry

```markdown
- id: ncf-emb-64
  hypothesis: NCF with embedding dim 64 beats SVD on NDCG@10
  status: proposed | accepted | rejected
```

## plans/<plan-id>.md entry

```markdown
# plan: ncf-emb-64
- idea: ncf-emb-64
- status: pending | in_progress | done
- tasks:
  - [ ] t1 build features        sdd: false
  - [ ] t2 train NCF             sdd: false
  - [ ] t3 evaluate vs SVD       sdd: false
```

## experiments.md entry

```markdown
## ncf-emb-64
- run_id: f8e7...
- code_version: 9c3f4a2
- data_version: a1b2c3
- metrics: rmse=0.89 ndcg@10=0.31
```

## Owners

- `data-scientist` writes `ideas.md`.
- `lead` writes `plans/<plan-id>.md`.
- `mle-engineer` writes `experiments.md`.
