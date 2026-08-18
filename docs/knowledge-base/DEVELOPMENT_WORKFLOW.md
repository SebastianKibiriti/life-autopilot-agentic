# Development workflow

## Before changing code

1. Read this knowledge-base index and `CURRENT_STATE.md`.
2. Identify whether the request changes implemented behavior, planned architecture, or documentation only.
3. Check the current tests and working tree.
4. Keep the Taskmaster scope narrow; do not add a generic chatbot or unrelated productivity features.

## During implementation

- Keep arithmetic in deterministic services.
- Introduce provider interfaces before provider-specific code.
- Prefer local fakes and fixtures so behavior can be tested without cloud credentials.
- Model explicit states and failure paths.
- Make external actions idempotent where retries are possible.
- Do not persist or display private chain-of-thought.
- Keep secrets in environment configuration.
- Update docs in the same change when behavior or contracts change.

## Verification expectation

Every slice should have a focused automated test and, when applicable, an API or UI smoke check. A provider integration is not complete until its success path and failure path are both demonstrated. A planned item must not be marked implemented based only on a stub or import.

## Knowledge-base maintenance

When a meaningful feature lands:

1. Update `CURRENT_STATE.md`.
2. Update the relevant architecture, behavior, domain, or API page.
3. Update `ROADMAP.md` checkboxes and acceptance notes.
4. Add a decision to `DECISIONS.md` if the change resolves a non-obvious tradeoff.
5. Add verification commands and results to `TESTING.md`.
6. Add a dated entry to `CHANGELOG.md`.
7. Check `DISCLOSURE.md` if code or data came from outside this fresh repository.

## Handoff protocol for another coding agent

The next agent should report:

- the current baseline commit and working-tree status;
- which knowledge-base pages were read;
- which roadmap item it is taking;
- files it expects to change;
- verification it will run;
- any assumption that is not yet confirmed.

At the end, it should update the knowledge base before handing work back.

