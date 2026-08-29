#!/usr/bin/env bash
set -euo pipefail

# Separate scenario: autonomous monitoring of a planned client meeting.
BASE_URL="${LIFE_AUTOPILOT_URL:-http://127.0.0.1:8001}"
STUDENT_ID="${LIFE_AUTOPILOT_STUDENT_ID:-sipho-supplier-demo}"
WEATHER_OPTIONS=("clear skies, 22°C" "light rain, 17°C" "strong wind, 19°C")
TRAFFIC_OPTIONS=("light traffic" "moderate traffic, delays near the highway" "heavy traffic, approximately 15 minutes of delay")
WEATHER_OBSERVATION="${WEATHER_OBSERVATION:-${WEATHER_OPTIONS[$((RANDOM % ${#WEATHER_OPTIONS[@]}))]}}"
TRAFFIC_OBSERVATION="${TRAFFIC_OBSERVATION:-${TRAFFIC_OPTIONS[$((RANDOM % ${#TRAFFIC_OPTIONS[@]}))]}}"
export WEATHER_OBSERVATION TRAFFIC_OBSERVATION
NOW="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
PICKUP="$(date -u -v+40M '+%Y-%m-%dT%H:%M:%SZ')"
URGENT_NOW="$(date -u -v+14M '+%Y-%m-%dT%H:%M:%SZ')"

echo "Selected conditions: $WEATHER_OBSERVATION; $TRAFFIC_OBSERVATION"
echo "1/6 Creating the planned 10:40 client meeting at Lakeside Office"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/calendar/sync" -H 'Content-Type: application/json' \
  -d "{\"events\":[{\"id\":\"client-meeting-lakeside\",\"summary\":\"10:40 team meeting with client\",\"location\":\"Lakeside Office\",\"meeting_contact_email\":\"sebastiankib@icloud.com\",\"start_time\":\"$PICKUP\"}]}"
echo
echo "2/6 Posting Sipho's fictional apartment-building home location"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/location" -H 'Content-Type: application/json' \
  -d "{\"latitude\":-26.1929,\"longitude\":28.0305,\"accuracy_meters\":10,\"provider\":\"simulated\",\"captured_at\":\"$NOW\"}"
echo
echo "3/6 Preparation window: agent advises preparation with weather and traffic context"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW&student_has_started_moving=false"
echo
echo "4/6 Missed departure: agent sends urgency/re-plan notification"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$URGENT_NOW&student_has_started_moving=false"
echo
echo "5/6 Movement detected: agent re-evaluates and advises leaving"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$URGENT_NOW&student_has_started_moving=true"
echo
echo "6/6 Complete audit timeline"
curl --fail-with-body -sS "$BASE_URL/api/v1/students/$STUDENT_ID/events?limit=20"
echo
