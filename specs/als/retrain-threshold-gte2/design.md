# Design — als-v1 retrain at threshold >= 2

Technical decisions for assembling the self-contained validation notebook (all
logic inline, no `src/` split). The notebook retrains the implicit-feedback ALS
model (`als-v1`) with the positive/relevance cutoff moved from `rating >= 4` to
`rating >= 2`. There is NO baseline comparison — the single evaluation is the
ALS model's own metrics at threshold >= 2.

## Decision: implicit feedback from ratings only (no tabular features)

Convert the explicit ratings into an implicit user-item confidence matrix:

- positive / relevant threshold = `rating >= 2` (was `>= 4`);
- confidence weight of an observed pair = `1 + alpha * rating` with `alpha=40`
  (unchanged);
- unobserved pairs = `0`.

The model consumes only `userId, movieId, rating, timestamp`. No age, gender,
occupation, genres, or release-year features are built.

Rationale: the human's directive moves the positive cutoff to `>= 2`, which
treats every non-1-star interaction as implicit positive signal (a much larger
positive set than `>= 4`), while confidence weighting (`1 + alpha*rating`)
continues to up-weight stronger observed preferences so a 5-star still dominates
a 2-star rather than treating all positives equally. `unobserved = 0` keeps the
matrix sparse.

## Decision: `AlternatingLeastSquares` config

`implicit.als.AlternatingLeastSquares(factors=64, alpha=40, regularization=0.1,
iterations=15, random_state=<fixed>)`. The `alpha` in the constructor matches
the confidence-weighting `alpha=40` so the matrix and the model are consistent.

Rationale: hyperparameters are unchanged from the existing `als-v1` plan (only
the binarization threshold changes). 64 latent factors is the standard
lab-scale choice for ml-latest-small; 15 iterations with L2 regularization 0.1
is enough to converge without overfitting the sparse matrix. A fixed
`random_state` (seed) makes the run reproducible.

## Decision: chronological 80/10/10 split

Sort interactions by timestamp; earliest 80% = train, next 10% = validation,
last 10% = test. Train builds the implicit matrix the model is fit on;
validation is an early sanity check; test is the final held-out metric.

Rationale: this is the lab convention (matches the prior `als-v1` spec) and
respects the temporal nature of recommendation, preventing future information
from leaking into training.

## Decision: ranking evaluation protocol (no baseline)

Per test user:

- relevant set = user's held-out test items with `rating >= 2`;
- candidate pool = all items the user did NOT rate in train;
- score candidates with ALS, rank descending, take top 10;
- exclude test users whose relevant set is empty;
- report mean NDCG@10 / precision@10 / recall@10 / hit-rate@10 over evaluated
  test users.

Rationale: identical to the prior `als-v1` protocol except the relevance
threshold is `>= 2` (matching the new binarization threshold). NDCG@10 is the
primary metric (it rewards relevant items ranked high); precision@10 /
recall@10 / hit-rate@10 are secondary. There is no baseline: the human deleted
the popularity baseline and the `xgboost-v1` test-alias baseline, and removed
all prior MLflow versions, so the only evaluation is the model's own metrics at
threshold >= 2.

## Decision: MLflow `test` alias only

Registry name `als-v1` (matching the repo's existing pattern). Tags
`code_version` (git sha), `data_version` (data hash), `intent` (`als-v1-gte2`).
Registered under `test`; no `Staging`/`Production` promotion at this stage.

## Decision: reproducibility

Fixed seed for ALS, deterministic chronological split, all hyperparameters
logged as MLflow params, and metrics recorded in `memory/als/experiments.md`.

## Rejected alternatives

- **Keep the `rating >= 4` binarization threshold.** Rejected: the human's
  directive explicitly moves the positive cutoff to `>= 2` for all existing
  models, so the threshold must change to match.

- **Change the confidence weighting formula alongside the threshold.** Rejected:
  the directive keeps `1 + alpha*rating` (alpha=40) unchanged; only the
  positive/relevance cutoff moves.

- **Retain a popularity or `xgboost-v1` test-alias baseline comparison.**
  Rejected: the human deleted the popularity model and all prior MLflow
  versions; there is no baseline to compare against. The single evaluation is
  the ALS model's own metrics at threshold >= 2.

- **Leave-one-out / per-user random holdout.** Rejected in favor of the
  chronological 80/10/10 split, which is the lab convention and prevents future
  information from leaking into training.
