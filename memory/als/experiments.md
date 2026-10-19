# Experiments — als

## als-implicit-beats-test-baseline

- run_id: fe4ed22ebac84a8cbe0ac2393db386b7
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: als-implicit-beats-test-baseline
- test alias: version 1
- hyperparams: factors=64 alpha=40 regularization=0.1 iterations=15
  random_state=42 num_threads=1 dtype=float32
- metrics: ndcg@10=0.038974 precision@10=0.037542 recall@10=0.009310
  hit-rate@10=0.233165
  baseline (popularity) ndcg@10=0.182879 precision@10=0.170286 recall@10=0.046312
  hit-rate@10=0.589226
- vs xgboost-v1 @ test alias v8 (T=4, rating>=4): ndcg@10 0.038974 vs 0.057167
  (delta -0.018193), precision@10 0.037542 vs 0.055219, recall@10 0.009310 vs
  0.015145. ALS does NOT beat the baseline on the primary metric (ndcg@10) nor on
  precision@10 / recall@10, and is far below the popularity floor. Hypothesis
  unsupported. No Staging/Production promotion (test alias only).
- reproducibility note: single-threaded fitting (num_threads=1, dtype=float32,
  OPENBLAS/OMP/MKL_NUM_THREADS=1) alongside fixed random_state=42 for stable,
  traceable metrics across threads.
- eval: chronological 80/10/10 split (800167/100021/100021); 1188 of 1209 test
  users evaluated (21 excluded for empty relevant set), applied identically to
  model and popularity baseline. Popularity baseline reproduces the prior T=4
  xgboost baseline exactly (0.170286/0.046312/0.182879), confirming protocol parity.

## als-v1-gte2 (retrain at threshold rating >= 2)

- run_id: cb2fc4575d844cd69de7584a2bf46715
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: als-v1-gte2
- test alias: version 1
- hyperparams: factors=64 alpha=40 regularization=0.1 iterations=15
  random_state=42 num_threads=1 dtype=float32
- threshold: positive/relevance = rating >= 2 (was >= 4); confidence =
  1 + 40*rating unchanged; unobserved = 0.
- metrics: ndcg@10=0.062205 precision@10=0.061093 recall@10=0.009941
  hit-rate@10=0.345199 (mean over evaluated test users).
- popularity baseline (inline, re-added; not registered to MLflow): ndcg@10=0.224530
  precision@10=0.212997 recall@10=0.035990 hit-rate@10=0.636589 on the same 1208
  test users. Deltas (model - popularity): ndcg@10 -0.162325,
  precision@10 -0.151904, recall@10 -0.026049, hit-rate@10 -0.291391. ALS loses
  to popularity on every metric at >= 2.
- EDA: n_users=6040 n_movies=3706 n_ratings=1000209 sparsity=0.0447;
  positive cells (>=2)=944035 (ratio 0.9438, imbalance positive/non-positive
  16.81).
- eval: chronological 80/10/10 split (800167/100021/100021); 1208 of 1209 test
  users evaluated (1 excluded for empty relevant set). Inline popularity baseline
  comparison re-added per directive (model-independent, one set of numbers shared
  across all retrained models). Test alias only (no Staging/Production promotion).

## als-v1-gte4 (plan prove-all-models-gte4, threshold rating >= 4)

- run_id: 7d33a2f998274df48e81b6c8f3e5b91a
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: als-v1-gte4
- test alias: version 1
- hyperparams: factors=64 alpha=40 regularization=0.1 iterations=15
  random_state=42 num_threads=1 dtype=float32
- threshold: positive/relevance = rating >= 4 (unchanged from original als-v1);
  confidence = 1 + 40*rating unchanged; unobserved = 0.
- metrics: precision@10=0.037542 (primary), ndcg@10=0.038974, recall@10=0.009310,
  hit-rate@10=0.233165 (mean over evaluated test users).
- EDA: n_users=6040 n_movies=3706 n_ratings=1000209 sparsity=0.0447;
  positive cells (>=4)=575281 (ratio 0.5752, imbalance positive/non-positive
  1.35).
- eval: chronological 80/10/10 split (800167/100021/100021); 1188 of 1209 test
  users evaluated (21 excluded for empty relevant set). NO popularity baseline
  in this notebook (deferred to shared step t10). Test alias only (no
  Staging/Production promotion).
