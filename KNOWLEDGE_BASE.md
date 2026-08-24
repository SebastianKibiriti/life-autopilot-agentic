# Life Autopilot knowledge base

Life Autopilot Agentic is a fresh hackathon rebuild for the All Things Agentic Hackathon, targeting **The Taskmaster**. It is an autonomous student operations agent: it combines upcoming commitments, current location, travel time, and learned preparation behavior to decide when the student needs to act, then intervenes before the student asks. 

NON-NEGOTIABLE PRODUCT PRINCIPLE

Life Autopilot is not a chat application.

Life Autopilot is not intended to be actively used throughout the day.

The primary user experience occurs while the application is in the background.

The agent is expected to initiate interactions.

The user should not need to open the application in order for the core value of the product to be delivered.

Opening the application should primarily serve:

- onboarding
- configuration
- reviewing agent activity
- viewing upcoming commitments
- reviewing learned behavior
- troubleshooting

The core product value is delivered through autonomous monitoring, decision making, and intervention.

## Read first

1. [Current state](docs/knowledge-base/CURRENT_STATE.md)
2. [Decisions](docs/knowledge-base/DECISIONS.md)
3. [Next steps](docs/knowledge-base/NEXT_STEPS.md)
4. [Project overview](docs/knowledge-base/PROJECT_OVERVIEW.md)
5. [Architecture](docs/knowledge-base/ARCHITECTURE.md)
6. [Agent behavior](docs/knowledge-base/AGENT_BEHAVIOR.md)

The full document map is in [docs/knowledge-base/README.md](docs/knowledge-base/README.md).

## Current scope

The first demo is one student and one upcoming commitment. The important loop is `Observe → Calculate → Reason → Act → Monitor → Re-evaluate → Learn`. The golden scenario is a 14:00 Database Systems class, with 22 minutes of travel, 12 minutes of preparation, and a 5-minute arrival buffer: `13:21 PREPARE`, `13:33 LEAVE`, and `13:37 REPLAN` if the student remains stationary.

## Required stack

The final submission must use Gemini 3.5+, a qualifying Google agent framework (planned: Google ADK), and Google Cloud infrastructure (planned: Cloud Run and Firestore). Planned supporting services are Vertex AI, Routes, Places, Firebase Authentication, notifications, and an autonomous trigger. Only the local FastAPI/Flutter foundation is working today.

## Current phase and verified state

Phase 0 foundation is complete locally. FastAPI exposes `/health` and `/api/v1/agent/evaluate`; the deterministic planner and bounded local decision policy are tested; the Flutter dashboard shell passes its widget test and analyzer. ADK, Gemini, Firestore, Cloud Run, live routing, location, notifications, import, and durable autonomy are not started.

## Instructions for a New AI Agent

1. Read `KNOWLEDGE_BASE.md` first.
2. Read `CURRENT_STATE.md`.
3. Read `DECISIONS.md`.
4. Read `NEXT_STEPS.md`.
5. Read the relevant subsystem document before editing code.
6. Inspect the actual repository before assuming documentation is correct.
7. Update the knowledge base whenever meaningful implementation changes are made.
8. Never silently change architecture decisions.
9. Record important architectural changes in `DECISIONS.md`.
10. Record completed milestones in `DEVELOPMENT_HISTORY.md`.
11. Update `CURRENT_STATE.md` at the end of substantial development sessions.
12. Keep `NEXT_STEPS.md` synchronized with the actual project.
13. Clearly distinguish implemented, partially implemented, planned, deferred, and abandoned work.
14. Never claim something works unless verified.
15. Preserve hackathon eligibility and mandatory Google technology requirements.

## Constraints

Keep arithmetic deterministic, state explicit, provider failures visible, secrets server-side, location retention minimal, and the scope narrow. Do not silently copy code from the historical Life Autopilot project; record any reuse in `DISCLOSURE.md`.

## Recommended next task

Add student/commitment API endpoints on top of the tested repository boundary. Acceptance is a local API flow that can create commitments and return the next active upcoming commitment without Firestore credentials.
