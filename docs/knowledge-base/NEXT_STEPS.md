# Next steps

## Completed target

Implemented the commitment repository interface, local in-memory fake, and next-commitment query. The boundary is compatible with a later Firestore implementation.

## Immediate target

Add student/commitment API endpoints on top of the repository boundary.

## Dependencies

- Current `Commitment` model in `backend/app/models.py`.
- A student identity or temporary demo student ID.
- Deterministic ordering by timezone-aware `start_time`.
- Unit tests that do not require Firestore credentials.

## Acceptance criteria

- A repository can save and list commitments for one student.
- `get_next_commitment` ignores completed/cancelled commitments and returns the earliest upcoming one.
- Empty schedules return an explicit empty result.
- The API or service test proves the query with at least two commitments.
- The interface can later be implemented by Firestore without changing agent policy.

## Blockers

- Firestore project and credentials are not configured.
- Student identity and authentication are not yet modelled.
- Timezone policy needs an explicit decision before production persistence.

## Priority order

1. Add student/commitment API endpoints and request validation.
2. Add Firestore repository and emulator/local integration path.
3. Add authenticated student identity and ownership boundaries.
4. Add ADK/Gemini adapter around the tested decision contract.
5. Add a route/context adapter boundary for the next commitment.
