# Current implementation state

Last reviewed: 2026-08-22

## Baseline

The repository contains a Collaborative Partner vertical slice plus context
adapters. Arithmetic stays deterministic. Gemini is used for notification copy,
timetable parsing, and structured companion suggestions, with a local fallback
when credentials are missing.

## Working

### Backend

- FastAPI application in `backend/app/main.py`.
- `GET /health` returns service health.
- `POST /api/v1/agent/evaluate` evaluates a supplied snapshot (legacy contract).
- `POST /api/v1/students/{student_id}/evaluate` runs the autonomous loop from stored commitment + location + preparation profile.
- Commitment create/list/next endpoints.
- Location GET/POST endpoints.
- Agent event timeline endpoint.
- Conservative preparation-profile learning endpoint.
- Timetable extract/confirm endpoints (Gemini text when configured; empty result without a client).
- Pydantic models including Location, Destination, TravelEstimate, PreparationProfile, AgentEvent, and AgentPhase.
- Deterministic timing service in `backend/app/planner.py`.
- Bounded Taskmaster policy in `backend/app/agent.py`.
- `CommitmentRepository`, location, event, and preparation-profile repositories with in-memory and Firestore adapters.
- `FirestoreCommitmentRepository` verified previously against project `gen-lang-client-0563563702`; live integration tests are opt-in (`FIRESTORE_INTEGRATION=true`).
- Places resolver with campus cache and optional Places API; unknown destinations return no coordinates.
- Walking Routes estimator with optional Routes API and labelled Haversine fallback.
- Gemini client via `google-genai`, default model `gemini-3.5-flash` through Vertex AI `global`, deterministic copy fallback.
- Idempotent in-process notification recorder (no FCM yet).
- Companion profile and suggestion memory with in-memory and Firestore storage.
- Curated campus graph alias resolution and stored follow-up answers.
- Timezone-aware datetime validation on API inputs.

Decisions currently supported: `NO_ACTION`, `PREPARE`, `LEAVE`, `REPLAN`, `ESCALATE`.

### Mobile

- Minimal Flutter Material 3 shell in `mobile/lib/main.dart`.
- Dashboard placeholder shows agent status, commitments, and activity sections.
- No network client, authentication, location permissions, notifications, timetable import, or Riverpod state management yet.

### Documentation

- Root roadmap: `docs/roadmap.md`.
- Initial architecture note: `docs/architecture.md`.
- This knowledge base under `docs/knowledge-base/`.

## Partially Working

- Gemini 3.5 Flash is the configured default and has been verified live through Vertex AI using the `global` location.
- Places/Routes live APIs require keys; without keys, known campus labels resolve from cache and unknown labels escalate.
- Notifications are persisted as events, not delivered to a device.
- The Flutter dashboard is a shell only and is not connected to the backend.
- There is still no background scheduler.

## Not Started

- Google ADK orchestration (GenAI SDK is present and qualifies as a Google agent framework);
- Cloud Run deployment;
- Firebase Authentication;
- local or remote push notifications;
- autonomous scheduler or background trigger;
- timetable PDF/image extraction and review UI;
- real Flutter-to-backend integration;
- production secrets and cloud configuration beyond local `.env`.

## Broken / Known Problems

- Default `unittest discover` skips live Firestore tests so the suite cannot hang on network.
- Timezone DST conversion is not implemented; naive datetimes are rejected.
- The service cannot yet demonstrate autonomous notifications without a caller hitting evaluate.

## External Configuration Required

- Google Cloud project and billing/credits.
- Vertex AI/Gemini access for live copy and extraction.
- Firestore database if `USE_FIRESTORE=true`.
- Cloud Run service account and deployment configuration.
- Routes and Places credentials for live geography.
- Firebase configuration if authentication or messaging is enabled.

## Last Verified Tests

- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s backend/tests -p 'test_*.py'` — 25 tests, 1 skipped (live Firestore), 0 failures.
- FastAPI `TestClient` covers health/evaluation, commitment CRUD/next, location, learning, and naive datetime rejection.

## Current Git branch

`main`

## Latest relevant commit

Use `git log -1 --oneline` for the exact checkpoint.

## Current development phase

Phases 2–4 in progress: context, routing, events, learning, and Gemini copy are in code. Scheduler, Flutter client, and Cloud Run remain.

## Known limitations

- Route fallback is Haversine walking, not live Google Routes, unless `ROUTES_API_KEY` is set.
- The local policy does not call Google ADK.
- Notification delivery is an event record, not a push channel.
- The mobile shell is not a functional client.
