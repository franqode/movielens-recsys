# plan: svd-ranking-beats-popularity

- idea: svd-ranking-beats-popularity (reframe of memory/svd/ideas.md `svd-vs-mean`
  from RMSE to ranking)
- status: pending
- sdd: true

## Directive (human, 2026-10-18)

"prove with svd" — validate whether SVD (surprise) can beat the popularity
baseline on ranking, ranked by predicted rating.

## Design decisions

- Model: SVD (surprise) latent factors, trained on the rating matrix.
- Ranking: score each candidate by predicted rating, rank descending, take top-10.
- Relevant set: held-out items with `rating >= 4` (the fair-test threshold — at
  `>= 2` popularity is near-optimal by construction and SVD is not expected to
  win; the data-scientist recommended `>= 4`).
- Candidate pool: full catalog minus the user's train-rated items.
- Split: chronological 80/10/10 (lab convention), fixed seed.
- Baseline: inline popularity (top-k by training-time rating count), same
  relevant set (`>= 4`), same test users, same candidate pool.
- Metrics: NDCG@10 (primary), precision@10 / recall@10 / hit-rate@10 (secondary).
- Eval protocol: per test user, top-10; exclude empty-relevant users; report
  mean over test users; applied identically to SVD and popularity.

## tasks

- [ ] t1 spec: how to assemble the SVD ranking validation notebook             owner: spec_author     sdd: true
- [ ] t2 train SVD (surprise, fixed seed, logged hyperparams)                  owner: data-scientist  sdd: false
- [ ] t3 evaluate NDCG@10 / precision@10 / recall@10 / hit-rate@10 vs popularity  owner: data-scientist  sdd: false
- [ ] t4 log run to MLflow under `test` alias (svd-v1); update experiments.md  owner: data-scientist  sdd: false
- [ ] t5 HUMAN GATE: approve notebook findings                                 owner: lead            sdd: false

After the notebook-validation HUMAN GATE passes, implementation follows (a
follow-on plan): `mle-engineer` implements into `src/` + `Staging`, then
`mlops-engineer` serves, then `reviewer` verifies completion.
