# Cross-app Taskmaster milestone plan

## Goal

Move Life Autopilot from an autonomous decision backend into a Taskmaster agent that can discover work in one application, reason across multiple signals, act in other applications, and monitor the result without step-by-step user guidance.

Each milestone ends with a verification checkpoint and a separate Git commit. The project remains demoable after every milestone.

## Milestone 1 — Google Calendar ingestion

**Outcome:** The agent discovers upcoming commitments from Google Calendar instead of requiring manual Swagger entry.

**Build:**

- Add a Calendar provider boundary and normalized event model.
- Implement read-only event sync for the next 24–48 hours.
- Preserve the current manual commitment endpoint as a fallback.
- Store the last sync cursor and imported event IDs in Firestore.
- Add tests with a fake Calendar client; no live credentials in tests.

**External setup:** Google Calendar API, OAuth consent screen, and a local/service credential flow.

**Verify:** A calendar event becomes a Life Autopilot commitment and duplicate sync does not create duplicate commitments.

**Commit:** `feat: add Google Calendar commitment ingestion`

## Milestone 2 — Calendar actions and idempotency

**Outcome:** The agent writes useful actions back into Calendar.

**Build:**

- Create/update “Prepare for …” and “Leave for …” calendar action events.
- Attach the decision reason, route estimate, and generated Gemini message.
- Make actions idempotent by source event ID and decision phase.
- Record Calendar action success/failure in the existing agent event timeline.

**External setup:** Calendar write scope and a test calendar.

**Verify:** One autonomous cycle creates the correct Calendar action once; repeating the cycle updates or suppresses the duplicate.

**Commit:** `feat: let the agent write calendar actions`

## Milestone 3 — Notification and audit action

**Outcome:** The agent produces a visible intervention and durable action audit without requiring a Google Workspace account.

**Build:**

- Keep the existing Firestore recorder as the durable audit sink and demo notification surface.
- Include the Gemini-generated message in the Calendar action description and API response.
- Keep the optional Google Chat webhook adapter for Workspace accounts only.
- Include decision, commitment, required action, and deep link/calendar reference.
- Add delivery outcome and retry-safe deduplication.

**External setup:** None for the MVP. Google Chat requires a Workspace account and is optional; Firebase/Gmail can be added later.

**Verify:** PREPARE, LEAVE, REPLAN, and ESCALATE produce a visible API response, Calendar action or recorded event, and remain idempotent.

**Commit:** `feat: add external Taskmaster notifications`

## Milestone 4 — Autonomous cross-app monitoring loop

**Outcome:** The agent completes and monitors the workflow without a manual evaluate request.

**Build:**

- Extend the scheduler to run the full Calendar → context → route → Gemini → Calendar/notification cycle.
- Evaluate multiple active commitments per student.
- Re-read Calendar and location context after an action.
- Replan when the student has not moved, the event changes, or route data becomes unavailable.
- Expose a compact cycle status endpoint for the demo and operational debugging.

**External setup:** Enable the deployed scheduler only after Calendar and notification credentials are configured.

**Verify:** A scripted scenario runs from calendar event to action to replan with no manual intervention between stages.

**Commit:** `feat: run autonomous cross-app monitoring cycles`

## Milestone 5 — Submission proof and release

**Outcome:** The project visibly proves the Taskmaster behavior to judges.

**Build:**

- Update architecture diagram to show Calendar, Routes/Places, Gemini, Calendar actions, notifications, Firestore, and Cloud Run.
- Add a reproducible demo seed script and a short end-to-end runbook.
- Capture Cloud Run, Firestore, Vertex AI, Calendar, notification, and event-log evidence.
- Update README and Devpost draft with the exact model, Google Gen AI SDK, Cloud services, and disclosure.
- Record a public demo video under four minutes.

**External setup:** Final Cloud Run deployment, public video upload, and Devpost submission.

**Verify:** A fresh viewer can follow the README, see the agent act across applications, and identify every required Google technology.

**Commit:** `docs: finalize cross-app Taskmaster submission evidence`

## Recommended order

Complete Milestone 1 before requesting Calendar write access. Complete Milestone 2 before adding notifications. Complete Milestone 4 only after the individual integrations are independently verified. Do not start submission recording until the end-to-end scenario succeeds twice.

## Current status

- Milestone 1: code and local OAuth sync complete; first real sync verified.
- Milestone 2: code and real Calendar write action verified.
- Milestone 3: core audit/action path is available; real Chat delivery is optional.
- Milestones 4–5: pending.
- Existing autonomous multi-commitment cycle: available as the baseline for Milestone 4.
- Current public repository: https://github.com/SebastianKibiriti/life-autopilot-agentic
