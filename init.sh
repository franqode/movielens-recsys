#!/usr/bin/env bash
set -euo pipefail

# MovieLens harness init: verify the harness is in a correct state.
# Run from the repo root. Needs python3 to validate feature_list.json.

FAIL=0

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found (needed to validate feature_list.json)"
  FAIL=1
fi

if [ ! -f feature_list.json ]; then
  echo "ERROR: feature_list.json missing"
  FAIL=1
fi

for d in memory specs progress docs .opencode/agents data/raw data/processed src/movielens/models app mlflow; do
  if [ ! -d "$d" ]; then
    echo "ERROR: missing directory '$d'"
    FAIL=1
  fi
done

if [ "$FAIL" -eq 0 ]; then
  python3 - <<'PY'
import json, sys
with open("feature_list.json") as f:
    data = json.load(f)
features = data.get("features", [])
allowed = {"pending", "spec_ready", "in_progress", "done"}
for feat in features:
    if feat.get("status") not in allowed:
        print("ERROR: bad status in feature", feat.get("id"), feat.get("status"))
        sys.exit(1)
    if feat.get("sdd") is None:
        print("ERROR: missing sdd flag in feature", feat.get("id"))
        sys.exit(1)
in_progress = [f["id"] for f in features if f.get("status") == "in_progress"]
if len(in_progress) > 1:
    print("ERROR: more than one feature in_progress:", in_progress)
    sys.exit(1)
print(f"OK: {len(features)} features, {len(in_progress)} in_progress")
PY
  [ $? -ne 0 ] && FAIL=1
fi

if [ "$FAIL" -ne 0 ]; then
  echo "Harness verification FAILED."
  exit 1
fi

echo "Harness OK. Open AGENTS.md and start from there."
