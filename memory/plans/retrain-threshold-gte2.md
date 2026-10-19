# plan: retrain-threshold-gte2

- idea: retrain all existing models with rating threshold >= 2; drop popularity;
  delete all previous MLflow model versions.
- status: pending
- sdd: true

## Directive (human, 2026-10-18)

1. Retrain all existing models with the positive-label cutoff `rating >= 2`
   (replaces the current `>= 3` XGBoost framing and the `>= 4` ALS implicit
   binarization).
2. Delete the popularity model (no popularity baseline going forward).
3. Delete all previous MLflow model versions (including `test`/`Staging`
   aliases), leaving only the newly retrained `>= 2` versions.

## Scope (confirmed)

- Retrain only the models already in `feature_list.json`:
  - `xgboost-binary-v1`
  - `xgboost-user-item-cross-terms`
  - `als-v1`
- Do NOT newly train SVD / NCF / KNN.

## Threshold change semantics

- XGBoost pointwise binary: label `rating >= 2` (was `{1,2 -> 0, 3,4,5 -> 1}`).
- ALS implicit binarization: positive `rating >= 2` (was `>= 4`), confidence
  weighting unchanged (`1 + alpha*rating`).
- Relevance set for ranking eval matches each model's threshold (`>= 2`).
- All other design decisions (features, split, seed, hyperparams, metrics)
  unchanged from the existing per-model plans.

## tasks

- [ ] t1 delete popularity model + all previous MLflow versions (destructive)  owner: mlops-engineer  sdd: false
- [ ] t2 spec: retrain xgboost-binary-v1 at >= 2                                 owner: spec_author     sdd: true
- [ ] t3 retrain xgboost-binary-v1 at >= 2 (notebook, test alias)                owner: data-scientist  sdd: false
- [ ] t4 spec: retrain xgboost-user-item-cross-terms at >= 2                      owner: spec_author     sdd: true
- [ ] t5 retrain xgboost-user-item-cross-terms at >= 2 (notebook, test alias)     owner: data-scientist  sdd: false
- [ ] t6 spec: retrain als-v1 at >= 2                                             owner: spec_author     sdd: true
- [ ] t7 retrain als-v1 at >= 2 (notebook, test alias)                            owner: data-scientist  sdd: false
- [ ] t8b add inline popularity baseline (>= 2) comparison to the 3 notebooks    owner: data-scientist  sdd: false
- [ ] t8 HUMAN GATE: approve notebook findings                                   owner: lead            sdd: false

## Deferred (not in this plan — later directive)

- t9 implement validated models into src/ + promote to Staging                  owner: mle-engineer
- t10 serve all models at latest version (app/)                                 owner: mlops-engineer
- t11 review completion                                                           owner: reviewer

This plan stops at t8 (HUMAN GATE). Implementation/serving/review are deferred
to a follow-on directive after the human approves the notebook findings.
