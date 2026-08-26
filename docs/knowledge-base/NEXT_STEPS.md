# Next steps

## Completed target

Location, destination resolution, walking routes (live or labelled fallback), Gemini 3.5 copy, event log, notification recorder, timetable extract/confirm, and preparation-profile learning are implemented with unit tests.

## Current checkpoint

The autonomous evaluation path and reusable `AgentScheduler` are implemented and covered by backend tests. Cloud Run packaging is now present in the repository (`Dockerfile`, `.dockerignore`, and `infrastructure/cloud-run.env.example`). The remaining work is wiring the scheduler into the service lifecycle and completing the mobile client.

## Dependencies

- `POST /api/v1/students/{student_id}/evaluate`
- Commitment, location, event, and profile repositories
- Idempotent notification recorder

## Scheduler acceptance criteria

- A configured interval evaluates students that have upcoming commitments.
- Duplicate PREPARE/LEAVE notifications are suppressed within the dedup window.
- The scheduler can be disabled in tests via environment configuration.
- Missing location or unknown destination still escalates.

## Blockers

- Live Gemini 3.5+, Places, and Routes calls need API/project credentials (local fallbacks exist).
- Cloud Run deploy needs gcloud auth and a project.
- Device push notifications need Firebase/FCM configuration.

## Priority order

1. Follow [CROSS_APP_TASKMASTER_PLAN.md](CROSS_APP_TASKMASTER_PLAN.md), beginning with Google Calendar ingestion.
2. Add Calendar actions and one real notification channel.
3. Run and verify the autonomous cross-app monitoring loop.
4. Finalize the architecture diagram, demo evidence, and Devpost submission.
