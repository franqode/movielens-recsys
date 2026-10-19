# Ideas — ncf

- id: ncf-demographics-coldstart
  hypothesis: NCF with user demographic features (age/occupation/gender)
    beats plain NCF on NDCG@10 for low-activity users (bottom quartile by
    rating count), where interaction history is sparse.
  evidence: Demographics are ~100% populated (6,040 users, no nulls); per-user
    rating counts are long-tailed (median 96, min 20), so many users have too
    little history for pure collaborative signal.
  status: proposed
