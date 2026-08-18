# Next steps

## Completed target

Implemented the commitment repository interface, local in-memory fake, and next-commitment query. The boundary is compatible with a later Firestore implementation.

## Completed target

Added student/commitment API endpoints on top of the repository boundary: create, list, next-upcoming, and request validation.

## Immediate target

Run the Firestore repository adapter against the real Firestore SDK and an emulator or configured Google Cloud project, then wire it into the application configuration.

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

- `google-cloud-firestore` is declared in `backend/requirements.txt` but is not installed in the current Python environment.
- `gcloud` is installed, but no active authenticated account was detected; the configured project is `gen-lang-client-0563563702`.
- Firestore emulator or a usable Firestore database/credentials are not configured.
- Student identity and authentication are not yet modelled.
- Timezone policy needs an explicit decision before production persistence.

## Priority order

1. Install/configure Firestore SDK and emulator or project credentials, then verify the adapter.
2. Add authenticated student identity and ownership boundaries.
3. Add ADK/Gemini adapter around the tested decision contract.
4. Add a route/context adapter boundary for the next commitment.
5. Add a real Flutter client for the commitment endpoints.
