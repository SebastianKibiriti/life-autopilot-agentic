# API contract

## Backend entry point

Run from the repository root:

```bash
uvicorn app.main:app --app-dir backend --reload
```

Interactive API docs are available at `http://127.0.0.1:8000/docs`.

## `GET /health`

Response:

```json
{
  "status": "ok",
  "service": "life-autopilot-agentic"
}
```

## `POST /api/v1/agent/evaluate`

This is the current local contract. It evaluates one context snapshot. It is not yet a persistent autonomous scheduler.

Request:

```json
{
  "now": "2026-08-18T13:22:00+02:00",
  "commitment": {
    "title": "Database Systems",
    "start_time": "2026-08-18T14:00:00+02:00",
    "destination": "Engineering Building B"
  },
  "travel_minutes": 22,
  "preparation_minutes": 12,
  "arrival_buffer_minutes": 5,
  "student_has_started_moving": false
}
```

Fields:

- `now`: evaluation timestamp.
- `commitment`: title, start time, and human-readable destination.
- `travel_minutes`: known route duration, or `null` when unavailable.
- `preparation_minutes`: deterministic preparation estimate.
- `arrival_buffer_minutes`: safety margin before the commitment.
- `student_has_started_moving`: current movement signal used by the local policy.

Response:

```json
{
  "commitment_title": "Database Systems",
  "preparation_at": "2026-08-18T13:21:00+02:00",
  "leave_at": "2026-08-18T13:33:00+02:00",
  "decision": "PREPARE",
  "reason": "The preparation window is open.",
  "route_provider": "provided"
}
```

Possible `decision` values are `NO_ACTION`, `PREPARE`, `LEAVE`, `REPLAN`, and `ESCALATE`.

Possible `route_provider` values in the current implementation are `provided` and `unavailable`. Future adapters should add explicit values such as `routes` and `fallback`.

## Commitment endpoints

### `POST /api/v1/students/{student_id}/commitments`

Creates a commitment in the configured repository and returns a generated ID.

```json
{
  "title": "Database Systems",
  "start_time": "2026-08-18T14:00:00Z",
  "destination": "Engineering Building B",
  "status": "active"
}
```

Returns `201 Created` with the stored commitment.

### `GET /api/v1/students/{student_id}/commitments`

Returns commitments scoped to the supplied student ID.

### `GET /api/v1/students/{student_id}/commitments/next?now=...`

Returns the earliest active commitment at or after `now`, or JSON `null` when none exists. If `now` is omitted, the server uses the current UTC time.

## Location, events, learning, and autonomous evaluate

### `POST /api/v1/students/{student_id}/location`

Stores the current location snapshot (timezone-aware `captured_at`).

### `GET /api/v1/students/{student_id}/location`

Returns the latest location or JSON `null`.

### `GET /api/v1/students/{student_id}/events`

Returns recent `AgentEvent` records, newest first.

### `POST /api/v1/students/{student_id}/evaluate`

Loads the next commitment, current location, and preparation profile, then runs the bounded loop. Query params: `now`, `student_has_started_moving`.

### `POST /api/v1/students/{student_id}/learn`

Updates the destination-scoped preparation profile with a bounded average.

### `POST /api/v1/students/{student_id}/timetable/extract` and `.../confirm`

Extracts proposed commitments (Gemini when configured) and saves confirmed items.

Naive datetimes are rejected with `422`.

## Planned contract evolution

The next API revisions should introduce authenticated student identity, a commitment ID, structured location and route objects, an evaluation/event ID, notification action results, and durable state versioning. Preserve backward compatibility only if it does not make the demo contract confusing.
