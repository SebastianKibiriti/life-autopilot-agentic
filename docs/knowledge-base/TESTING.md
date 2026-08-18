# Testing and verification

## Current commands

From the repository root:

```bash
PYTHONPATH=backend python3 -m unittest discover -s backend/tests -p 'test_*.py'
```

Expected baseline: 4 tests pass.

```bash
PYTHONPATH=backend python3 -m compileall -q backend
```

```bash
cd mobile
flutter test
flutter analyze
```

Expected baseline: widget tests pass and analyzer reports no issues.

## API smoke check

Use FastAPI `TestClient` or run the service and call `/health` and `/api/v1/agent/evaluate`. The golden request should produce:

- `preparation_at`: 13:21;
- `leave_at`: 13:33;
- `PREPARE` when evaluated at 13:22;
- `REPLAN` at 13:37 when stationary.

## Current test coverage

- planner threshold calculation;
- commitment repository scoping and ID assignment;
- earliest active next-commitment query;
- completed/cancelled filtering;
- empty and past schedule behavior;
- missing route escalation;
- late stationary replanning;
- preparation-window decision;
- API health and evaluation smoke;
- Flutter dashboard rendering.
- commitment API create/list/next flows and validation.
- Firestore-shaped adapter persistence and next-query behavior through a local fake client.

## Gaps to close

- timezone and DST behavior;
- commitment validation and persistence;
- provider timeout/fallback behavior;
- notification idempotency and failure;
- ADK tool invocation;
- Gemini response validation;
- Firestore security rules;
- scheduler retries and duplicate evaluations;
- location permission states;
- timetable extraction validation and user review;
- end-to-end Flutter/backend flow.
