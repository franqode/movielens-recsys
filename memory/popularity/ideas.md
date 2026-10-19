# Ideas — popularity

- id: pop-floor
  hypothesis: A most-popular baseline (top-k movies by rating count) beats
    random on NDCG@10 and hit-rate@10 and serves as the floor every
    personalized model must clear.
  evidence: Rating distribution is long-tailed (median 124 ratings/movie, max
    3,428); popularity is a strong, cheap signal in sparse explicit-feedback
    data (4.47% sparsity).
  status: proposed
