# Experiments — svd

## svd-v1-gte4 (ranking at threshold `rating >= 4`)

- run_id: 8a37c962a7b64abdab814ed2c1e3fda7
- code_version: 172af8dd3b087c250ce2c8aaaa38104e548b3a39
- data_version: 28770e0e10e2
- intent: svd-v1-gte4
- registry: svd-v1, test alias -> version 1
- hyperparams: n_factors=100 n_epochs=20 biased=True lr_all=0.005
  reg_all=0.02 random_state=42 (surprise SVD defaults + fixed seed)
- threshold: relevance = rating >= 4 (1/2/3 -> non-relevant; 4/5 -> relevant)
- metrics (mean over evaluated test users): precision@10=0.103030 (primary)
  ndcg@10=0.111802 recall@10=0.027465 hit-rate@10=0.463805
- EDA: n_users=6040 n_movies=3706 n_ratings=1000209 sparsity=0.0447;
  relevant cells (>=4)=575281 (ratio 0.5752, imbalance relevant/non-relevant 1.35)
- eval: chronological 80/10/10 split (800167/100021/100021); 1188 of 1209 test
  users evaluated (21 excluded for empty relevant set). Candidate pool = full
  catalog minus train-rated; ranked by SVD predicted rating (`mu + bu + bi +
  <pu, qi>`), top-10.
- cold-start note: surprise SVD learns factors only for users/items present in
  train (5400 users / 3662 items; 640 cold-start users, 44 cold-start items).
  Cold-start test users are scored with the non-personalized fallback
  `global_mean + item_bias` (mu=3.5905), keeping all 1188 relevant users in the
  eval set so it stays comparable to the other models in the plan.
- note: NO popularity baseline in this notebook (it is a separate shared step,
  plan t10). `test` alias only — no Staging/Production promotion.
