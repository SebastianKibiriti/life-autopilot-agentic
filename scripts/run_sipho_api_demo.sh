#!/usr/bin/env bash
set -euo pipefail

# Real HTTP demo for the Sipho consumer story.
# Prerequisite: uvicorn is running on http://127.0.0.1:8001 and Gmail/Calendar
# environment variables are configured in that server terminal.

BASE_URL="${LIFE_AUTOPILOT_URL:-http://127.0.0.1:8001}"
STUDENT_ID="${LIFE_AUTOPILOT_STUDENT_ID:-sipho-demo}"
NOW="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
PICKUP="$(date -u -v+40M '+%Y-%m-%dT%H:%M:%SZ')"
URGENT_NOW="$(date -u -v+14M '+%Y-%m-%dT%H:%M:%SZ')"

echo "1/8 Seeding Sipho's planned supplier pickup via the API"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/calendar/sync" \
  -H 'Content-Type: application/json' \
  -d "{\"events\":[{\"id\":\"sipho-flour-pickup-demo\",\"summary\":\"Pick up imported flour from supplier\",\"location\":\"Engineering Building B\",\"start_time\":\"$PICKUP\"}]}"
echo

echo "2/6 Posting Sipho's current bakery location via the API"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/location" \
  -H 'Content-Type: application/json' \
  -d "{\"latitude\":-26.1929,\"longitude\":28.0305,\"accuracy_meters\":10,\"provider\":\"simulated\",\"captured_at\":\"$NOW\"}"
echo

echo "3/8 Evaluating as preparation time approaches (PREPARE notification)"
curl --fail-with-body -sS -X POST \
  "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW&student_has_started_moving=false"
echo

echo "4/8 Checking the first audit event"
curl --fail-with-body -sS "$BASE_URL/api/v1/students/$STUDENT_ID/events?limit=20"
echo

echo "5/8 Re-evaluating after the planned departure time (REPLAN urgency notification)"
curl --fail-with-body -sS -X POST \
  "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$URGENT_NOW&student_has_started_moving=false"
echo

echo "6/8 Simulating movement and asking the agent to re-evaluate (LEAVE notification)"
curl --fail-with-body -sS -X POST \
  "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$URGENT_NOW&student_has_started_moving=true"
echo

echo "7/8 Checking the complete action timeline"
curl --fail-with-body -sS "$BASE_URL/api/v1/students/$STUDENT_ID/events?limit=20"
echo

echo "8/8 Recording the observed preparation behavior"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/learn" \
  -H 'Content-Type: application/json' \
  -d "{\"actual_prep_minutes\":12,\"actual_start_moving_at\":\"$NOW\",\"destination_key\":\"default\"}"
echo

echo "Demo complete. Save the JSON responses and Gmail message as submission evidence."
