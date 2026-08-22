# Next steps

## Completed target

Location, destination resolution, walking routes (live or labelled fallback), Gemini 3.5 copy, event log, notification recorder, timetable extract/confirm, and preparation-profile learning are implemented with unit tests.

## Immediate target

Add a background scheduler so the golden PREPARE → LEAVE → REPLAN loop progresses without a chat prompt or manual evaluate call.

## Dependencies

- `POST /api/v1/students/{student_id}/evaluate`
- Commitment, location, event, and profile repositories
- Idempotent notification recorder

## Acceptance criteria

- A configured interval evaluates students that have upcoming commitments.
- Duplicate PREPARE/LEAVE notifications are suppressed within the dedup window.
- The scheduler can be disabled in tests via environment configuration.
- Missing location or unknown destination still escalates.

## Blockers

- Live Gemini 3.5+, Places, and Routes calls need API/project credentials (local fallbacks exist).
- Cloud Run deploy needs gcloud auth and a project.
- Device push notifications need Firebase/FCM configuration.

## Priority order

1. Add a background scheduler/autonomous trigger.
2. Connect the Flutter client to commitment, location, evaluate, and event APIs.
3. Add Cloud Run packaging and a submission architecture diagram.
4. Verify live Gemini 3.5+ with Vertex or Gemini API credentials.
5. Add authenticated student identity when it no longer blocks the demo.
