# Architecture

```text
Flutter mobile shell
        │ HTTP
        ▼
FastAPI API boundary ─────── Firestore repositories
        │
        ▼
Taskmaster orchestration
   ├── deterministic departure planner
   ├── ADK/Gemini reasoning adapter
   ├── Routes/Places adapters
   └── notification/action adapters
        │
        ▼
Cloud Run deployment + Vertex AI + Firestore
```

The deterministic planner owns arithmetic. The agent owns contextual decisions and bounded re-planning. Every action should produce a structured event containing observation, context, decision, action, and outcome; private model chain-of-thought is not persisted or displayed.

## First API contract

`POST /api/v1/agent/evaluate`

Input:

```json
{
  "now": "2026-08-18T13:20:00+02:00",
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

The response returns preparation/leave thresholds plus one bounded decision and a concise operational reason.

