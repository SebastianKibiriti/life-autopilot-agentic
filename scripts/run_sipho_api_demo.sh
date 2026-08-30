#!/usr/bin/env bash
set -euo pipefail

# Real HTTP demo for the Sipho consumer story.
# Prerequisite: uvicorn is running on http://127.0.0.1:8001 and Gmail/Calendar
# environment variables are configured in that server terminal.

BASE_URL="${LIFE_AUTOPILOT_URL:-http://127.0.0.1:8001}"
STUDENT_ID="${LIFE_AUTOPILOT_STUDENT_ID:-sipho-demo}"
WEATHER_OBSERVATION="${WEATHER_OBSERVATION:-light rain, 17°C}"
TRAFFIC_OBSERVATION="${TRAFFIC_OBSERVATION:-moderate traffic, highway delays}"
NOW="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
LECTURE="$(date -u -v+60M '+%Y-%m-%dT%H:%M:%SZ')"

echo "1/6 Seeding Sipho's fictional lecture via the API"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/calendar/sync" \
  -H 'Content-Type: application/json' \
  -d "{\"events\":[{\"id\":\"sipho-entrepreneurship-demo\",\"summary\":\"Entrepreneurship lecture\",\"location\":\"Engineering Building B\",\"start_time\":\"$LECTURE\"}]}"
echo

echo "2/6 Posting Sipho's current bakery location via the API"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/location" \
  -H 'Content-Type: application/json' \
  -d "{\"latitude\":-26.1929,\"longitude\":28.0305,\"accuracy_meters\":10,\"provider\":\"simulated\",\"captured_at\":\"$NOW\"}"
echo

echo "3/6 Running autonomous evaluation (this may send Gmail)"
curl --fail-with-body -sS -X POST \
  "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW&student_has_started_moving=false&weather_observation=$(printf '%s' "$WEATHER_OBSERVATION" | jq -sRr @uri)&traffic_observation=$(printf '%s' "$TRAFFIC_OBSERVATION" | jq -sRr @uri)"
echo

echo "4/6 Checking the agent audit timeline"
curl --fail-with-body -sS "$BASE_URL/api/v1/students/$STUDENT_ID/events?limit=20"
echo

echo "5/6 Re-evaluating after Sipho starts moving"
curl --fail-with-body -sS -X POST \
  "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW&student_has_started_moving=true&weather_observation=$(printf '%s' "$WEATHER_OBSERVATION" | jq -sRr @uri)&traffic_observation=$(printf '%s' "$TRAFFIC_OBSERVATION" | jq -sRr @uri)"
echo

echo "6/6 Recording the observed preparation behavior"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/learn" \
  -H 'Content-Type: application/json' \
  -d "{\"actual_prep_minutes\":12,\"actual_start_moving_at\":\"$NOW\",\"destination_key\":\"default\"}"
echo

echo "Demo complete. Save the JSON responses and Gmail message as submission evidence."
