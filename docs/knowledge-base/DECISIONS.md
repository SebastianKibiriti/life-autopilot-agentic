# Architecture Decision Records

## ADR-001

- ID: ADR-001
- Date: 2026-08-18
- Title: Target The Taskmaster
- Status: Accepted
- Context: Life Autopilot's strongest value is autonomous event-driven coordination: a commitment approaches, context is gathered, a decision is made, and an action is taken.
- Decision: Target The Taskmaster rather than a conversation-first partner or enterprise multi-agent fleet.
- Reasoning: The workflow directly matches autonomous routing and removes a concrete everyday friction.
- Alternatives considered: Collaborative Partner; Fortified Enterprise Fleet.
- Consequences: The demo must show the agent acting without a chat request, and scope must stay focused on one workflow.

## ADR-002

- ID: ADR-002
- Date: 2026-08-18
- Title: Keep arithmetic deterministic
- Status: Accepted and implemented
- Context: Travel duration, buffers, preparation, thresholds, and lateness are reliable application calculations.
- Decision: `DeparturePlanner` owns arithmetic; Gemini will reason about ambiguous or changing context.
- Reasoning: This improves correctness, testability, cost control, and explainability.
- Alternatives considered: Ask the LLM to calculate all timing; use a single opaque prompt for planning.
- Consequences: The agent receives structured calculations and cannot invent basic timing values.

## ADR-003

- ID: ADR-003
- Date: 2026-08-18
- Title: Build a fresh hackathon repository
- Status: Accepted and implemented
- Context: The historical Life Autopilot project predates the hackathon.
- Decision: Treat this repository as a new implementation and disclose any future reuse explicitly.
- Reasoning: This preserves hackathon eligibility and makes the build history clear.
- Alternatives considered: Submit the historical repository; silently copy historical modules.
- Consequences: Product knowledge may be reused, but copied source must be recorded in `DISCLOSURE.md`.

## ADR-004

- ID: ADR-004
- Date: 2026-08-18
- Title: Start with one autonomous workflow
- Status: Accepted
- Context: A broad life-management assistant would dilute the demo and increase delivery risk.
- Decision: Build one student, one upcoming commitment, walking travel, one preparation profile, and one decision loop first.
- Reasoning: A narrow, complete autonomous loop is more valuable for the hackathon than many partial features.
- Alternatives considered: General productivity suite; broad campus assistant; multiple parallel agents.
- Consequences: Calendar integrations, voice, analytics, and richer campus data remain deferred.

## ADR-005

- ID: ADR-005
- Date: 2026-08-18
- Title: Use bounded decisions and explicit states
- Status: Accepted and partially implemented
- Context: A free-form LLM should not invent application states or actions.
- Decision: Constrain decisions to `NO_ACTION`, `PREPARE`, `LEAVE`, `REPLAN`, and `ESCALATE`, with an explicit state machine planned for persistence.
- Reasoning: Bounded behavior is safer, testable, and easier for judges to understand.
- Alternatives considered: Free-form action text; conversation-history-only state.
- Consequences: New actions require a documented enum/state transition rather than prompt-only behavior.

## ADR-006

- ID: ADR-006
- Date: 2026-08-18
- Title: Treat provider failures as data
- Status: Accepted and partially implemented
- Context: Location, routing, Gemini, notifications, and Firestore can fail during a live demo.
- Decision: Return explicit provider markers and safe exceptional decisions instead of fabricated values.
- Reasoning: Failure visibility is safer and demonstrates production-minded architecture.
- Alternatives considered: Retry indefinitely; silently use stale or invented context.
- Consequences: Every adapter needs timeout, failure classification, fallback, and verification behavior.

## ADR-007

- ID: ADR-007
- Date: 2026-08-18
- Title: Delay external integrations until contracts are testable
- Status: Accepted
- Context: Cloud integrations add cost and moving parts before the core behavior is stable.
- Decision: Start provider-free with local fakes and connect Google services behind tested interfaces.
- Reasoning: This keeps the first slice reproducible while preserving the required final architecture.
- Alternatives considered: Start with live APIs; couple business logic directly to SDKs.
- Consequences: The current baseline is not yet hackathon-submittable; real Google integrations remain a required next phase.

