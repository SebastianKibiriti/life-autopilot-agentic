# Life Autopilot — build roadmap

## Product promise

Keep a student on schedule by continuously monitoring upcoming commitments and real-world context, deciding what the student needs to do next, and proactively acting before the student has to ask.

## Scope lock

Must demonstrate: commitments, destination, current location, travel estimate, preparation time, autonomous decision-making, preparation/leave notifications, re-evaluation, persistent state, behavior learning, activity history, import, failure handling, Google Cloud deployment, tests, architecture documentation, and a reproducible demo.

The first demo should stay narrow: one student, one upcoming commitment, walking travel, one preparation profile, and one autonomous decision loop.

## Build order

1. Foundation: Flutter shell, FastAPI, ADK/Gemini boundary, environment configuration, Cloud Run/Firestore plan.
2. Commitment domain: student, commitment, repositories, and next-commitment query.
3. Location: permission-aware current-location adapter.
4. Destination resolution: Places-backed lookup with cached coordinates.
5. Routing: Routes-backed walking estimate with a clearly labelled fallback.
6. Deterministic departure planner: preparation threshold, leave threshold, lateness.
7. Taskmaster agent: bounded decisions `NO_ACTION`, `PREPARE`, `LEAVE`, `REPLAN`, `ESCALATE`.
8. Activity log: structured operational events, never private chain-of-thought.
9. Notifications and autonomous triggers.
10. Re-evaluation and behavioral learning.
11. Timetable import, failure handling, deployment, tests, architecture docs, and demo polish.

## Out of scope for the MVP

Social features, a general-purpose chatbot, budgeting, email management, study planning, multi-agent architecture, iOS polish, and complex animation.

