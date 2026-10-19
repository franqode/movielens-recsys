# Design — svd (prove-all-models-gte4, task t8)

Technical decisions for assembling the self-contained validation notebook (all
logic inline, no `src/` split). The notebook trains a surprise SVD model and
reports its ranking quality at the `rating >= 4` relevance threshold.

## Decision: SVD latent factors trained on the rating matrix

Train `surprise.SVD` directly on the explicit rating matrix (no tabular
user/item features). SVD factorizes the user-item rating matrix into user and
item latent factors, then reconstructs a predicted rating for any unobserved
`(userId, movieId)` pair. The reconstructed rating is the ranking score.

Rationale: SVD is the natural explicit-feedback baseline for ml-latest-small
(mean 3.58, std 1.12, >=20 ratings per user). Latent factors capture personal
taste from the dense-enough per-user rating history, which the
`svd-vs-mean` idea already argued for; here the predicted rating is consumed as
a ranking score rather than compared to the global mean.

## Decision: rank by predicted rating, top-10

Score each candidate `(user, item)` with the SVD-predicted rating, sort
descending, and keep the top 10. The predicted rating is used purely as a
relative ordering signal; no calibration to actual rating scale is required
because relevance is a binary `>= 4` threshold.

Rationale: matches the plan directive ("ranked by predicted rating") and the
shared `prove-all-models-gte4` eval protocol, keeping SVD directly comparable
to the other models in the same plan.

## Decision: chronological 80/10/10 split, fixed seed

Sort interactions by timestamp; earliest 80% = train, next 10% = validation,
last 10% = test, under a fixed seed. Train builds the rating matrix SVD is fit
on; validation is an early sanity check; test is the final held-out metric.

Rationale: lab convention (matches the ALS and XGBoost specs) and respects the
temporal nature of recommendation, preventing future information from leaking
into training. The fixed seed makes the split deterministic.

## Decision: relevance threshold `rating >= 4`

A held-out item is relevant iff its rating is `>= 4`. Candidates are scored and
ranked against this binary relevance set.

Rationale: the `prove-all-models-gte4` plan fixes the threshold at `>= 4` for
ALL models. At `>= 2` the popularity baseline is near-optimal by construction
and SVD is not expected to win; `>= 4` is the fair-test threshold the
data-scientist recommended.

## Decision: candidate pool = full catalog minus train-rated

Per test user, candidates = all items the user did NOT rate in train. This
excludes items already consumed in training so the model cannot trivially
"recommend" what the user already rated.

Rationale: matches the shared eval protocol in the plan and the prior notebook
specs, so metrics stay comparable across models.

## Decision: precision@10 primary, NDCG@10 / recall@10 / hit-rate@10 secondary

Report all four metrics as the mean over evaluated test users (excluding
empty-relevant users), with `precision@10` as the optimization target.

Rationale: the `prove-all-models-gte4` plan elevates `precision@10` to the
primary metric across all four models; the other three remain secondary
diagnostics.

## Decision: no popularity baseline inside this notebook

This notebook reports SVD's own metrics only. The inline popularity baseline
(`>= 4`) comparison is a **shared** step (plan task t10) added uniformly to all
four notebooks, so the comparison logic lives in one place and is applied
identically to every model.

Rationale: keeps each model's notebook self-contained for its own training and
evaluation, and avoids duplicating (and drifting) the popularity baseline logic
across four notebooks.

## Decision: MLflow `test` alias only, registry `svd-v1`

Registry name `svd-v1`; tags `code_version` (git sha), `data_version` (data
hash), `intent` (`svd-v1-gte4`). Registered under the `test` alias; no
`Staging`/`Production` promotion at this stage (validation phase only).

## Decision: reproducibility

Fixed `random_state` seed for SVD, deterministic chronological split, all
hyperparameters logged as MLflow params, and metrics recorded in
`memory/svd/experiments.md`.

## Rejected alternatives

- **Inline popularity baseline inside this notebook.** Rejected in favor of the
  shared step (t10), which adds the `>= 4` popularity baseline to all four
  notebooks uniformly and avoids duplicated, drift-prone logic.

- **Retain the RMSE framing (`svd-vs-mean`).** Rejected: the human reframed the
  idea from rating-error (RMSE vs global mean 3.58) to ranking at `>= 4`, which
  is the shared objective across the `prove-all-models-gte4` plan.

- **Relevance threshold `>= 2` (or `>= 3`).** Rejected: the plan fixes `>= 4`
  for all models; at `>= 2` popularity is near-optimal by construction and SVD
  is not expected to win.

- **Leave-one-out / per-user random holdout.** Rejected in favor of the
  chronological 80/10/10 split, the lab convention that prevents temporal
  leakage and keeps metrics comparable to the other models in the plan.

- **Non-default SVD hyperparameters (tuned).** Rejected for this validation
  pass: the idea specifies surprise defaults; tuning is a follow-on step once
  the default model's ranking quality is established against the baseline.
