# Architecture

## Current local architecture

```text
Flutter shell
    │ not connected yet
    ▼
FastAPI
    │
    ├── Pydantic request/response models
    ├── deterministic departure planner
    └── local bounded companion policy
```

## Target hackathon architecture

```text
Student
  │
  ▼
Flutter + Riverpod
  ├── onboarding and permissions
  ├── timetable import and review
  ├── current-state dashboard
  ├── agent activity timeline
  └── local/remote notification surface
  │ HTTPS
  ▼
Cloud Run: FastAPI + Google ADK
  ├── commitment and student services
  ├── agent state machine
  ├── deterministic DeparturePlanner
  ├── companion agent and personalization memory
  ├── Routes/Places adapters
  └── notification/action adapters
  │
  ├── Vertex AI: Gemini 3.5+
  ├── Firestore: operational state and memory
  ├── Google Routes API
  ├── Google Places API
  └── Firebase/Flutter notification path
```

## Component responsibilities

### Flutter

Owns user-facing state, permissions, timetable review, location capture, notification presentation, and activity history display. It should not own agent policy or duplicate timing arithmetic.

### FastAPI

Owns the API boundary, validation, authentication boundary, orchestration entry points, provider adapters, and response shaping. It should remain usable locally with provider fakes.

### Google ADK and Gemini

ADK owns agent orchestration and tool access. Gemini reasons about ambiguous or changing context. Gemini must not be used for arithmetic that deterministic code can perform reliably.

### Firestore

The planned persistent source of truth for student profiles, commitments, agent state, decision events, departure history, and preparation profiles. Writes should be explicit and idempotent where a scheduler may retry.

### External providers

Routes estimates travel; Places resolves human-readable destinations; location adapters provide current coordinates; notifications carry actions to the student. Each provider needs a timeout, error classification, and safe fallback.

## Data flow

1. A commitment is loaded or imported and reviewed by the student.
2. The scheduler selects the next relevant commitment.
3. Context tools retrieve location, destination, route, and preparation profile.
4. `DeparturePlanner` calculates preparation and leave thresholds.
5. The bounded agent chooses a decision.
6. An action tool sends a notification or records an escalation.
7. A structured `AgentEvent` is persisted.
8. A later evaluation checks movement and route changes, then reuses or replaces the plan.

## Security and failure posture

Secrets belong in runtime configuration, never source files. User identity must scope Firestore reads and writes. Provider failures should become explicit exceptional states, not fabricated values. Operational event logs may expose concise reasons and inputs, but never private chain-of-thought.
