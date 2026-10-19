# Design — als-v1

Technical decisions for assembling the self-contained validation notebook (all
logic inline, no `src/` split). The notebook trains an implicit-feedback ALS
model and proves it beats the current MLflow `test`-alias model (`xgboost-v1`
v8) on NDCG@10 (primary) and precision@10 / recall@10 / hit-rate@10.

## Decision: implicit feedback from ratings only (no tabular features)

Convert the explicit ratings into an implicit user-item confidence matrix:

- positive / relevant threshold = `rating >= 4`;
- confidence weight of an observed pair = `1 + alpha * rating` with `alpha=40`;
- unobserved pairs = `0`.

The model consumes only `userId, movieId, rating, timestamp`. No age, gender,
occupation, genres, or release-year features are built.

Rationale: 4.47% rating sparsity and a positively-skewed explicit rating
distribution (mean 3.58, mode 4) mean an implicit *interaction* signal is a
better fit than a pointwise tabular GBM over user/item features. Confidence
weighting (`1 + alpha*rating`) up-weights stronger observed preferences so the
model differentiates a 5-star from a 4-star rather than treating all positives
equally, while `unobserved = 0` keeps the matrix sparse.

## Decision: `AlternatingLeastSquares` config

`implicit.als.AlternatingLeastSquares(factors=64, alpha=40, regularization=0.1,
iterations=15, random_state=<fixed>)`. The `alpha` in the constructor matches
the confidence-weighting `alpha=40` so the matrix and the model are consistent.

Rationale: 64 latent factors is the standard lab-scale choice for
ml-latest-small; 15 iterations with L2 regularization 0.1 is enough to converge
without overfitting the sparse matrix. A fixed `random_state` (seed) makes the
run reproducible.

## Decision: chronological 80/10/10 split

Sort interactions by timestamp; earliest 80% = train, next 10% = validation,
last 10% = test. Train builds the implicit matrix the model is fit on;
validation is an early sanity check; test is the final held-out metric.

Rationale: this is the lab convention (matches the prior `xgboost-binary-v1`
spec) and respects the temporal nature of recommendation, preventing future
information from leaking into training.

## Decision: ranking evaluation protocol

Per test user:

- relevant set = user's held-out test items with `rating >= 4`;
- candidate pool = all items the user did NOT rate in train;
- score candidates with ALS, rank descending, take top 10;
- exclude test users whose relevant set is empty, applied identically to the
  model and every baseline;
- report mean NDCG@10 / precision@10 / recall@10 / hit-rate@10 over evaluated
  test users.

Rationale: identical to the prior notebooks' protocol so the ALS result is
directly comparable to the `xgboost-v1` numbers already recorded under the
`test` alias. NDCG@10 is the primary metric (it rewards relevant items ranked
high); precision@10 / recall@10 / hit-rate@10 are secondary.

## Decision: baseline comparison

- **Primary**: `xgboost-v1` @ `test` alias, v8 (run
  `5f84f66a695c46789501202741c7959a`), matched to the `rating >= 4` relevance
  threshold (T=4): `NDCG@10=0.057167`, `precision@10=0.055219`,
  `recall@10=0.015145`. (The plan also records the T=2 best-threshold numbers
  `0.071991 / 0.067550 / 0.013378`; the fair comparison is T=4 because ALS's
  relevance threshold is `>= 4`.)
- **Secondary / floor**: inline popularity baseline (top-10 by train rating
  count) computed on the same evaluated users and candidate pool, not
  registered.
- **hit-rate@10**: `xgboost-v1` never logged it, so ALS hit-rate@10 is compared
  against the recomputed inline popularity only.

Rationale: the human chose to compete against the existing `test`-alias model,
not to build a fresh SVD baseline. The inline popularity floor guards against a
model that merely reproduces global popularity.

## Decision: MLflow `test` alias only

Registry name `als-v1` (matching the repo's existing `xgboost-v1` pattern;
`docs/conventions.md` writes `<model>/v<N>` but the repo uses `<model>-v<N>`,
reconciled in the implementation phase). Tags `code_version` (git sha),
`data_version` (data hash), `intent` (`als-implicit-beats-test-baseline`).
Registered under `test`; no `Staging`/`Production` promotion at this stage.

## Decision: reproducibility

Fixed seed for ALS, deterministic chronological split, all hyperparameters
logged as MLflow params, and metrics recorded in `memory/als/experiments.md`.

## Rejected alternatives

- **Keep the original "beats SVD" framing / build an SVD baseline from scratch.**
  Rejected because no SVD model is registered in MLflow and the human chose to
  compete against the existing `test`-alias model (`xgboost-v1` v8). Building a
  fresh SVD just to compare would add an unregistered baseline and dilute the
  hypothesis.

- **Uniform confidence (treat all observed interactions as `1`).** Rejected:
  uniform confidence throws away the explicit rating strength; `1 + alpha*rating`
  is the standard implicit-feedback conversion and differentiates strong from
  weak preferences, which the hypothesis relies on.

- **Leave-one-out / per-user random holdout.** Rejected in favor of the
  chronological 80/10/10 split, which is the lab convention and prevents future
  information from leaking into training (and matches the prior notebook
  protocol so metrics stay comparable).

- **Binary `{3,4,5 -> 1, 1,2 -> 0}` relevance threshold.** Rejected: the plan
  fixes relevance at `rating >= 4` (matching the implicit binarization), not the
  `>= 3` threshold used by the earlier `xgboost-binary-v1` spec.
