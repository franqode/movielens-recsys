# Ideas — svd

- id: svd-vs-mean
  hypothesis: SVD (surprise, default hyperparameters) reduces RMSE vs the
    global-mean rating baseline (3.58) by at least 0.15 on a chronological
    80/20 holdout.
  evidence: Global mean is 3.58 with std 1.12; explicit ratings are dense enough
    per user (>=20, median 96) for a latent-factor model to learn personal taste.
  status: proposed
