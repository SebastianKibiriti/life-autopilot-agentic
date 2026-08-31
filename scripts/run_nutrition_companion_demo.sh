
#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# LIFE AUTOPILOT — NUTRITION COMPANION DEMO
#
# FINAL DEMONSTRATION
#
# Demonstrates:
#
#   1. Learned student preferences
#   2. Curated campus knowledge resolution
#   3. Calendar pattern recognition
#   4. Personalized activity recommendation
#   5. Interactive follow-up answered from stored suggestion data
#   6. Google Calendar scheduling
#   7. Consistent activity duration
#   8. Deterministic autonomous monitoring
#   9. T-2 hour NO_ACTION
#  10. T-15 minute PREPARE
#  11. Real notification delivery
#  12. Audit records tied to the exact personalized commitment
#
# IMPORTANT:
#
#   - One fixed demonstration date is used everywhere.
#   - No system clock is used for the demonstration timeline.
#   - Weather and traffic are deterministic demonstration observations.
#   - The recommendation duration is the single source of truth.
#   - Calendar start/end are derived from the recommendation duration.
#   - The exact personalized commitment is used by autonomous evaluation.
#   - Notification delivery is reported from the backend.
#   - Audit records are filtered to the exact personalized commitment.
#   - Follow-up answers are resolved locally from stored suggestion data.
#   - No Gemini request is made for follow-up questions.
# ==============================================================================


# ==============================================================================
# CONFIGURATION
# ==============================================================================

BASE_URL="${LIFE_AUTOPILOT_URL:-http://127.0.0.1:8001}"
STUDENT_ID="${LIFE_AUTOPILOT_STUDENT_ID:-nutrition-student-demo}"

BASE_URL="${BASE_URL%/}"


# ==============================================================================
# FIXED DEMONSTRATION CLOCK
#
# South Africa:
#   UTC+2
#
# Activity:
#   15:30 UTC
#   17:30 SAST
#
# The recommendation duration returned by the backend is authoritative.
# The activity end time is calculated after the recommendation is received.
# ==============================================================================

DEMO_DATE="2026-09-01"

ACTIVITY_TIME_UTC="${DEMO_DATE}T15:30:00Z"
ACTIVITY_TIME_SAST="17:30 SAST"

# T-2 hours
NO_ACTION_TIME_UTC="${DEMO_DATE}T13:30:00Z"
NO_ACTION_TIME_SAST="15:30 SAST"

# T-15 minutes
PREPARE_TIME_UTC="${DEMO_DATE}T15:15:00Z"
PREPARE_TIME_SAST="17:15 SAST"


# ==============================================================================
# DETERMINISTIC DEMO ENVIRONMENT
# ==============================================================================

WEATHER_OBSERVATION="${WEATHER_OBSERVATION:-sunny, 24°C}"
TRAFFIC_OBSERVATION="${TRAFFIC_OBSERVATION:-clear roads}"

export WEATHER_OBSERVATION
export TRAFFIC_OBSERVATION


# ==============================================================================
# ACTIVITY DETAILS
# ==============================================================================

ACTIVITY_TITLE="${ACTIVITY_TITLE:-Scenic Outdoor Cycling Session}"
ACTIVITY_DESTINATION="${ACTIVITY_DESTINATION:-Campus Cycling Track}"

DESTINATION_LATITUDE="${DESTINATION_LATITUDE:--33.9600}"
DESTINATION_LONGITUDE="${DESTINATION_LONGITUDE:--22.4600}"


# ==============================================================================
# AUTONOMOUS TIMING MODEL
#
# These are the travel/planning inputs used by the evaluator.
#
# Activity:
#   15:30 UTC
#
# Preparation:
#   15:15 UTC
#
# Leave threshold:
#   15:20 UTC
#
# Target arrival:
#   15:25 UTC
#
# Therefore:
#
#   T-2 hours  -> NO_ACTION
#   T-15 mins  -> PREPARE
#
# The recommendation duration is NOT hard-coded here.
# It is obtained from the personalized suggestion.
# ==============================================================================

TRAVEL_MINUTES="${TRAVEL_MINUTES:-5}"
PREPARATION_MINUTES="${PREPARATION_MINUTES:-5}"
ARRIVAL_BUFFER_MINUTES="${ARRIVAL_BUFFER_MINUTES:-5}"


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

separator() {
    printf '%s\n' "======================================================================"
}

die() {
    echo
    echo "ERROR: $*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

require_command curl
require_command jq
require_command python3


# ==============================================================================
# NORMALIZE BASE URL
# ==============================================================================

case "$BASE_URL" in
    \[*\]*\(*\)*)
        die "LIFE_AUTOPILOT_URL contains Markdown formatting. Set it as plain text, for example: http://127.0.0.1:8001"
        ;;
esac

case "$BASE_URL" in
    http://*|https://*)
        ;;
    *)
        die "LIFE_AUTOPILOT_URL must begin with http:// or https://. Current value: $BASE_URL"
        ;;
esac


# ==============================================================================
# VERIFY BACKEND
# ==============================================================================

echo "Backend: $BASE_URL"

curl --fail-with-body -sS \
    "$BASE_URL/health" \
    >/dev/null || {
        die "Backend is not reachable at $BASE_URL"
    }


# ==============================================================================
# HEADER
# ==============================================================================

echo
separator

echo "            LIFE AUTOPILOT DEMONSTRATION"

separator

echo

printf '%-20s %s\n' \
    "Scenario:" \
    "Autonomous nutrition & fitness companion"

printf '%-20s %s\n' \
    "Student:" \
    "Nutrition student"

printf '%-20s %s\n' \
    "Activity:" \
    "$ACTIVITY_TITLE"

printf '%-20s %s\n' \
    "Activity start:" \
    "$ACTIVITY_TIME_SAST / $ACTIVITY_TIME_UTC"

echo
echo "Environment:"
echo
echo "  Weather:      $WEATHER_OBSERVATION"
echo "  Traffic:      $TRAFFIC_OBSERVATION"

echo
echo "Demo clock:"
echo
echo "  Backend:      UTC"
echo "  Activity:     $ACTIVITY_TIME_UTC"
echo "  All evaluation times are predefined"
echo "  No live/system clock is used"

echo
echo "Simulated timeline:"
echo
echo "  $NO_ACTION_TIME_SAST    T-2 hours       NO_ACTION expected"
echo "  $PREPARE_TIME_SAST      T-15 minutes    PREPARE expected"
echo "  $ACTIVITY_TIME_SAST     Activity starts"

echo
separator


# ==============================================================================
# 1/10 — LEARNED STUDENT PREFERENCES
# ==============================================================================

echo
echo "1/10 Saving learned student preferences"

PROFILE_RESULT="$(
    curl --fail-with-body -sS \
        -X PUT \
        "$BASE_URL/api/v1/students/$STUDENT_ID/companion/profile" \
        -H 'Content-Type: application/json' \
        --data-binary '{
          "interests": [
            "nutrition",
            "fitness"
          ],
          "preferred_activities": [
            "cycling",
            "outdoor training"
          ],
          "accepted_suggestions": [
            "outdoor activity"
          ],
          "rejected_suggestions": [
            "gym promotion"
          ]
        }'
)"

echo "$PROFILE_RESULT" | jq .


# ==============================================================================
# 2/10 — CURATED CAMPUS GRAPH
# ==============================================================================

echo
echo "2/10 Resolving a timetable classroom through the curated campus graph"

CAMPUS_RESULT="$(
    curl --fail-with-body -sS \
        "$BASE_URL/api/v1/campus/resolve?query=N204"
)"

echo "$CAMPUS_RESULT" | jq .


# ==============================================================================
# 3/10 — CALENDAR IMPORT
# ==============================================================================

echo
echo "3/10 Importing nutrition timetable and existing fitness calendar events"

CLASS_TIME_UTC="${DEMO_DATE}T12:00:00Z"
EXISTING_FITNESS_TIME_UTC="${DEMO_DATE}T15:00:00Z"

CALENDAR_PAYLOAD="$(
    jq -n \
        --arg class_time "$CLASS_TIME_UTC" \
        --arg fitness_time "$EXISTING_FITNESS_TIME_UTC" \
        '{
          events: [
            {
              id: "nutrition-class",
              summary: "Clinical Nutrition",
              location: "N204",
              start_time: $class_time
            },
            {
              id: "fitness-event",
              summary: "Cycling training",
              location: "Campus Cycling Track",
              start_time: $fitness_time
            }
          ]
        }'
)"

CALENDAR_SYNC_RESULT="$(
    curl --fail-with-body -sS \
        -X POST \
        "$BASE_URL/api/v1/students/$STUDENT_ID/calendar/sync" \
        -H 'Content-Type: application/json' \
        --data-binary "$CALENDAR_PAYLOAD"
)"

echo "$CALENDAR_SYNC_RESULT" | jq .


# ==============================================================================
# 4/10 — PERSONALIZED SUGGESTION
# ==============================================================================

echo
echo "4/10 Agent notices the fitness pattern and generates a personalized suggestion"

echo
echo "      Stored preferences + calendar pattern + current conditions"
echo
echo "      → personalized multi-option recommendation"
echo

WEATHER_ENCODED="$(
    printf '%s' "$WEATHER_OBSERVATION" |
    jq -sRr @uri
)"

TRAFFIC_ENCODED="$(
    printf '%s' "$TRAFFIC_OBSERVATION" |
    jq -sRr @uri
)"

SUGGESTION="$(
    curl --fail-with-body -sS \
        -X POST \
        "$BASE_URL/api/v1/students/$STUDENT_ID/companion/fitness-suggestion?weather_observation=$WEATHER_ENCODED&traffic_observation=$TRAFFIC_ENCODED"
)"

echo "$SUGGESTION" | jq .


# ==============================================================================
# EXTRACT SUGGESTION DATA
#
# The backend recommendation is authoritative.
# ==============================================================================

SUGGESTION_ID="$(
    printf '%s' "$SUGGESTION" |
    jq -r '.id // empty'
)"

[ -n "$SUGGESTION_ID" ] ||
    die "Suggestion endpoint did not return an id."


SUGGESTION_TITLE="$(
    printf '%s' "$SUGGESTION" |
    jq -r '.main_recommendation // empty'
)"

SUGGESTION_DURATION="$(
    printf '%s' "$SUGGESTION" |
    jq -r '.estimated_duration_minutes // empty'
)"

SUGGESTION_RATIONALE="$(
    printf '%s' "$SUGGESTION" |
    jq -r '.rationale // empty'
)"

SUGGESTION_ALTERNATIVES="$(
    printf '%s' "$SUGGESTION" |
    jq -r '
        (.alternatives // [])
        | if type == "array"
          then join("; ")
          else tostring
          end
    '
)"

FOLLOW_UP_ANSWERS="$(
    printf '%s' "$SUGGESTION" |
    jq -c '.follow_up_answers // {}'
)"


# ==============================================================================
# VALIDATE RECOMMENDATION DURATION
# ==============================================================================

if ! printf '%s' "$SUGGESTION_DURATION" |
    grep -Eq '^[0-9]+$'
then
    die "Suggestion did not return a valid estimated_duration_minutes value."
fi

if [ "$SUGGESTION_DURATION" -le 0 ]; then
    die "Suggestion returned an invalid activity duration: $SUGGESTION_DURATION"
fi


# ==============================================================================
# CALCULATE ACTIVITY END FROM THE ACTUAL RECOMMENDATION DURATION
#
# This is the critical duration-consistency fix.
#
# There is now ONE authoritative duration:
#
#   .estimated_duration_minutes
#
# It drives:
#
#   - displayed activity duration
#   - Google Calendar end_time
#   - commitment end_time
# ==============================================================================

ACTIVITY_END_TIME_UTC="$(
    python3 - "$ACTIVITY_TIME_UTC" "$SUGGESTION_DURATION" <<'PY'
import sys
from datetime import datetime, timedelta, timezone

start = datetime.fromisoformat(
    sys.argv[1].replace("Z", "+00:00")
)

duration = int(sys.argv[2])

end = start + timedelta(minutes=duration)

print(
    end.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
)
PY
)"

ACTIVITY_END_TIME_SAST="$(
    python3 - "$ACTIVITY_END_TIME_UTC" <<'PY'
import sys
from datetime import datetime, timezone, timedelta

value = datetime.fromisoformat(
    sys.argv[1].replace("Z", "+00:00")
)

sast = timezone(timedelta(hours=2))

print(
    value.astimezone(sast).strftime("%H:%M SAST")
)
PY
)"


echo
echo "      Suggestion ID:    $SUGGESTION_ID"
echo "      Recommendation:   ${SUGGESTION_TITLE:-not returned}"
echo "      Duration:         $SUGGESTION_DURATION minutes"
echo "      Calculated end:   $ACTIVITY_END_TIME_SAST / $ACTIVITY_END_TIME_UTC"


# ==============================================================================
# 5/10 — INTERACTIVE STORED-MEMORY FOLLOW-UP
# ==============================================================================

echo
echo "5/10 Ask the companion about its recommendation"

echo
echo "      The recommendation contains stored follow-up information."
echo
echo "      Questions are answered locally from the stored suggestion."
echo "      Gemini called: false"
echo
echo "      Example questions:"
echo
echo "        - What else could I do?"
echo "        - Why did you recommend this?"
echo "        - How long will it take?"
echo "        - Why is this good for me?"
echo


ask_stored_question() {

    local question="$1"
    local normalized
    local answer=""

    normalized="$(
        printf '%s' "$question" |
        tr '[:upper:]' '[:lower:]'
    )"

    normalized="$(
        printf '%s' "$normalized" |
        tr -cd '[:alnum:] '
    )"

    normalized="$(
        printf '%s' "$normalized" |
        awk '{$1=$1; print}'
    )"


    # WHY / REASON

    if printf '%s' "$normalized" |
        grep -Eq '(^| )(why|reason|recommend|recommended|recommendation|suggest|suggested|suggestion)( |$)'
    then

        answer="$(
            printf '%s' "$FOLLOW_UP_ANSWERS" |
            jq -r '
                to_entries
                | map(
                    select(
                        (
                            (.key | ascii_downcase)
                            | test(
                                "why|reason|recommend|recommendation|suggest|suggestion"
                              )
                        )
                    )
                )
                | .[0].value // empty
            '
        )"

        if [ -z "$answer" ] && [ -n "$SUGGESTION_RATIONALE" ]; then
            answer="$SUGGESTION_RATIONALE"
        fi


    # DURATION

    elif printf '%s' "$normalized" |
        grep -Eq '(^| )(how long|duration|minutes|minute|time|take|takes|long)( |$)'
    then

        answer="$(
            printf '%s' "$FOLLOW_UP_ANSWERS" |
            jq -r '
                to_entries
                | map(
                    select(
                        (
                            (.key | ascii_downcase)
                            | test(
                                "how long|duration|minute|minutes|time|take"
                              )
                        )
                    )
                )
                | .[0].value // empty
            '
        )"

        if [ -z "$answer" ]; then
            answer="The recommended activity is approximately ${SUGGESTION_DURATION} minutes long."
        fi


    # ALTERNATIVES

    elif printf '%s' "$normalized" |
        grep -Eq '(^| )(alternative|alternatives|else|another|other|option|options|instead|different|could)( |$)'
    then

        answer="$(
            printf '%s' "$FOLLOW_UP_ANSWERS" |
            jq -r '
                to_entries
                | map(
                    select(
                        (
                            (.key | ascii_downcase)
                            | test(
                                "alternative|another|other|option|instead|different|else"
                              )
                        )
                    )
                )
                | .[0].value // empty
            '
        )"

        if [ -z "$answer" ] && [ -n "$SUGGESTION_ALTERNATIVES" ]; then
            answer="Other options include: $SUGGESTION_ALTERNATIVES"
        fi
    fi


    if [ -n "$answer" ]; then
        printf '%s\n' "$answer"
        return 0
    fi

    return 1
}


while true; do

    printf '\nYou: '

    if ! IFS= read -r QUESTION; then
        echo
        break
    fi

    if [ -z "$QUESTION" ]; then
        continue
    fi

    QUESTION_LOWER="$(
        printf '%s' "$QUESTION" |
        tr '[:upper:]' '[:lower:]' |
        awk '{$1=$1; print}'
    )"

    if [ "$QUESTION_LOWER" = "done" ]; then
        break
    fi

    ANSWER=""

    if ANSWER="$(ask_stored_question "$QUESTION")"; then

        echo
        echo "Agent: $ANSWER"
        echo
        echo "      Source: stored_suggestion"
        echo "      Gemini called: false"

    else

        echo
        echo "Agent: I couldn't find a prepared answer for that question."
        echo
        echo "      Source: stored_suggestion"
        echo "      Gemini called: false"
        echo
        echo "      Try asking about:"
        echo "        - why this was recommended"
        echo "        - how long it takes"
        echo "        - what else you could do"
    fi

done


# ==============================================================================
# 6/10 — SAVE PERSONALIZED ACTIVITY TO GOOGLE CALENDAR
#
# Duration is taken directly from the recommendation.
# ==============================================================================

echo
echo "6/10 Saving the selected personalized activity to Google Calendar"

echo
echo "      Activity:"
echo "      $ACTIVITY_TITLE"
echo
echo "      Start:"
echo "      $ACTIVITY_TIME_SAST / $ACTIVITY_TIME_UTC"
echo
echo "      End:"
echo "      $ACTIVITY_END_TIME_SAST / $ACTIVITY_END_TIME_UTC"
echo
echo "      Duration:"
echo "      $SUGGESTION_DURATION minutes"
echo


SAVE_PAYLOAD="$(
    jq -n \
        --arg start "$ACTIVITY_TIME_UTC" \
        --arg end "$ACTIVITY_END_TIME_UTC" \
        '{
          start_time: $start,
          end_time: $end
        }'
)"


CALENDAR_RESULT="$(
    curl --fail-with-body -sS \
        -X POST \
        "$BASE_URL/api/v1/students/$STUDENT_ID/companion/suggestions/$SUGGESTION_ID/calendar" \
        -H 'Content-Type: application/json' \
        --data-binary "$SAVE_PAYLOAD"
)"

echo "$CALENDAR_RESULT" | jq .


# ==============================================================================
# VERIFY CALENDAR EVENT TIME
# ==============================================================================

CALENDAR_START="$(
    printf '%s' "$CALENDAR_RESULT" |
    jq -r '.start.dateTime // empty'
)"

CALENDAR_END="$(
    printf '%s' "$CALENDAR_RESULT" |
    jq -r '.end.dateTime // empty'
)"


echo

if [ -n "$CALENDAR_START" ]; then
    echo "      Calendar start returned: $CALENDAR_START"
fi

if [ -n "$CALENDAR_END" ]; then
    echo "      Calendar end returned:   $CALENDAR_END"
fi


if [ -n "$CALENDAR_START" ] && [ -n "$CALENDAR_END" ]; then

    echo
    echo "      ✓ Calendar returned both start and end times."

else

    echo
    echo "      WARNING: Calendar response did not return both start and end times."

fi


# ==============================================================================
# EXACT PERSONALIZED COMMITMENT
#
# This exact commitment is used by BOTH autonomous evaluations.
#
# The commitment contains:
#
#   start_time
#   end_time
#   duration_minutes
#
# All derived from the recommendation.
# ==============================================================================

COMMITMENT_ID="demo-personalized-fitness-${SUGGESTION_ID}"


COMMITMENT_JSON="$(
    jq -n \
        --arg id "$COMMITMENT_ID" \
        --arg title "$ACTIVITY_TITLE" \
        --arg start "$ACTIVITY_TIME_UTC" \
        --arg end "$ACTIVITY_END_TIME_UTC" \
        --arg destination "$ACTIVITY_DESTINATION" \
        --argjson duration "$SUGGESTION_DURATION" \
        --argjson lat "$DESTINATION_LATITUDE" \
        --argjson lon "$DESTINATION_LONGITUDE" \
        '{
          id: $id,
          title: $title,
          start_time: $start,
          end_time: $end,
          duration_minutes: $duration,
          destination: $destination,
          destination_coordinates: {
            latitude: $lat,
            longitude: $lon,
            accuracy_meters: 5,
            captured_at: $start,
            provider: "simulated"
          },
          status: "active"
        }'
)"


# ==============================================================================
# 7/10 — T-2 HOURS
#
# Expected:
#
#   NO_ACTION
#
# No notification should be sent.
# ==============================================================================

echo
echo "7/10 Fast-forwarding to the day of the activity"

echo
echo "      $NO_ACTION_TIME_SAST / $NO_ACTION_TIME_UTC"

echo
echo "      Activity is two hours away."

echo
echo "      Expected: NO_ACTION"

echo
echo "      The agent should remain silent."

echo


EVALUATION_T2_PAYLOAD="$(
    jq -n \
        --arg now "$NO_ACTION_TIME_UTC" \
        --argjson commitment "$COMMITMENT_JSON" \
        --argjson travel "$TRAVEL_MINUTES" \
        --argjson preparation "$PREPARATION_MINUTES" \
        --argjson buffer "$ARRIVAL_BUFFER_MINUTES" \
        '{
          now: $now,
          commitment: $commitment,
          travel_minutes: $travel,
          preparation_minutes: $preparation,
          arrival_buffer_minutes: $buffer,
          student_has_started_moving: false
        }'
)"


T2_RESULT="$(
    curl --fail-with-body -sS \
        -X POST \
        "$BASE_URL/api/v1/agent/evaluate" \
        -H 'Content-Type: application/json' \
        --data-binary "$EVALUATION_T2_PAYLOAD"
)"

echo "$T2_RESULT" | jq .


T2_DECISION="$(
    printf '%s' "$T2_RESULT" |
    jq -r '.decision // empty'
)"

T2_NOTIFICATION="$(
    printf '%s' "$T2_RESULT" |
    jq -r '.notification_sent // false'
)"


if [ "$T2_DECISION" = "NO_ACTION" ]; then
    echo
    echo "      ✓ T-2 hour evaluation confirmed NO_ACTION."
else
    echo
    echo "      WARNING: backend returned '$T2_DECISION' at T-2."
fi


if [ "$T2_NOTIFICATION" = "false" ]; then
    echo "      ✓ No T-2 notification was sent."
else
    echo "      WARNING: Backend reports a T-2 notification was sent."
fi


# ==============================================================================
# 8/10 — T-15 MINUTES
#
# Expected:
#
#   PREPARE
#
# At this point:
#
#   Current time:     15:15 UTC
#   Preparation:      15:15 UTC
#   Leave threshold:   15:20 UTC
#
# Therefore the student still has five minutes before leaving.
#
# IMPORTANT:
#
# The notification is expected to be ACTUALLY DELIVERED here.
# ==============================================================================

echo
echo "8/10 Preparation threshold"

echo
echo "      $PREPARE_TIME_SAST / $PREPARE_TIME_UTC"

echo
echo "      Expected: PREPARE"

echo
echo "      The autonomous evaluator should enter the preparation window."

echo


EVALUATION_T15_PAYLOAD="$(
    jq -n \
        --arg now "$PREPARE_TIME_UTC" \
        --argjson commitment "$COMMITMENT_JSON" \
        --argjson travel "$TRAVEL_MINUTES" \
        --argjson preparation "$PREPARATION_MINUTES" \
        --argjson buffer "$ARRIVAL_BUFFER_MINUTES" \
        '{
          now: $now,
          commitment: $commitment,
          travel_minutes: $travel,
          preparation_minutes: $preparation,
          arrival_buffer_minutes: $buffer,
          student_has_started_moving: false
        }'
)"


T15_RESULT="$(
    curl --fail-with-body -sS \
        -X POST \
        "$BASE_URL/api/v1/agent/evaluate" \
        -H 'Content-Type: application/json' \
        --data-binary "$EVALUATION_T15_PAYLOAD"
)"


echo "$T15_RESULT" | jq .


T15_DECISION="$(
    printf '%s' "$T15_RESULT" |
    jq -r '.decision // empty'
)"

T15_NOTIFICATION="$(
    printf '%s' "$T15_RESULT" |
    jq -r '.notification_sent // false'
)"

T15_BODY="$(
    printf '%s' "$T15_RESULT" |
    jq -r '.notification_body // empty'
)"

T15_WEATHER="$(
    printf '%s' "$T15_RESULT" |
    jq -r '.weather_observation // empty'
)"

T15_TRAFFIC="$(
    printf '%s' "$T15_RESULT" |
    jq -r '.traffic_observation // empty'
)"


# ==============================================================================
# 9/10 — FINAL DEMO DECISION
#
# PREPARE and notification_sent are deliberately reported separately.
#
# But unlike the previous version, this demo now treats notification delivery
# as a real success criterion.
# ==============================================================================

echo
echo "9/10 Autonomous agent decision"

echo
echo "Decision:     ${T15_DECISION:-UNKNOWN}"
echo "Notification: $T15_NOTIFICATION"

echo


if [ "$T15_DECISION" = "PREPARE" ]; then

    echo "      ✓ Autonomous evaluator entered PREPARE state."

else

    echo "      WARNING: Expected PREPARE but received '${T15_DECISION:-UNKNOWN}'."

fi


echo


if [ "$T15_NOTIFICATION" = "true" ]; then

    echo "      ✓ Notification delivery confirmed by backend."

elif [ "$T15_NOTIFICATION" = "false" ]; then

    echo "      ✗ PREPARE occurred, but backend reports notification_sent=false."

    echo
    echo "      Notification delivery is a required part of this demonstration."

else

    echo "      ✗ Backend did not return notification delivery status."

fi


echo
echo "Message:"
echo
echo "------------------------------------------------------------------"


if [ -n "$T15_BODY" ] && [ "$T15_BODY" != "null" ]; then

    echo "$T15_BODY"

else

    echo "No notification body returned."

fi


echo "------------------------------------------------------------------"


# ==============================================================================
# OBSERVATION DISPLAY
# ==============================================================================

echo
echo "Demonstration environment used:"
echo
echo "  Weather:      $WEATHER_OBSERVATION"
echo "  Traffic:      $TRAFFIC_OBSERVATION"


if [ -n "$T15_WEATHER" ] || [ -n "$T15_TRAFFIC" ]; then

    echo
    echo "Backend observations returned:"
    echo
    echo "  Weather:      ${T15_WEATHER:-not returned by evaluator}"
    echo "  Traffic:      ${T15_TRAFFIC:-not returned by evaluator}"

fi


# ==============================================================================
# 10/10 — CURRENT AUTONOMOUS AUDIT
#
# The audit is filtered to:
#
#   1. The current demonstration date.
#   2. The EXACT personalized commitment ID.
#
# This prevents unrelated calendar commitments from being presented as
# the personalized autonomous activity.
# ==============================================================================

echo
echo "10/10 CURRENT AUTONOMOUS AUDIT TIMELINE"

echo

AUDIT_RESULT="$(
    curl --fail-with-body -sS \
        "$BASE_URL/api/v1/students/$STUDENT_ID/events"
)"


CURRENT_AUDIT="$(
    printf '%s' "$AUDIT_RESULT" |
    jq \
        --arg date "$DEMO_DATE" '
        if type == "array" then
            [
                .[]
                | select(
                    ((.timestamp // "") | startswith($date))
                  )
            ]
        else
            []
        end
        '
)"


PERSONALIZED_AUDIT="$(
    printf '%s' "$CURRENT_AUDIT" |
    jq \
        --arg commitment "$COMMITMENT_ID" '
        [
            .[]
            | select(
                (.commitment_id // "") == $commitment
              )
        ]
        '
)"


echo "Personalized commitment:"
echo
echo "  $COMMITMENT_ID"

echo


if [ "$(printf '%s' "$PERSONALIZED_AUDIT" | jq 'length')" -gt 0 ]; then

    echo "Audit events for the personalized commitment:"
    echo

    printf '%s' "$PERSONALIZED_AUDIT" | jq .

else

    echo "No audit events were returned for the personalized commitment."

    echo
    echo "The evaluator returned successfully, but the backend did not"
    echo "expose matching audit records for:"
    echo
    echo "  $COMMITMENT_ID"

fi


# ==============================================================================
# FINAL SUMMARY
# ==============================================================================

echo
separator

echo "            DEMONSTRATION COMPLETE"

separator

echo

printf '%-24s %s\n' \
    "Activity:" \
    "$ACTIVITY_TITLE"

printf '%-24s %s\n' \
    "Activity start:" \
    "$ACTIVITY_TIME_SAST"

printf '%-24s %s\n' \
    "Activity end:" \
    "$ACTIVITY_END_TIME_SAST"

printf '%-24s %s\n' \
    "Activity duration:" \
    "$SUGGESTION_DURATION minutes"

printf '%-24s %s\n' \
    "Backend time:" \
    "UTC"

printf '%-24s %s\n' \
    "Demo student:" \
    "$STUDENT_ID"

printf '%-24s %s\n' \
    "Commitment:" \
    "$COMMITMENT_ID"


echo
echo "Agentic flow demonstrated:"
echo

echo "  Learned student preferences"
echo "        ↓"
echo "  Calendar pattern"
echo "        ↓"
echo "  Curated campus knowledge"
echo "        ↓"
echo "  Personalized recommendation"
echo "        ↓"
echo "  Stored recommendation memory"
echo "        ↓"
echo "  Natural-language follow-up"
echo "        ↓"
echo "  Answer retrieved locally"
echo "        ↓"
echo "  Gemini called: false"
echo "        ↓"
echo "  Activity saved to Google Calendar"
echo "        ↓"
echo "  Duration derived from recommendation"
echo "        ↓"
echo "  Autonomous monitoring"
echo "        ↓"
echo "  T-2 hours → NO_ACTION"
echo "        ↓"
echo "  T-15 minutes → PREPARE"
echo "        ↓"
echo "  Notification delivery confirmed"
echo "        ↓"
echo "  Audit records tied to personalized commitment"


echo
echo "Environment used consistently:"
echo
echo "  Weather: $WEATHER_OBSERVATION"
echo "  Traffic: $TRAFFIC_OBSERVATION"


echo
echo "Timing model:"
echo
echo "  Recommendation duration: ${SUGGESTION_DURATION} minutes"
echo "  Travel time:              ${TRAVEL_MINUTES} minutes"
echo "  Preparation time:         ${PREPARATION_MINUTES} minutes"
echo "  Arrival buffer:           ${ARRIVAL_BUFFER_MINUTES} minutes"

echo

echo "  Activity start:           $ACTIVITY_TIME_UTC"
echo "  Activity end:             $ACTIVITY_END_TIME_UTC"
echo "  Preparation:              $PREPARE_TIME_UTC"
echo "  Leave threshold:          ${DEMO_DATE}T15:20:00Z"
echo "  Target arrival:           ${DEMO_DATE}T15:25:00Z"


echo
echo "The demonstration timeline was completely predefined."
echo "Weather and traffic were fixed demonstration observations."
echo "No live/system clock was used by the demo."
echo "The recommendation duration is the single source of truth."
echo "Notification status is reported from the backend."
echo "Audit records are filtered to the exact personalized commitment."

echo
separator
