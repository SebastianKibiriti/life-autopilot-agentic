#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# LIFE AUTOPILOT
# Autonomous Client Meeting Demonstration
#
# All demonstration timestamps are fixed.
# The backend receives UTC timestamps explicitly.
# No system clock is used for the simulated timeline.
#
# Scenario:
#   10:40 SAST client meeting
#   22-minute current fallback travel estimate
#
# Behavior demonstrated:
#   08:40 SAST  -> NO_ACTION
#   09:00 SAST  -> PREPARE
#   09:15 SAST  -> REPLAN
#                 User receives an informative warning.
#                 Client is NOT contacted.
#   09:20 SAST  -> LEAVE
#                 User is leaving while still expected to arrive early.
#                 Client is NOT contacted.
#   10:25 SAST  -> LEAVE
#                 ETA becomes 10:47 SAST.
#                 User is genuinely going to be late.
#                 Client receives courtesy notification.
# ============================================================

BASE_URL="${LIFE_AUTOPILOT_URL:-http://127.0.0.1:8001}"

# Explicit, stable demo namespace.
# Change this manually when a clean namespace is desired.
DEMO_RUN="${DEMO_RUN:-07}"

STUDENT_ID="${LIFE_AUTOPILOT_STUDENT_ID:-sipho-client-demo-${DEMO_RUN}}"
COMMITMENT_ID="client-meeting-lakeside-${DEMO_RUN}"

# ------------------------------------------------------------
# Fixed meeting
# ------------------------------------------------------------

MEETING_SAST="10:40"
MEETING_UTC="2026-09-01T08:40:00Z"

# ------------------------------------------------------------
# Fixed simulated timeline
# ------------------------------------------------------------

NOW_INITIAL="2026-09-01T06:40:00Z"
NOW_PREPARE="2026-09-01T07:00:00Z"
NOW_REPLAN="2026-09-01T07:15:00Z"
NOW_LEAVE="2026-09-01T07:20:00Z"

# The important late-arrival demonstration point.
#
# 10:25 SAST = 08:25 UTC
# 08:25 + 22 minutes = 08:47 UTC
# 08:47 UTC = 10:47 SAST
#
# Therefore the user is now genuinely expected to arrive
# seven minutes after the 10:40 SAST meeting.
NOW_LATE="2026-09-01T08:25:00Z"

# ------------------------------------------------------------
# Randomized environmental observations
#
# These are the only intentionally variable elements.
# ------------------------------------------------------------

WEATHER_OPTIONS=(
    "clear skies, 22°C"
    "light rain, 17°C"
    "strong wind, 19°C"
)

TRAFFIC_OPTIONS=(
    "light traffic"
    "moderate traffic, delays near the highway"
    "heavy traffic, approximately 15 minutes of delay"
)

WEATHER_OBSERVATION="${WEATHER_OBSERVATION:-${WEATHER_OPTIONS[$((RANDOM % ${#WEATHER_OPTIONS[@]}))]}}"
TRAFFIC_OBSERVATION="${TRAFFIC_OBSERVATION:-${TRAFFIC_OPTIONS[$((RANDOM % ${#TRAFFIC_OPTIONS[@]}))]}}"

export WEATHER_OBSERVATION
export TRAFFIC_OBSERVATION

# ------------------------------------------------------------
# URL encoding helper
# ------------------------------------------------------------

urlencode() {
    printf '%s' "$1" | jq -sRr @uri
}

WEATHER_ENCODED="$(urlencode "$WEATHER_OBSERVATION")"
TRAFFIC_ENCODED="$(urlencode "$TRAFFIC_OBSERVATION")"

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

echo
echo "============================================================"
echo "             LIFE AUTOPILOT DEMONSTRATION"
echo "============================================================"
echo
echo "Scenario:       Autonomous client meeting monitoring"
echo "Student:        Sipho"
echo "Meeting:        Team Meeting with Client"
echo "Destination:    Lakeside Office"
echo "Meeting time:   ${MEETING_SAST} AM SAST"
echo "Demo run:       ${DEMO_RUN}"
echo "Student ID:     ${STUDENT_ID}"
echo "Commitment ID:  ${COMMITMENT_ID}"
echo
echo "Environment:"
echo "  Weather:      ${WEATHER_OBSERVATION}"
echo "  Traffic:      ${TRAFFIC_OBSERVATION}"
echo
echo "Demo clock:"
echo "  Backend:      UTC"
echo "  Meeting:      ${MEETING_UTC}"
echo "  All evaluation times are predefined"
echo "  No live/system clock is used"
echo
echo "Simulated timeline:"
echo "  08:40 SAST    T-2 hours       NO_ACTION expected"
echo "  09:00 SAST    Preparation     PREPARE expected"
echo "  09:15 SAST    Leave threshold REPLAN expected"
echo "  09:20 SAST    Moving          LEAVE expected, on time"
echo "  10:25 SAST    Moving late     LEAVE expected, ETA 10:47"
echo "  10:40 SAST    Meeting"
echo
echo "============================================================"
echo

# ------------------------------------------------------------
# 1. Import planned meeting
# ------------------------------------------------------------

echo "1/8  Importing the planned client meeting"

curl --fail-with-body -sS \
    -X POST \
    "$BASE_URL/api/v1/students/$STUDENT_ID/calendar/sync" \
    -H 'Content-Type: application/json' \
    -d "{
        \"events\": [{
            \"id\": \"$COMMITMENT_ID\",
            \"summary\": \"Team Meeting with Client\",
            \"location\": \"Lakeside Office\",
            \"meeting_contact_email\": \"sebastiankib@icloud.com\",
            \"start_time\": \"$MEETING_UTC\"
        }]
    }"

echo
echo

# ------------------------------------------------------------
# 2. Create Google Calendar event
# ------------------------------------------------------------

echo "2/8  Creating the meeting in Google Calendar"

curl --fail-with-body -sS \
    -X POST \
    "$BASE_URL/api/v1/students/$STUDENT_ID/calendar/actions" \
    -H 'Content-Type: application/json' \
    -d "{
        \"commitment_id\": \"$COMMITMENT_ID\",
        \"title\": \"Team Meeting with Client\",
        \"start_time\": \"$MEETING_UTC\",
        \"description\": \"Life Autopilot demo meeting at Lakeside Office. Contact: sebastiankib@icloud.com\"
    }"

echo
echo

# ------------------------------------------------------------
# 3. Simulated home location
# ------------------------------------------------------------

echo "3/8  Posting Sipho's fictional apartment-building home location"

curl --fail-with-body -sS \
    -X POST \
    "$BASE_URL/api/v1/students/$STUDENT_ID/location" \
    -H 'Content-Type: application/json' \
    -d "{
        \"latitude\": -26.1929,
        \"longitude\": 28.0305,
        \"accuracy_meters\": 10,
        \"provider\": \"simulated\",
        \"captured_at\": \"$NOW_INITIAL\"
    }"

echo
echo

# ------------------------------------------------------------
# 4. Initial evaluation
# ------------------------------------------------------------

echo "4/8  Initial autonomous evaluation"
echo
echo "      Expected: NO_ACTION"
echo "      The commitment is still on track."

curl --fail-with-body -sS \
    -X POST \
    "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW_INITIAL&student_has_started_moving=false&weather_observation=$WEATHER_ENCODED&traffic_observation=$TRAFFIC_ENCODED"

echo
echo

# ------------------------------------------------------------
# 5. Preparation threshold
# ------------------------------------------------------------

echo "5/8  Preparation threshold"
echo
echo "      09:00 SAST / 07:00 UTC"
echo "      Expected: PREPARE"

curl --fail-with-body -sS \
    -X POST \
    "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW_PREPARE&student_has_started_moving=false&weather_observation=$WEATHER_ENCODED&traffic_observation=$TRAFFIC_ENCODED"

echo
echo

# ------------------------------------------------------------
# 6. Replan threshold
# ------------------------------------------------------------

echo "6/8  Leave threshold reached while stationary"
echo
echo "      09:15 SAST / 07:15 UTC"
echo "      Expected: REPLAN"
echo "      User is warned and given current travel context."
echo "      Client must NOT be contacted yet."

curl --fail-with-body -sS \
    -X POST \
    "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW_REPLAN&student_has_started_moving=false&weather_observation=$WEATHER_ENCODED&traffic_observation=$TRAFFIC_ENCODED"

echo
echo

# ------------------------------------------------------------
# 7. User starts moving
# ------------------------------------------------------------

echo "7/8  Movement detected after the leave threshold"
echo
echo "      09:20 SAST / 07:20 UTC"
echo "      Expected: LEAVE"
echo "      ETA with current route: 09:42 SAST"
echo "      Client must NOT be contacted because arrival is still early."

curl --fail-with-body -sS \
    -X POST \
    "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW_LEAVE&student_has_started_moving=true&weather_observation=$WEATHER_ENCODED&traffic_observation=$TRAFFIC_ENCODED"

echo
echo

# ------------------------------------------------------------
# 8. Late-arrival courtesy scenario
# ------------------------------------------------------------

echo "8/8  Late-arrival courtesy scenario"
echo
echo "      10:25 SAST / 08:25 UTC"
echo "      Current route estimate: 22 minutes"
echo "      Expected arrival: 10:47 SAST"
echo "      Meeting: 10:40 SAST"
echo
echo "      Expected: LEAVE"
echo "      User is now genuinely late."
echo "      Client SHOULD receive a courtesy notification."

curl --fail-with-body -sS \
    -X POST \
    "$BASE_URL/api/v1/students/$STUDENT_ID/autonomous-cycle?now=$NOW_LATE&student_has_started_moving=true&weather_observation=$WEATHER_ENCODED&traffic_observation=$TRAFFIC_ENCODED"

echo
echo

# ------------------------------------------------------------
# Audit timeline
# ------------------------------------------------------------

echo "============================================================"
echo "             CURRENT AUTONOMOUS AUDIT TIMELINE"
echo "============================================================"

curl --fail-with-body -sS \
    "$BASE_URL/api/v1/students/$STUDENT_ID/events?limit=20"

echo
echo
echo "============================================================"
echo "             DEMONSTRATION COMPLETE"
echo "============================================================"
echo
echo "Meeting:             10:40 AM SAST"
echo "Backend time:        UTC"
echo "Demo namespace:      $STUDENT_ID"
echo "Route provider:      backend fallback"
echo
echo "Expected behavior:"
echo "  08:40  NO_ACTION"
echo "  09:00  PREPARE"
echo "  09:15  REPLAN → user notified, client NOT contacted"
echo "  09:20  LEAVE   → user notified, client NOT contacted"
echo "  10:25  LEAVE   → ETA 10:47, client notified"
echo
echo "The backend calculated the departure thresholds."
echo "The demonstration timeline was completely predefined."
echo "Weather and traffic were randomly selected."
echo "No live/system clock was used by the demo."
echo
echo "============================================================"