# Life Autopilot — Collaborative Partner

## One-line summary

A persistent personal companion that learns routines and preferences, combines schedule and location context, and proactively takes lightweight actions.

## Problem

Students and busy working adults coordinate commitments across calendars,
locations, preparation habits, and communication tools. A calendar can show
that something starts at 14:00, but it cannot determine when the person should
prepare, leave, re-plan, or ask for help. Generic reminders also forget the
user’s preferences and past feedback.

## Value proposition

Life Autopilot reduces coordination friction by remembering how a person works,
grounding suggestions in real context, and proactively turning that context
into useful next steps. It learns without silently changing production behavior:
user preferences adapt through feedback, while policy improvements are
evaluated and explicitly promoted.

## What the demo proves

The nutrition-student scenario imports timetable and fitness events, resolves a
classroom through a curated campus graph, retrieves the student’s Firestore
profile, generates a multi-option fitness suggestion with Gemini, stores it,
answers a follow-up from the stored response, and saves the selected option to
Google Calendar. Separate lecture and supplier scenarios prove the same agent
can monitor commitments, calculate travel context, notify, and re-plan.

## AI and Google Cloud

Gemini 3.5 Flash runs through Vertex AI for contextual notification copy,
timetable extraction, and structured companion suggestions. The Google Gen AI
SDK provides the model boundary. Cloud Run hosts the FastAPI backend. Firestore
stores user-scoped profiles, suggestions, commitments, events, policies, and
evaluation records. Google Calendar and Gmail provide visible lightweight
actions.

## Self-evolution

The agent evaluates final responses, safety constraints, and structured agent
outcomes against golden scenarios. It can propose a new policy version, compare
the candidate score with the active version, and promote only an eligible
candidate. Runtime requests never rewrite the active policy, and private
user-memory records remain separate from global policy records.

## Architecture

See [architecture diagram](docs/ARCHITECTURE_DIAGRAM.md) and the [knowledge base](docs/knowledge-base/README.md).

## Reproduction

Follow the [README spin-up instructions](README.md), run the test suite, then
run the four scenario scripts in `scripts/`. The deployed API is available at
https://life-autopilot-agentic-725797619054.us-central1.run.app/docs.

## Limitations

The current demo uses curated campus facts, simulated locations where needed,
and local OAuth files for Calendar/Gmail. It does not claim access to private
university portals, WhatsApp, banking, POS, printing, or device-density data.

## Links to complete before Devpost

- Repository: https://github.com/SebastianKibiriti/life-autopilot-agentic
- Public demo URL: https://life-autopilot-agentic-725797619054.us-central1.run.app
- Demo video URL: TODO
- Architecture image: docs/ARCHITECTURE_DIAGRAM.md
