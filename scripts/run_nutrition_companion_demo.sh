#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${LIFE_AUTOPILOT_URL:-http://127.0.0.1:8001}"
STUDENT_ID="${LIFE_AUTOPILOT_STUDENT_ID:-nutrition-student-demo}"
CLASS="$(date -u -v+3d '+%Y-%m-%dT14:00:00Z')"
FITNESS="$(date -u -v+2d '+%Y-%m-%dT17:30:00Z')"

echo "1/6 Saving learned student preferences (Firestore when enabled)"
curl --fail-with-body -sS -X PUT "$BASE_URL/api/v1/students/$STUDENT_ID/companion/profile" -H 'Content-Type: application/json' \
  -d '{"interests":["nutrition","fitness"],"preferred_activities":["cycling","outdoor training"],"accepted_suggestions":["outdoor activity"],"rejected_suggestions":["gym promotion"]}'
echo
echo "2/6 Resolving a timetable classroom through the curated campus graph"
curl --fail-with-body -sS "$BASE_URL/api/v1/campus/resolve?query=N204"
echo
echo "3/6 Importing nutrition timetable and fitness calendar events"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/calendar/sync" -H 'Content-Type: application/json' \
  -d "{\"events\":[{\"id\":\"nutrition-class\",\"summary\":\"Clinical Nutrition\",\"location\":\"N204\",\"start_time\":\"$CLASS\"},{\"id\":\"fitness-event\",\"summary\":\"Cycling training\",\"location\":\"Campus Cycling Track\",\"start_time\":\"$FITNESS\"}]}"
echo
echo "4/6 Self-initiating a personalized multi-option fitness suggestion"
SUGGESTION="$(curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/companion/fitness-suggestion")"
echo "$SUGGESTION"
SUGGESTION_ID="$(printf '%s' "$SUGGESTION" | jq -r .id)"
echo "5/6 Answering a follow-up from stored suggestion memory (no new Gemini call)"
curl --fail-with-body -sS "$BASE_URL/api/v1/students/$STUDENT_ID/companion/suggestions/$SUGGESTION_ID/follow-up?question=what%20are%20the%20alternatives"
echo
echo "6/6 Saving the selected suggestion to Google Calendar"
SAVE_AT="$(date -u -v+2d '+%Y-%m-%dT18:00:00Z')"
curl --fail-with-body -sS -X POST "$BASE_URL/api/v1/students/$STUDENT_ID/companion/suggestions/$SUGGESTION_ID/calendar" -H 'Content-Type: application/json' -d "{\"start_time\":\"$SAVE_AT\"}"
echo
