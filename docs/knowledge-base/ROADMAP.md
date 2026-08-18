# Build roadmap

This is the knowledge-base version of the implementation plan. `docs/roadmap.md` remains the shorter project roadmap.

## Phase 0 — foundation (current baseline)

- [x] Fresh repository structure.
- [x] FastAPI shell and health endpoint.
- [x] Flutter shell.
- [x] Deterministic departure planner.
- [x] Local bounded decision policy.
- [x] Initial tests and documentation.
- [ ] Actual Google ADK/Gemini boundary.
- [ ] Cloud Run and Firestore configuration.

Acceptance: local backend and mobile shell run independently, and the golden timing logic is tested.

## Phase 1 — commitment domain

- [ ] Student and commitment API endpoints.
- [x] Local commitment repository interface and fake.
- [x] Next-commitment query.
- [ ] Firestore repository implementation.
- [ ] Manual commitment creation.

Acceptance: the backend returns the next structured commitment for a student.

## Phase 2 — context and destination

- [ ] Location permission-aware adapter.
- [ ] Current-location endpoint.
- [ ] Destination model and Places resolver.
- [ ] Cache and confidence handling.

Acceptance: a commitment can be connected to a trustworthy destination and a current context or explicit failure state.

## Phase 3 — routing and planning

- [ ] Routes adapter for walking.
- [ ] Explicit fallback estimate.
- [ ] Route timestamp and provider metadata.
- [ ] Timezone validation.

Acceptance: current location plus destination produces a route estimate or a visible, safe failure.

## Phase 4 — real agent and actions

- [ ] Google ADK Taskmaster agent.
- [ ] Vertex AI Gemini adapter.
- [ ] Tool contracts for schedule, context, travel, memory, and actions.
- [ ] Structured decision event log.
- [ ] Local notification action.

Acceptance: a context change causes a bounded agent decision and observable action result.

## Phase 5 — autonomy and learning

- [ ] Scheduler/background trigger.
- [ ] Re-evaluation after missed departure.
- [ ] Idempotent notification delivery.
- [ ] Conservative preparation-profile updates.
- [ ] Activity timeline in Flutter.

Acceptance: the student does not need to open the app or ask a question for the golden scenario to progress.

## Phase 6 — import, deployment, and submission readiness

- [ ] PDF/image timetable extraction with Gemini.
- [ ] Validation and user review before save.
- [ ] Cloud Run deployment.
- [ ] Firestore production configuration.
- [ ] Architecture diagram.
- [ ] Reproducible README.
- [ ] Demo recording and hackathon disclosure.

Acceptance: a judge can understand, run, and see the agent working, with visible Google Cloud proof.
