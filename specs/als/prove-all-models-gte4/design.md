# Design — als-v1 @ rating >= 4 (plan prove-all-models-gte4)

Technical decisions for assembling the self-contained validation notebook (all
logic inline, no `src/` split). The notebook retrains the implicit-feedback ALS
model (`als-v1`) with the positive/relevance cutoff at `rating >= 4`. There is
NO baseline comparison inside this notebook: the inline popularity baseline is a
separate shared step (plan t10), so the single evaluation is the ALS model's own
metrics at threshold >= 4.

## Decision: implicit feedback from ratings only (no tabular features)

Convert the explicit ratings into an implicit user-item confidence matrix:

- positive / relevant threshold = `rating >= 4` (the original `als-v1`
  threshold, unchanged);
- confidence weight of an observed pair = `1 + alpha * rating` with `alpha=40`
  (unchanged);
- unobserved pairs = `0`.

The model consumes only `userId, movieId, rating, timestamp`. No age, gender,
occupation, genres, or release-year features are built.

Rationale: 4.47% rating sparsity and a positively-skewed explicit rating
distribution (mean 3.58, mode 4) mean an implicit *interaction* signal is a
better fit than a pointwise tabular GBM over user/item features. Confidence
weighting (`1 + alpha*rating`) up-weights stronger observed preferences so the
model differentiates a 5-star from a 4-star rather than treating all positives
equally, while `unobserved = 0` keeps the matrix sparse. The `>= 4` cutoff is
the original `als-v1` threshold; it is retained here per the plan directive that
all models use `>= 4`.

## Decision: `AlternatingLeastSquares` config

`implicit.als.AlternatingLeastSquares(factors=64, alpha=40, regularization=0.1,
iterations=15, random_state=<fixed>)`. The `alpha` in the constructor matches
the confidence-weighting `alpha=40` so the matrix and the model are consistent.

Rationale: hyperparameters are unchanged from the original `als-v1` spec (only
the primary metric changes, see below). 64 latent factors is the standard
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

- relevant set = user's held-out test items with `rating >= 4`;
- candidate pool = all items the user did NOT rate in train;
- score candidates with ALS, rank descending, take top 10;
- exclude test users whose relevant set is empty;
- report mean precision@10 (primary) / NDCG@10 / recall@10 / hit-rate@10
  (secondary) over evaluated test users.

Rationale: identical to the original `als-v1` protocol (relevance `>= 4`), but
with `precision@10` promoted to the primary/optimization target and
`NDCG@10`/`recall@10`/`hit-rate@10` demoted to secondary, per the plan's shared
eval protocol. There is no baseline comparison inside this notebook: the inline
popularity baseline is added to all four notebooks as a separate shared step
(plan t10), so this notebook reports the model's own metrics only.

## Decision: MLflow `test` alias only

Registry name `als-v1` (matching the repo's existing pattern). Tags
`code_version` (git sha), `data_version` (data hash), `intent` (`als-v1-gte4`).
Registered under `test`; no `Staging`/`Production` promotion at this stage.

## Decision: reproducibility

Fixed seed for ALS, deterministic chronological split, all hyperparameters
logged as MLflow params, and metrics recorded in `memory/als/experiments.md`.

## Rejected alternatives

- **Keep `NDCG@10` as the primary metric.** Rejected: the plan's shared eval
  protocol fixes `precision@10` as the primary optimization target for all
  models and lists `NDCG@10`/`recall@10`/`hit-rate@10` as secondary.

- **Include an inline popularity baseline in this notebook.** Rejected: the
  human moved the popularity-baseline comparison out of the per-model notebooks
  into a single shared step (plan t10) so all four models are compared against
  the same baseline in one place.

- **Change the confidence-weighting formula or hyperparameters alongside the
  threshold.** Rejected: the plan keeps `1 + alpha*rating` (alpha=40),
  `factors=64`, `regularization=0.1`, `iterations=15`, and the fixed seed
  unchanged; only the primary metric changes.

- **Leave-one-out / per-user random holdout.** Rejected in favor of the
  chronological 80/10/10 split, which is the lab convention and prevents future
  information from leaking into training.
