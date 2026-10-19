# Experiments — xgboost

## xgboost-user-item-cross-terms

- run_id: 5f84f66a695c46789501202741c7959a
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: xgboost-user-item-cross-terms
- test alias: version 8
- hyperparams: max_depth=6 n_estimators=100 learning_rate=0.1
  objective=binary:logistic seed=42 (scale_pos_weight varies per threshold, see below)
- features: 89 (47 base + 18 standalone user_genre_affinity[g] + 24 cross terms:
  um_x_im, um_x_ic, uc_x_im, uc_x_ic, age_x_year, genre_affinity_score, 18
  aff_x_genre_{g}). No scaling; no demographic x item terms.
- threshold sweep (best threshold by precision@10, ties -> NDCG@10):
  - T=2 (scale_pos_weight=0.0601): model precision@10=0.067550 recall@10=0.013378
    ndcg@10=0.071991 | baseline 0.212997 / 0.035990 / 0.224530  **BEST**
  - T=3 (0.1939): model 0.062822 / 0.013159 / 0.069782 | baseline 0.203154 /
    0.038631 / 0.215432
  - T=4 (0.7281): model 0.055219 / 0.015145 / 0.057167 | baseline 0.170286 /
    0.046312 / 0.182879
  - T=5 (3.3304): model 0.031559 / 0.024401 / 0.039232 | baseline 0.093557 /
    0.072528 / 0.117692
- best threshold: 2
- note: single ablation of cross terms. Feature importance confirms the new
  cross/affinity terms dominate (um_x_im gain 0.405, genre_affinity_score 0.039,
  uc_x_im, uc_x_ic, and several aff_x_genre_* / user_genre_affinity_* in the top
  25). vs prior no-cross-terms run fdab1c40799f460db34a2ec60e8c9774 (v7, T=3
  framing): precision@10 0.062822 vs 0.027137 (2.3x) and recall@10 0.013159 vs
  0.006287 (2.1x) — cross terms substantially beat the prior run. However the
  model still does NOT beat the popularity baseline on precision@10 at any
  threshold (best T=2: 0.067550 vs 0.212997), so the full hypothesis remains
  unsupported. No Staging/Production promotion.

### retrain at fixed threshold >= 2 (2026-10-18, single threshold, no baseline)

- run_id: 7185069d624f49b684e518547addf849
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: xgboost-user-item-cross-terms-gte2
- test alias: version 2 (registry xgboost-v1)
- threshold: rating >= 2 (single fixed cutoff; 1 -> 0, 2/3/4/5 -> 1). No sweep.
- hyperparams: max_depth=6 n_estimators=100 learning_rate=0.1
  objective=binary:logistic seed=42 scale_pos_weight=0.0601
- class balance (all ratings): label_1=944035 (94.38%) label_0=56174 (5.62%)
  ratio=16.81:1 (train-fold negatives/positives 45338/754829 -> spw 0.0601)
- features: 89 (47 base + 18 standalone user_genre_affinity[g] + 24 cross terms:
  um_x_im, um_x_ic, uc_x_im, uc_x_ic, age_x_year, genre_affinity_score, 18
  aff_x_genre_{g}). No scaling; no demographic x item terms. Train-fold-only
  leakage guards unchanged.
- metrics: precision@10=0.067550 recall@10=0.013378 ndcg@10=0.071991
  (eval_users=1208, empty-relevant users excluded).
- popularity baseline (inline, re-added; not registered to MLflow):
  precision@10=0.212997 recall@10=0.035990 ndcg@10=0.224530 on the same 1208 test
  users. Deltas (model - popularity): precision@10 -0.145447, recall@10 -0.022612,
  ndcg@10 -0.152539. Model loses to popularity on every metric at >= 2.
- note: re-training of xgboost-user-item-cross-terms at the human-fixed cutoff
  >= 2. Metrics exactly match the prior run's T=2 slice (identical features,
  split, seed, hyperparams). Feature importance still dominated by cross terms
  (um_x_im gain 0.405, genre_affinity_score 0.039, uc_x_im/uc_x_ic and several
  aff_x_genre_*/user_genre_affinity_* in top 25). No Staging/Production
  promotion.

### retrain at fixed threshold >= 4 (2026-10-19, single threshold, no baseline)

- run_id: bf96b5ebcdde43439727a056c4ed49bd
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: xgboost-user-item-cross-terms-gte4
- test alias: version 1 (registry xgboost-v1)
- note: the `xgboost-v1` registry and its single `test` alias are SHARED between
  `xgboost-user-item-cross-terms` (this run, version 1) and `xgboost-binary-v1`
  (version 2, run 8f619251806f49ae95f4c93dfefdbb35, intent xgboost-binary-v1-gte4).
  Both spec sets require the `test` alias on `xgboost-v1`, so the alias is
  "last-writer-wins" and collides across the two models — the same collision
  documented in the prior gte2 round. The alias currently points to version 1
  (this cross-terms run); flagged to the lead for resolution (the registry name
  likely needs to be per-model, per `docs/conventions.md` `<model>/v<N>`).
- threshold: rating >= 4 (single fixed cutoff; 1,2,3 -> 0, 4,5 -> 1). No sweep.
- hyperparams: max_depth=6 n_estimators=100 learning_rate=0.1
  objective=binary:logistic seed=42 scale_pos_weight=0.7281
- class balance (all ratings): label_1=575281 (57.52%) label_0=424928 (42.48%)
  ratio=0.7386 negative/positive (train-fold negatives/positives 337147/463020 ->
  spw 0.7281)
- features: 89 (47 base + 18 standalone user_genre_affinity[g] + 24 cross terms:
  um_x_im, um_x_ic, uc_x_im, uc_x_ic, age_x_year, genre_affinity_score, 18
  aff_x_genre_{g}). No scaling; no demographic x item terms. Train-fold-only
  leakage guards unchanged.
- metrics: precision@10=0.055219 recall@10=0.015145 ndcg@10=0.057167
  (eval_users=1188, empty-relevant users excluded).
- note: re-training of xgboost-user-item-cross-terms at the human-fixed cutoff
  >= 4 (plan prove-all-models-gte4, task t5). No popularity baseline in this
  notebook (baseline comparison is the separate shared step t10). Metrics exactly
  match the prior threshold-sweep run's T=4 slice (identical features, split,
  seed, hyperparams). Feature importance still dominated by cross terms (um_x_im
  gain 0.561, genre_affinity_score 0.037, uc_x_im/uc_x_ic and several
  aff_x_genre_*/user_genre_affinity_* in top 25). No Staging/Production
  promotion.

## xgboost-binary-v1

### {1,2,3,4,5} framing (label 1 = rating >= 4, label 0 = 1+2+3-star) — prove-all-models-gte4

- run_id: 8f619251806f49ae95f4c93dfefdbb35
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: xgboost-binary-v1-gte4
- registry: xgboost-v1, registered version 2, `test` alias (set at registration)
- threshold: rating >= 4 (single fixed cutoff; 1,2,3 -> 0; 4,5 -> 1). All ratings kept.
- hyperparams: max_depth=6 n_estimators=100 learning_rate=0.1
  objective=binary:logistic eval_metric=logloss seed=42 scale_pos_weight=0.7281
- class balance (all ratings): label_1=575281 (57.52%) label_0=424928 (42.48%)
  ratio=1.35:1 (train-fold positives/negatives 463020/337147 -> spw 0.7281)
- features: 47 tabular (age + gender one-hot + occupation one-hot + genres multi-hot +
  release_year + user/item mean rating + user/item rating count). No embeddings. No
  scaling. Train-fold-only leakage guards unchanged.
- metrics: precision@10=0.001010 recall@10=0.000259 ndcg@10=0.000919
  (eval_users=1188, 21 excluded as empty relevant set).
- note: prove-all-models-gte4 retrain — positive-label cutoff moved to `>= 4`
  (1,2,3-star -> 0; 4,5-star -> 1) keeping ALL ratings. Same 47 features, chronological
  80/10/10 split, seed 42, max_depth=6. NO popularity baseline in this notebook (deferred
  to shared plan step t10). Feature importance dominated by item_mean_rating (gain 0.444)
  then user_mean_rating (0.174); without collaborative/cross-term signal the model ranks
  nearly by (near-constant) item mean rating, so precision@10 collapses to ~0.001
  (sanity check: inline popularity baseline on the same 1188 users = 0.170286, item-mean
  ranking = 0.000421). This matches prior findings that the pointwise tabular model
  cannot beat popularity at any threshold. No Staging/Production promotion.
- CAVEAT: registry `xgboost-v1` + `test` alias is SHARED with the concurrent
  xgboost-user-item-cross-terms-gte4 retrain (t5), which also registers under
  `xgboost-v1`/`test`; the two runs race and re-point the `test` alias over each other
  (this run registered version 2; the cross-terms run later re-pointed `test` to its
  version). Flagged to lead — the two xgboost specs should use distinct registry names or
  aliases.

### {2,3,4,5} framing (label 1 = rating >= 2, label 0 = 1-star) — retrain-threshold-gte2

- run_id: 643118880c944a8dbac59937d2171752
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: xgboost-binary-v1-gte2
- registry: xgboost-v1, registered version 1 (test alias set at registration;
  note a concurrently-running cross-terms retrain later re-pointed the `test`
  alias — see cross-terms section)
- hyperparams: max_depth=6 n_estimators=100 learning_rate=0.1
  scale_pos_weight=0.0601 objective=binary:logistic seed=42 eval_metric=logloss
- metrics: precision@10=0.059603 recall@10=0.010950 ndcg@10=0.062298
- popularity baseline (inline, re-added; not registered to MLflow):
  precision@10=0.212997 recall@10=0.035990 ndcg@10=0.224530 on the same 1208 test
  users. Deltas (model - popularity): precision@10 -0.153394, recall@10 -0.025040,
  ndcg@10 -0.162232. Model loses to popularity on every metric at >= 2.
- class balance: label_1=944035 (94.38%) label_0=56174 (5.62%) ratio=16.81:1
- note: retrain-threshold-gte2 directive — positive-label cutoff moved from
  `>= 3` to `>= 2` (rating 1 -> 0; 2,3,4,5 -> 1). All ratings 1-5 kept (nothing
  dropped). 47 tabular features unchanged, chronological 80/10/10 split, seed 42.
  NO popularity baseline (deleted by human; re-added as an inline comparison in a
  follow-on step t8b). 1209 test users, 1 excluded (empty relevant set), 1208
  evaluated. No Staging/Production promotion.

### {1,2,3,4,5} framing (label 1 = 3+4+5-star, label 0 = 1+2-star)

- run_id: fdab1c40799f460db34a2ec60e8c9774
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: xgboost-binary-v1
- test alias: version 7
- hyperparams: max_depth=6 n_estimators=100 learning_rate=0.1
  scale_pos_weight=0.1939 objective=binary:logistic seed=42
- metrics: precision@10=0.027137 recall@10=0.006287
  baseline_precision@10=0.203154 baseline_recall@10=0.038631
- class balance: label_1=836478 (83.63%) label_0=163731 (16.37%) ratio=5.11:1
- note: {1,2,3,4,5} framing iteration. All ratings kept (no filtering); label 1 =
  rating >= 3 (3+4+5-star), label 0 = 1+2-star. Model still does NOT beat the
  popularity baseline on precision@10/recall@10 (negative deltas), so the
  hypothesis remains unsupported. No Staging/Production promotion.
- corrected metrics note: evaluation now excludes test users with an empty
  relevant set (no held-out 3+4+5-star items) from the mean of precision@10 /
  recall@10, per R11/R12. 4 of 1209 test users excluded (1205 evaluated);
  filtering applied identically to model and popularity baseline. Corrected
  metrics (model precision@10=0.027137 recall@10=0.006287 vs baseline
  precision@10=0.203154 recall@10=0.038631) do not change the verdict: the model
  still does NOT beat the popularity baseline. Re-logged as run
  fdab1c40799f460db34a2ec60e8c9774 (test alias version 7), superseding run
  5ea452b6c2ed4e28a17168a2ac94102f (version 6).

### {1,4,5} framing (label 1 = 4+5-star, label 0 = 1-star)

- run_id: 6ec03025a5be444ca29d1c337dbc6e6c
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: xgboost-binary-v1
- test alias: version 5
- hyperparams: max_depth=6 n_estimators=100 learning_rate=0.1
  scale_pos_weight=0.0979 objective=binary:logistic seed=42
- metrics: precision@10=0.060589 recall@10=0.016261
  baseline_precision@10=0.174652 baseline_recall@10=0.045852
- class balance: label_1=575281 (91.11%) label_0=56174 (8.89%) ratio=10.24:1
- note: {1,4,5} framing iteration. Ratings 2 and 3 are dropped; label 1 =
  rating >= 4 (4+5-star), label 0 = 1-star. Model still does NOT beat the
  popularity baseline on precision@10/recall@10 (negative deltas), so the
  hypothesis remains unsupported. No Staging/Production promotion.

### {1,5} framing (label 1 = 5-star, label 0 = 1-star) — superseded

- run_id: 1de1f63a0b034ad685d113398dd6a68f
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: xgboost-binary-v1
- test alias: version 4 (superseded by version 5)
- hyperparams: max_depth=6 n_estimators=100 learning_rate=0.1
  scale_pos_weight=0.2447 objective=binary:logistic seed=42
- metrics: precision@10=0.034523 recall@10=0.026569
  baseline_precision@10=0.102158 baseline_recall@10=0.070669
- class balance: label_1=226310 (80.11%) label_0=56174 (19.89%) ratio=4.03:1
- note: validation-first run. Model does NOT beat the popularity baseline on
  precision@10/recall@10 (negative deltas), so the hypothesis is not supported
  by this pointwise tabular-feature framing. No Staging/Production promotion.
- superseded run (premature, pre-validation): run_id 773e0a1c517746dc8816e9729f929e32
  (archived, identical metrics; was implemented into src/ before notebook validation).
