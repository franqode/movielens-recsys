# Design — xgboost-user-item-cross-terms (retrain at threshold >= 2)

Technical decisions for assembling the validation notebook. The notebook is
self-contained (all logic inline, no `src/` split) and re-trains the
`xgboost-user-item-cross-terms` model with a SINGLE fixed cutoff `rating >= 2`,
validated under the MLflow `test` alias.

## Decision: single fixed threshold `rating >= 2` (no sweep)

Keep ALL ratings in `{1, 2, 3, 4, 5}`, form one binary label
`label = 1 if rating >= 2 else 0` (`1 -> 0`; `2, 3, 4, 5 -> 1`), and train a
single pointwise classifier. This replaces the prior threshold sweep
`T ∈ {2, 3, 4, 5}` with the single fixed cutoff `2` per the human's directive.

Rationale: the human fixed the positive-label cutoff at `>= 2`. There is no
sweep, no "best threshold" selection, and no per-threshold table — one model at
one threshold. The label is heavily imbalanced: `rating >= 2` covers roughly 94%
of ratings (positive), leaving `rating == 1` as the ≈6% negative class, so
`scale_pos_weight` is set once to the negative/positive ratio (≈0.064) and logged.

## Decision: the 89 features (unchanged from the prior cross-terms run)

The feature set is identical to the prior `xgboost-user-item-cross-terms`
run — the threshold change does not touch features:

1. **47 base tabular features**: user (age, gender one-hot, occupation one-hot),
   item (genres multi-hot over 18 genres, release_year), and interaction
   (user_mean_rating, item_mean_rating, user_rating_count, item_rating_count),
   with the four interaction stats computed on training folds only (leakage
   guard).
2. **18 standalone `user_genre_affinity[g]`**: shrunk mean-rating deviation
   `affinity[u,g] = (sum(rating - global_mean)) / (count_u,g + 5)`, train-fold
   only, fallback `0.0` for unseen (user, genre).
3. **24 cross terms**: `um_x_im`, `um_x_ic`, `uc_x_im`, `uc_x_ic`, `age_x_year`,
   `genre_affinity_score` (dot product), and 18 `aff_x_genre_{g}`.

Total: 47 + 18 + 24 = 89. No scaling (XGBoost is monotonic-scale invariant);
no demographic × item terms.

## Decision: chronological 80/10/10 split, relevance at `>= 2`

Same chronological (time-ordered) global 80/10/10 train/validation/test split,
seed 42. Ranking evaluation relevance now matches the new cutoff: for each test
user the relevant set is held-out items with `rating >= 2`; the candidate pool is
the full catalog minus the user's train-rated items; candidates are ranked by
predicted P(positive) descending and the top 10 taken. Users with an empty
relevant set are excluded from the mean.

## Decision: evaluation with NO baseline and NO prior-run comparison

The single evaluation is the model's own `precision@10` (primary), `recall@10`,
and `NDCG@10` (secondary), mean over included test users. There is NO popularity
baseline (deleted by directive) and NO comparison to any prior `test`-alias run
(prior versions deleted). The notebook reports only the model's three metrics at
the fixed threshold `>= 2`, plus feature importance for interpretability.

## Decision: MLflow `test` alias in registry `xgboost-v1`

Log metrics `precision@10`/`recall@10`/`NDCG@10` and the model artifact; register
the model in the `xgboost-v1` registry under the `test` alias (no
`Staging`/`Production` at this stage). Tags: `code_version` (git sha),
`data_version` (data hash), `intent=xgboost-user-item-cross-terms-gte2`. Record
the run in `memory/xgboost/experiments.md`.

## Rejected alternative

- **Keeping the four-threshold sweep `T ∈ {2, 3, 4, 5}` and selecting a best
  threshold.** Rejected: the human's directive fixes the cutoff to a single
  `>= 2`; sweeping and selecting would contradict the instruction and add
  unrequested model variants.

- **Retaining the popularity baseline.** Rejected: the human deleted the
  popularity model and directed that no popularity baseline be used going
  forward. The spec therefore excludes it entirely.

- **Comparing against the prior `test`-alias run (v7/v8).** Rejected: those
  prior MLflow versions were deleted by directive, so there is no stable prior
  run to compare against; the retrained run stands alone.
