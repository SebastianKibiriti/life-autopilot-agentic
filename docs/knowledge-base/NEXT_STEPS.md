# Next steps

## Immediate target

Implement the commitment repository interface and a local in-memory fake, then add a next-commitment query. Keep the repository shape compatible with a later Firestore implementation.

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

1. Add commitment repository protocol and local fake.
2. Add next-commitment service and tests.
3. Add student/commitment API endpoints.
4. Add Firestore repository and emulator/local integration path.
5. Add ADK/Gemini adapter around the tested decision contract.

