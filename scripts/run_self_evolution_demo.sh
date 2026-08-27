#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${LIFE_AUTOPILOT_URL:-http://127.0.0.1:8001}"
echo "1/5 Active policy"
curl --fail-with-body -sS "$BASE_URL/api/v1/agent/policy"; echo
echo "2/5 Evaluate golden scenarios"
RUN="$(curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/evaluations/run")"; echo "$RUN"
echo "3/5 Generate candidate proposal"
PROPOSAL="$(curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/evolution/proposals")"; echo "$PROPOSAL"
ID="$(printf '%s' "$PROPOSAL" | jq -r .proposal_id)"
echo "4/5 Explicitly promote the evaluated candidate"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/evolution/proposals/$ID/promote"; echo
echo "5/5 Active policy after promotion"
curl --fail-with-body -sS "$BASE_URL/api/v1/agent/policy"; echo
