# Ideas — als

- id: als-implicit-beats-test-baseline
  hypothesis: Implicit-feedback ALS (confidence weighting, factors=64) beats the
    current MLflow `test`-alias model (xgboost-v1 v8) on NDCG@10 (primary) and
    precision@10 / recall@10 / hit-rate@10, because 4.47% sparsity and
    positively skewed explicit ratings favor implicit signal.
  evidence: Ratings skew positive (mean 3.58, modal value 4); only 3,706 of
    3,952 movies have any rating, so ranking from implicit interaction is a
    better fit than pointwise rating prediction. Baseline is xgboost-v1 @ test
    (NDCG@10=0.071991, precision@10=0.067550, recall@10=0.013378); no SVD is
    registered, so the comparison target is the existing test-alias model.
  status: accepted
