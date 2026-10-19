# plan: als-v1

- idea: als-implicit-beats-test-baseline (retitled from als-implicit-beats-svd-ranking)
- status: pending
- sdd: true
- goal: prove in a self-contained notebook that implicit-feedback ALS
  (confidence weighting) beats the current MLflow `test`-alias model
  (`xgboost-v1` v8) on NDCG@10 (primary) and precision@10 / recall@10 /
  hit-rate@10, because 4.47% rating sparsity and positively-skewed explicit
  ratings favor implicit interaction signal over a pointwise tabular GBM.

## Design decisions

- Input: ratings only (no user/item tabular features). Convert to implicit
  user-item matrix: positive = rating >= 4 (else 0), confidence = 1 + alpha*rating
  (alpha=40), unobserved = 0.
- Model: `implicit.als.AlternatingLeastSquares`, factors=64, alpha=40,
  regularization=0.1, iterations=15, fixed seed (reproducible).
- Baseline(s):
  - primary = `xgboost-v1` @ `test` alias (v8, run `5f84f66a695c46789501202741c7959a`):
    NDCG@10=0.071991, precision@10=0.067550, recall@10=0.013378 (best threshold T=2);
    matched T=4 (rating>=4): NDCG@10=0.057167, precision@10=0.055219, recall@10=0.015145.
  - secondary = inline popularity baseline (top-k by rating count; not registered).
  - hit-rate@10: xgboost-v1 never logged it, so report against recomputed inline
    popularity only.
- Split: chronological 80/10/10 train/val/test (lab convention). val = early
  check; test = final held-out metrics.
- Relevance: held-out item counts as relevant at rating >= 4 (matches the
  binarization threshold).
- Eval protocol (same as prior notebooks): per test user, score all items
  unrated-in-train with ALS, rank desc, take top-10; relevant set = user's
  held-out test items with rating >= 4; exclude test users with empty relevant
  set, applied identically to model and baselines; report mean
  precision@10 / recall@10 / NDCG@10 / hit-rate@10 over test users.
- MLflow: log under `test` alias, registry name `als-v1` (matches existing
  `xgboost-v1` pattern; note `docs/conventions.md` states `<model>/v<N>` — the
  actual repo uses `<model>-v<N>`, reconcile in implementation phase), tags
  `code_version` + `data_version` + `intent`.

## tasks

- [ ] t1 write spec of how to assemble the notebook                               owner: spec_author     sdd: true
- [x] t2 build implicit user-item matrix (binarize >=4, confidence 1+40*rating)   owner: data-scientist  sdd: false
- [x] t3 chronological 80/10/10 split; define relevant set (>=4) + candidate pool owner: data-scientist  sdd: false
- [x] t4 train implicit ALS (factors=64, alpha=40, reg=0.1, iters=15, seed)       owner: data-scientist  sdd: false
- [x] t5 evaluate NDCG@10 / precision@10 / recall@10 / hit-rate@10 vs baseline    owner: data-scientist  sdd: false
- [x] t6 log run to MLflow under `test` alias (als-v1); update experiments.md     owner: data-scientist  sdd: false

After the notebook-validation HUMAN GATE passes, implementation follows (a
follow-on plan): `mle-engineer` implements into `src/` + `Staging`, then
`mlops-engineer` serves, then `reviewer` verifies completion.
