# Design — xgboost-user-item-cross-terms

Technical decisions for assembling the validation notebook. The notebook is
self-contained (all logic inline, no `src/` split) and extends the pointwise
XGBoost recommender with user-item cross terms, validated under the MLflow
`test` alias.

## Decision: extend the existing pointwise XGBoost (base unchanged)

Start from the prior `xgboost-binary-v1` setup and keep everything identical
except for one deliberate change: the binary threshold becomes a *variable*
swept over `T ∈ {2, 3, 4, 5}` (`label = 1 if rating >= T else 0`), instead of a
single fixed `{1,2 -> 0, 3,4,5 -> 1}` cut. All ratings are retained in every
case. Everything else stays identical: 47 tabular features, chronological
80/10/10 split, seed 42, `max_depth=6`. The only other change is the added
cross/affinity features and the ablation-style comparison.

Rationale: this is a controlled ablation — isolating the effect of cross terms
requires holding every other knob fixed so the metric delta is attributable to
the new features alone, and comparable to the prior `test`-alias run.

Class imbalance varies per threshold (higher `T` → fewer positives), so the
positive/negative ratio — and any `scale_pos_weight` — is set per threshold.

## Decision: `user_genre_affinity[g]` as a shrunk mean-rating deviation

For each (user, genre) pair, compute the shrunk mean deviation:

```
affinity[u,g] = (sum over u's train ratings in genre g of (rating - global_mean))
                / (count_u,g + 5)
```

where `global_mean` is the overall mean rating over training data. Shrinkage
`+5` pulls low-count (user, genre) pairs toward 0.0 (no preference), and the
deviation-from-global-mean form makes it a *personalized* taste signal rather
than a raw rating average. Unseen (user, genre) pairs fall back to `0.0`.

Rationale: this injects the missing collaborative/personalization signal (the
root cause identified in the ideas) in a form the GBM's trees can consume
directly, without embedding training.

## Decision: leakage guard (train-fold-only affinity)

`user_genre_affinity` is computed from training folds only and mapped onto
validation/test rows by user key. This mirrors the existing leakage guard on the
four interaction statistics and prevents the model from seeing its own target
through the aggregate.

## Decision: the 24 cross terms (multiplicative interactions)

- 4 user-stat × item-stat: `um_x_im`, `um_x_ic`, `uc_x_im`, `uc_x_ic`.
- 1 demographic × item-attribute: `age_x_year` (age × release_year).
- 1 dot-product affinity score: `genre_affinity_score = sum_g affinity[g] × genre_item[g]`.
- 18 per-genre affinity × item-genre: `aff_x_genre_{g} = affinity[u,g] × genre_item[g]`.

These let the trees express "this user's taste meets this item" in a single
split, rather than requiring deep trees to discover it from additive inputs —
the core hypothesis of idea #4.

## Decision: add the 18 standalone affinity columns

`user_genre_affinity[g]` is added both as a standalone block (18 columns) and via
the cross terms. Standalone affinity lets the model use the taste signal
additively (e.g. a general affinity for a genre), while the cross terms expose
the multiplicative interactions.

Total features: 47 + 24 + 18 = 89.

## Decision: no scaling; skip demographic × item terms

No scaling/normalization — XGBoost is monotonic-scale invariant, so scaling
changes nothing. Demographic × item terms (age × item_mean_rating, age ×
item_rating_count, gender/occupation × item) are deliberately excluded to keep
the feature set focused on the hypothesized interaction class and to avoid
bloating an already 89-column matrix with low-signal terms.

## Decision: single ablation of cross terms, evaluated across four thresholds

One ablation run on the 89-feature matrix, using the same chronological
80/10/10 split, seed 42, and metrics as the prior notebook. The model is
trained + evaluated at each threshold `T ∈ {2, 3, 4, 5}`. Compare, at each T,
against:

1. the prior `test`-alias run `fdab1c40799f460db34a2ec60e8c9774` (v7) — the
   no-cross-terms pointwise XGBoost; and
2. the popularity baseline (top-10 by rating count).

Metrics: `precision@10` (primary), `recall@10` and `NDCG@10` (secondary). The
best threshold is selected by `precision@10` (ties broken by higher `NDCG@10`)
and reported explicitly.

## Decision: ranking evaluation semantics

For each test user and threshold T: relevant set = held-out items with
`rating >= T` (positive under T); candidate pool = full catalog minus
train-rated items; rank by predicted P(positive) descending; take top 10.
Exclude users with an empty relevant set from the mean (per T). This matches
the prior notebook so deltas are clean.

## Decision: MLflow `test` alias only

Log with tags `code_version` (git sha), `data_version` (data hash),
`intent=xgboost-user-item-cross-terms`, metrics `precision@10`/`recall@10`/
`NDCG@10` (per threshold, plus the identified best threshold), and register the
best-threshold model under `test`. No `Staging`/`Production` promotion at
this stage (that happens only after the human gate and `mle-engineer`
implementation).

## Rejected alternative

- **Latent-factor features (ALS/SVD embeddings) as the collaborative signal.**
  Rejected for this idea: `xgboost-user-item-cross-terms` is the
  *engineered*-cross-term hypothesis; learned latent factors are a separate
  higher-tier idea (`xgboost-latent-factors`). Mixing them here would confound
  which signal is responsible for the gain. The shrunk affinity feature gives a
  lightweight, interpretable collaborative signal without an embedding-training
  dependency.

- **Demographic × item cross terms (age × item_mean_rating, gender/occupation ×
  item).** Rejected: low expected signal, adds many columns with no clear
  hypothesis, and the plan explicitly excludes them.

- **Adding ranking objectives / hyperparameter tuning alongside the features.**
  Rejected: the ablation must isolate the feature change; altering the objective
  or tuning depth would break comparability with the prior run.
