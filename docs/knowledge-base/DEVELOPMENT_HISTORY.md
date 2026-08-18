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

