# Development history

## 2026-08-18 — Foundation checkpoint

- Attempted: establish the fresh hackathon repository and first end-to-end local contract.
- Changed: added the FastAPI app, Pydantic evaluation models, deterministic planner, bounded local policy, Flutter dashboard shell, tests, README, roadmap, and architecture note.
- Verified: four backend unit tests, backend compile, FastAPI health/evaluation smoke check, Flutter widget test, and Flutter analyzer.
- Failed or deferred: Git metadata initially required workspace permission; after approval the first commit was recorded. ADK, Gemini, Firestore, Cloud Run, routing, location, notifications, and import were not attempted in this slice.
- Decision rationale: keep arithmetic and the initial policy deterministic so behavior is testable before adding cloud cost and provider variability.

## 2026-08-18 — Knowledge-base build

- Attempted: create durable context for a future coding agent without relying on conversation history.
- Changed: added the root entry point, subsystem documents, current-state audit, ADRs, roadmap, testing strategy, disclosure record, and exact maintenance prompt.
- Verified: prompt comparison against the attached source, Markdown patch validation, repository status, and the existing backend test suite.
- Failed or deferred: no code behavior changed; cloud integrations remain unverified.
- Decision rationale: separate authoritative current facts from planned architecture and preserve the maintenance prompt as a repository artifact.

## 2026-08-18 — Commitment repository slice

- Attempted: implement the next documented task without requiring Firestore credentials.
- Changed: added the `CommitmentRepository` protocol, in-memory implementation, generated IDs, status filtering, idempotent replacement by ID, and `get_next_commitment` service.
- Verified: eight backend unit tests, backend compilation, and `git diff --check` pass.
- Failed or deferred: API endpoints, Firestore persistence, authentication, and timezone policy remain outstanding.
- Decision rationale: keep the repository boundary provider-independent so Firestore can be added without changing agent policy.

## 2026-08-18 — Commitment API slice

- Attempted: expose the local commitment boundary through a usable backend API.
- Changed: added commitment creation, student-scoped listing, next-upcoming retrieval, validation, dependency overrides for tests, and API contract documentation.
- Verified: eleven backend tests pass, including API flows and invalid input handling.
- Failed or deferred: Firestore persistence and authenticated ownership are still not configured.
- Decision rationale: keep the API dependent on the repository protocol so the storage provider can change without changing the endpoint or agent policy.

## 2026-08-18 — Firestore adapter boundary

- Attempted: advance persistence toward Firestore without requiring external credentials.
- Changed: added `FirestoreCommitmentRepository` with an injected client boundary, Firestore-shaped student/commitment collection paths, and local fake-client tests.
- Verified: thirteen backend tests pass, compilation succeeds, and the diff is clean.
- Failed or deferred: real Firestore SDK/emulator/project verification cannot proceed because the SDK is not installed and no active gcloud account was detected.
- Decision rationale: stop at the first external setup boundary while preserving a tested adapter contract for the next session.

## 2026-08-21 — Real Firestore Integration

- Attempted: connect the backend to a real Google Cloud Firestore project and verify the storage adapter.
- Changed: added local `.env` configuration, loaded environment settings via `dotenv`, conditionally initialized a real Firestore client, and updated FastAPI dependency injection.
- Verified: added `tests/test_firestore_integration.py` containing live CRUD tests on the target project (`gen-lang-client-0563563702`). All 14 tests (13 unit, 1 integration) pass. Verified live database writing via `curl` smoke test.
- Failed or deferred: authentication and student ownership boundary remains deferred.
- Decision rationale: verify the real adapter contract early using environment variables to ensure compatibility with Cloud Run before building downstream routing/ADK features.

## 2026-08-22 — Context, routing, Gemini, events, and learning

- Attempted: land the autonomous evaluation path without fabricating geography or depending on live Gemini in tests.
- Changed: location APIs, Places/Routes adapters, Gemini 3.5 client with fallback, event/notification recorder, timetable extract/confirm, preparation-profile learning, timezone-aware validation.
- Verified: 25 unit tests pass; live Firestore test is skipped unless `FIRESTORE_INTEGRATION=true`.
- Failed or deferred: background scheduler, Flutter client, Cloud Run, live Gemini/Places/Routes verification, ADK, push delivery.
- Decision rationale: unknown destinations must escalate; Gemini 3.5 Flash is the configured default to match hackathon rules; GenAI SDK is the current qualifying Google agent framework.
