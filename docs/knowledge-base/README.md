# Life Autopilot project knowledge base

This directory is the durable project context for future coding agents. Read it before making architectural or product changes. It is explicit about what is implemented, what is planned, and what remains unverified.

## Start here

1. [Current state](CURRENT_STATE.md) — authoritative snapshot of the repository today.
2. [Project overview](PROJECT_OVERVIEW.md) — product purpose, user, hackathon fit, and demo story.
3. [Architecture](ARCHITECTURE.md) — current implementation and target Google Cloud design.
4. [Agent behavior](AGENT_BEHAVIOR.md) — state machine, decisions, timing rules, and autonomous loop.
5. [API contract](API_CONTRACT.md) — currently implemented backend endpoint.
6. [Domain model](DOMAIN_MODEL.md) — implemented and planned entities.
7. [Roadmap](ROADMAP.md) — sequenced build plan and acceptance gates.
8. [Development workflow](DEVELOPMENT_WORKFLOW.md) — how to work safely in this repository.
9. [Testing](TESTING.md) — verification commands and known limitations.
10. [Decisions](DECISIONS.md) — important choices and their rationale.
11. [Disclosure](DISCLOSURE.md) — fresh-build and reuse record for the hackathon.
12. [Knowledge-base build prompt](KNOWLEDGE_BASE_BUILD_PROMPT.md) — the maintenance specification that created this system.

## Subsystem references

The following focused pages are maintained as concise entry points or aliases to the authoritative pages above:

- [Product vision](PRODUCT_VISION.md)
- [Hackathon context](HACKATHON_CONTEXT.md)
- [Agent design](AGENT_DESIGN.md)
- [Data model](DATA_MODEL.md)
- [Autonomous workflow](AUTONOMOUS_WORKFLOW.md)
- [Services and integrations](SERVICES_AND_INTEGRATIONS.md)
- [Mobile app](MOBILE_APP.md)
- [Backend](BACKEND.md)
- [Decision engine](DECISION_ENGINE.md)
- [Memory and learning](MEMORY_AND_LEARNING.md)
- [Security and privacy](SECURITY_AND_PRIVACY.md)
- [Testing strategy](TESTING_STRATEGY.md)
- [Demo and submission](DEMO_AND_SUBMISSION.md)
- [Development history](DEVELOPMENT_HISTORY.md)
- [Known issues](KNOWN_ISSUES.md)
- [Glossary](GLOSSARY.md)

## Authority and update rule

`CURRENT_STATE.md` is the source of truth for implementation status. The roadmap, architecture, and behavior documents describe the intended system, but they must label future work as planned. When code changes, update the relevant knowledge-base page in the same change whenever possible.

The knowledge base must never claim that Gemini, ADK, Firestore, Cloud Run, Routes, Places, authentication, notifications, or timetable extraction are working until the repository contains the integration and a verification record exists.

## Last reviewed

2026-08-18 — initial knowledge base created from the repository, the project roadmap, and `KNOWLEDGE_BASE_BUILD_PROMPT.md`.
