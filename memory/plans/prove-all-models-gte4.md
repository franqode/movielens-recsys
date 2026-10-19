# plan: prove-all-models-gte4

- idea: prove-all-models-gte4 (replaces retrain-threshold-gte2)
- status: pending
- sdd: true

## Directive (human, 2026-10-18)

1. Threshold `rating >= 4` for ALL models (replaces `>= 2`).
2. Delete all previous MLflow models.
3. Prove every model against the inline popularity baseline at `>= 4`.

## Scope

- Models to retrain/prove: `xgboost-binary-v1`, `xgboost-user-item-cross-terms`,
  `als-v1`, `svd` (the three existing + SVD). NOT ncf / knn_item (still ideas).

## Threshold semantics (`>= 4`)

- XGBoost pointwise binary: label `rating >= 4` (1,2,3 -> 0; 4,5 -> 1).
- ALS implicit: positive `rating >= 4` (confidence weighting unchanged).
- SVD: ranked by predicted rating; relevance set `rating >= 4`.
- Relevance set for ranking eval = held-out items with `rating >= 4` (all models).
- Popularity baseline: inline top-k by training-time rating count, `>= 4` relevance.

## Shared eval protocol

- Chronological 80/10/10 split, fixed seed.
- Per test user top-10; candidate pool = full catalog minus train-rated.
- Exclude empty-relevant users; report mean over test users.
- Metrics: precision@10 (primary, optimization target), NDCG@10 / recall@10 /
  hit-rate@10 (secondary).
- Every model compared against the SAME inline popularity baseline (>= 4).

## tasks

- [ ] t1 delete all previous MLflow models (destructive)                        owner: mlops-engineer  sdd: false
- [ ] t2 spec: xgboost-binary-v1 @ >= 4                                          owner: spec_author     sdd: true
- [ ] t3 retrain xgboost-binary-v1 @ >= 4 (notebook, test alias)                 owner: data-scientist  sdd: false
- [ ] t4 spec: xgboost-user-item-cross-terms @ >= 4                               owner: spec_author     sdd: true
- [ ] t5 retrain xgboost-user-item-cross-terms @ >= 4 (notebook, test alias)      owner: data-scientist  sdd: false
- [ ] t6 spec: als-v1 @ >= 4                                                      owner: spec_author     sdd: true
- [ ] t7 retrain als-v1 @ >= 4 (notebook, test alias)                             owner: data-scientist  sdd: false
- [ ] t8 spec: svd ranking @ >= 4                                                 owner: spec_author     sdd: true
- [ ] t9 train svd @ >= 4 (notebook, test alias)                                  owner: data-scientist  sdd: false
- [ ] t10 add inline popularity baseline (>= 4) comparison to all 4 notebooks     owner: data-scientist  sdd: false
- [ ] t11 HUMAN GATE: approve notebook findings                                   owner: lead            sdd: false

## Deferred (not in this plan — later directive)

- implement validated models into src/ + promote to Staging                    owner: mle-engineer
- serve all models (app/)                                                       owner: mlops-engineer
- review completion                                                              owner: reviewer

This plan stops at t11 (HUMAN GATE). Implementation/serving/review are deferred.
