# Current implementation state

Last reviewed: 2026-08-18

## Baseline

The repository contains the first local vertical slice. It is intentionally provider-free and deterministic so the product contract can be tested before cloud credentials and external APIs are introduced.

## Working

### Backend

- FastAPI application in `backend/app/main.py`.
- `GET /health` returns service health.
- `POST /api/v1/agent/evaluate` accepts a minimal commitment and context snapshot.
- Pydantic models in `backend/app/models.py`.
- Deterministic timing service in `backend/app/planner.py`.
- Local bounded Taskmaster policy in `backend/app/agent.py`.
- `CommitmentRepository` protocol and `InMemoryCommitmentRepository` fake in `backend/app/repositories.py`.
- `get_next_commitment` service in `backend/app/schedule.py`.
- Commitment persistence fields now include an optional ID and active/completed/cancelled status.
- Decisions currently supported: `NO_ACTION`, `PREPARE`, `LEAVE`, `REPLAN`, `ESCALATE`.
- Missing travel context escalates rather than inventing a route.
- Late and stationary context replans.

### Mobile

- Minimal Flutter Material 3 shell in `mobile/lib/main.dart`.
- Dashboard placeholder shows agent status, commitments, and activity sections.
- No network client, authentication, location permissions, notifications, timetable import, or Riverpod state management yet.

### Documentation

- Root roadmap: `docs/roadmap.md`.
- Initial architecture note: `docs/architecture.md`.
- This knowledge base under `docs/knowledge-base/`.

## Partially Working

- The local evaluation endpoint models the decision contract but is not yet a persistent autonomous agent.
- The Flutter dashboard is a shell only and is not connected to the backend.
- The route duration is accepted as input, but no Routes adapter exists.

## Not Started

The following are planned, not working:

- Google ADK orchestration;
- Gemini 3.5+ through Vertex AI;
- Firestore persistence and agent memory;
- Cloud Run deployment;
- Google Routes API;
- Google Places API;
- current-location adapter;
- Firebase Authentication;
- local or remote notifications;
- autonomous scheduler or background trigger;
- timetable PDF/image extraction;
- user review and timetable persistence;
- behavioral learning;
- activity event persistence;
- real Flutter-to-backend integration;
- production secrets and cloud configuration.

## Broken / Known Problems

- No known failing test at the current baseline.
- The service cannot yet demonstrate autonomous notifications because there is no scheduler or notification adapter.
- Timezone normalization and DST handling are not enforced.

## External Configuration Required

- Google Cloud project and billing/credits.
- Vertex AI/Gemini access.
- Google ADK runtime configuration.
- Firestore database.
- Cloud Run service account and deployment configuration.
- Routes and Places credentials.
- Firebase configuration if authentication or messaging is enabled.

## Last Verified Tests

- `PYTHONPATH=backend python3 -m unittest discover -s backend/tests -p 'test_*.py'` — 8 tests pass.
- FastAPI `TestClient` smoke check — `/health` and `PREPARE` evaluation pass.
- `flutter test` — widget test passes.
- `flutter analyze` — no issues reported.

## Current Git branch

`main`

## Latest relevant commit

Current HEAD after this slice; use `git log -1 --oneline` for the exact checkpoint. The previous foundation baseline was `9c97420 feat: establish hackathon agent foundation`.

## Current development phase

Phase 1 — commitment domain boundary. Local persistence and next-commitment retrieval are working; the next slice is student/commitment API endpoints.

## Contradictions reconciled

- The roadmap names ADK, Gemini, Firestore, Cloud Run, location, routing, notifications, learning, and import as required or planned, but repository inspection confirms none of those integrations are implemented yet.
- The current mobile dependency list does not include Riverpod; Riverpod remains planned.
- The current API accepts a travel duration directly; it does not yet resolve destinations or call a route provider.

## Known limitations

- The current route input is already a duration, not a route-provider result.
- Time arithmetic assumes timezone-aware values are supplied by callers; timezone normalization is not yet enforced.
- The local policy is not an LLM agent and does not call ADK or Gemini.
- There is no durable state, idempotency, notification delivery record, or retry behavior.
- The mobile shell is a visual starting point, not a functional client.
