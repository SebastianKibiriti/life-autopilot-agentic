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

## Solution

Life Autopilot is a backend-first Collaborative Partner. It observes a user's
commitments and context, retrieves relevant memory, calculates preparation and
travel implications, and chooses a bounded response: prepare, leave, re-plan,
notify, suggest, or escalate. The result is visible through the API, audit
events, Gmail, and Google Calendar rather than being only a chat reply.

## Why this matters

The project addresses the small coordination failures that cause missed
classes, late errands, and abandoned personal goals. Its value is continuity:
the companion remembers preferences and feedback, then uses that history to
make the next intervention more useful while keeping uncertain routes and
unsafe actions conservative.

## How we used AI

Gemini 3.5 Flash, accessed through Vertex AI and the Google Gen AI SDK, is used
for structured companion suggestions, contextual notification wording, and
context synthesis. Responses are validated and normalized before they reach
the application. Deterministic code remains responsible for timing arithmetic,
schema safety, route grounding, idempotency, and promotion gates.

## How we used Codex

Codex was used to shape the product around the Collaborative Partner track,
implement the FastAPI services and integrations, create the Flutter shell,
write documentation and demo scripts, diagnose malformed model output, and
build automated tests for personalization, auditability, and bounded policy
evolution.

## Key features

- Persistent user-scoped profile and feedback memory.
- Curated campus graph with aliases such as `N204`.
- Schedule-aware preparation, departure, re-planning, and escalation.
- Structured multi-option suggestions with stored follow-up answers.
- Gmail notifications and Google Calendar actions when OAuth is configured.
- Firestore persistence in production mode, with a local fallback.
- Offline evaluate → propose → score → explicitly promote self-evolution.
- Structured audit events showing context, decisions, tools, and side effects.

## Testing instructions

```bash
git clone https://github.com/SebastianKibiriti/life-autopilot-agentic.git
cd life-autopilot-agentic
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
PYTHONPATH=backend python -m unittest discover -s backend/tests -p 'test_*.py' -v
```

For the live API, open the [hosted Swagger UI](https://life-autopilot-agentic-725797619054.us-central1.run.app/docs).
The repository README contains local startup, integration credentials, and
scenario-demo commands.

## Public demo link

https://life-autopilot-agentic-725797619054.us-central1.run.app/docs

## Public repository link

https://github.com/SebastianKibiriti/life-autopilot-agentic

## Demo video

TODO: Add the public YouTube or Vimeo URL. The recording should show Cloud Run,
the hosted Swagger/API flow, a personalized suggestion, Calendar/Gmail side
effects, and the bounded self-evolution evaluation.

## Screenshot shot list

1. Cloud Run service and deployed revision.
2. Hosted Swagger UI and a successful API response.
3. Firestore profile, suggestion, or audit record.
4. Calendar event created by the companion.
5. Gmail late-arrival notification and policy score comparison.

## Submission readiness notes

The repository, Cloud Run URL, architecture documentation, README setup
instructions, automated tests, and demo scripts are available. Before entering
the Devpost form, verify the deployed revision matches the repository, capture
the evidence above, and add the video URL. Use local OAuth for the recorded
Calendar/Gmail demonstration unless production-safe Cloud Run credentials have
been configured.

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
