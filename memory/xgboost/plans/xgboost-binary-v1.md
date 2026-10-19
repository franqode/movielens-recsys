# plan: xgboost-binary-v1

- idea: xgboost-binary-v1
- status: in_progress
- sdd: true
- goal: prove in a notebook that a binary XGBoost model (rating 1 and 2 -> 0,
  ratings 3, 4, 5 -> 1; keep all ratings) can rank recommendations, evaluated
  with precision@10 and recall@10.

## Design decisions

- Task framing: pointwise binary classification over the full interaction set
  (all ratings 1-5 kept). 1 and 2 -> label 0; 3, 4, 5 -> label 1.
- Features (all tabular, no embeddings):
  - user: age, gender (one-hot), occupation (one-hot).
  - item: genres (multi-hot), release_year.
  - interaction: user_mean_rating, item_mean_rating, user_rating_count,
    item_rating_count (computed on training folds only to avoid leakage).
- Split: chronological, global 80/10/10 (train/validation/test). Test users
  and their held-out 5-star items are the ground truth for ranking eval.
- Evaluation (ranking, k=10) per test user over a candidate pool of unseen
  movies:
  - relevant set = the user's held-out 5-star movies.
  - candidates = movies not rated by that user in train (optionally capped for
    speed), scored by predicted P(positive), ranked descending.
  - precision@10 = |top10 ∩ relevant| / 10; recall@10 = |top10 ∩ relevant| / |relevant|.
  - report mean over test users; baseline = popularity (top-k by rating count).
- Class imbalance: positive (3-5 star) dominates negative (1-2 star). Use
  logistic objective; record `scale_pos_weight`/`max_depth`/`n_estimators`,
  fixed seed for reproducibility.

## tasks

- [x] t1 write spec of how to assemble the notebook                               owner: spec_author     sdd: true
- [x] t2 load ratings; filter {1,5}; map 1->0, 5->1; report class balance         owner: data-scientist  sdd: false
- [x] t3 build user/item/interaction features (train-fold statistics only)        owner: data-scientist  sdd: false
- [x] t4 chronological 80/10/10 split; define relevant set + candidate pool       owner: data-scientist  sdd: false
- [x] t5 train XGBoost binary classifier (fixed seed, logged hyperparams)         owner: data-scientist  sdd: false
- [x] t6 evaluate precision@10 / recall@10 vs popularity baseline                 owner: data-scientist  sdd: false
- [x] t7 log run to MLflow under `test` alias; update experiments.md              owner: data-scientist  sdd: false

After the notebook-validation HUMAN GATE passes, implementation follows (a
follow-on plan): `mle-engineer` implements into `src/` + `Staging`, then
`mlops-engineer` serves, then `reviewer` verifies completion.
