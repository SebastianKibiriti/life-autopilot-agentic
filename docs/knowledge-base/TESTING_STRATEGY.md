# Testing strategy

## Unit tests

Test deterministic timing, timezone handling, state transitions, bounded decisions, preparation-profile updates, and validation independently of external services.

## Integration tests

Test FastAPI request/response contracts, repository interfaces, Firestore emulator/local fake behavior, and adapter error mapping. Use dependency injection so tests do not need production credentials.

## Agent tool tests

Each ADK tool needs contract tests for valid input, missing context, provider timeout, malformed provider response, and safe output. Agent decisions should be tested against structured context fixtures, not only prompt text.

## Failure tests

Cover unavailable location, unknown destination, Routes failure, stale route, Gemini failure, notification failure, duplicate scheduler evaluation, and a student who moves after an escalation.

## End-to-end tests

Exercise timetable/commitment input → context retrieval → deterministic plan → bounded agent decision → action result → event log → re-evaluation. The final demo should use fake clock and provider fixtures so the golden scenario is repeatable.

## Golden 14:00 scenario

Commitment starts at 14:00. Travel is 22 minutes. Preparation is 12 minutes. Arrival buffer is 5 minutes.

- 13:21: `PREPARE`.
- 13:33: `LEAVE`.
- 13:37 with the student stationary: fresh context and `REPLAN`.

This scenario must remain a recurring regression test throughout development.

