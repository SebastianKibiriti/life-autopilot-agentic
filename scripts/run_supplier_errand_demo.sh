#!/usr/bin/env bash
set -euo pipefail

# Separate scenario: autonomous monitoring of a planned client meeting.
BASE_URL="${LIFE_AUTOPILOT_URL:-http://127.0.0.1:8001}"
STUDENT_ID="${LIFE_AUTOPILOT_STUDENT_ID:-sipho-supplier-demo}"
RUN_ID="$(date -u '+%Y%m%d%H%M%S')"
COMMITMENT_ID="client-meeting-lakeside-${RUN_ID}"
WEATHER_OPTIONS=("clear skies, 22°C" "light rain, 17°C" "strong wind, 19°C")
TRAFFIC_OPTIONS=("light traffic" "moderate traffic, delays near the highway" "heavy traffic, approximately 15 minutes of delay")
WEATHER_OBSERVATION="${WEATHER_OBSERVATION:-${WEATHER_OPTIONS[$((RANDOM % ${#WEATHER_OPTIONS[@]}))]}}"
TRAFFIC_OBSERVATION="${TRAFFIC_OBSERVATION:-${TRAFFIC_OPTIONS[$((RANDOM % ${#TRAFFIC_OPTIONS[@]}))]}}"
export WEATHER_OBSERVATION TRAFFIC_OBSERVATION
# Fixed demonstration timeline

MEETING_AT="2026-09-01T10:00:00Z"

NOW="2026-09-01T08:00:00Z"          # T-2h
PREPARE_NOW="2026-09-01T09:00:00Z"  # T-1h
REPLAN_NOW="2026-09-01T09:45:00Z"   # T-15m
LEAVE_NOW="2026-09-01T09:50:00Z"    # T-10m

echo "Selected conditions: $WEATHER_OBSERVATION; $TRAFFIC_OBSERVATION"
echo "1/8 T-2 hours: importing the planned client meeting"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/calendar/sync" -H 'Content-Type: application/json' \
  -d "{\"events\":[{\"id\":\"$COMMITMENT_ID\",\"summary\":\"team meeting with client\",\"location\":\"Lakeside Office\",\"meeting_contact_email\":\"sebastiankib@icloud.com\",\"start_time\":\"$MEETING_AT\"}]}"
echo
echo "2/8 Creating the meeting in Google Calendar"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/calendar/actions" \
  -H 'Content-Type: application/json' \
  -d "{\"commitment_id\":\"$COMMITMENT_ID\",\"title\":\"team meeting with client\",\"start_time\":\"$MEETING_AT\",\"description\":\"Life Autopilot demo meeting at Lakeside Office. Contact: sebastiankib@icloud.com\"}"
echo
echo "3/7 Posting Sipho's fictional apartment-building home location"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/location" -H 'Content-Type: application/json' \
  -d "{\"latitude\":-26.1929,\"longitude\":28.0305,\"accuracy_meters\":10,\"provider\":\"simulated\",\"captured_at\":\"$NOW\"}"
echo
echo "4/8 T-2 hours: agent should stay silent (NO_ACTION)"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW&student_has_started_moving=false&weather_observation=$(printf '%s' "$WEATHER_OBSERVATION" | jq -sRr @uri)&traffic_observation=$(printf '%s' "$TRAFFIC_OBSERVATION" | jq -sRr @uri)"
echo
echo "5/8 T-1 hour: preparation window"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$PREPARE_NOW&student_has_started_moving=false&weather_observation=$(printf '%s' "$WEATHER_OBSERVATION" | jq -sRr @uri)&traffic_observation=$(printf '%s' "$TRAFFIC_OBSERVATION" | jq -sRr @uri)"
echo
echo "6/8 T-15 minutes: stationary user triggers REPLAN"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$REPLAN_NOW&student_has_started_moving=false&weather_observation=$(printf '%s' "$WEATHER_OBSERVATION" | jq -sRr @uri)&traffic_observation=$(printf '%s' "$TRAFFIC_OBSERVATION" | jq -sRr @uri)"
echo
echo "7/8 T-10 minutes: movement detected, agent says LEAVE"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$LEAVE_NOW&student_has_started_moving=true&weather_observation=$(printf '%s' "$WEATHER_OBSERVATION" | jq -sRr @uri)&traffic_observation=$(printf '%s' "$TRAFFIC_OBSERVATION" | jq -sRr @uri)"
echo
echo "8/8 Current audit timeline"
curl --fail-with-body -sS "$BASE_URL/api/v1/students/$STUDENT_ID/events?limit=20"
echo
