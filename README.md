# Life Autopilot Agentic

Life Autopilot is a persistent Collaborative Partner that learns a student's routines and context, then proactively coordinates schedules, travel, preparation, and personalized suggestions.

This is a new hackathon project inspired by the historical Life Autopilot product. The implementation is being rebuilt in this repository for the All Things Agentic Hackathon.

## Current MVP

The first vertical slice is local and deliberately deterministic:

- Flutter mobile shell with a clean analyzer pass;
- FastAPI backend;
- structured student and commitment models;
- commitment repository interface with an in-memory fake;
- Firestore-shaped repository adapter with injected client boundary;
- next-commitment query service;
- student commitment create/list/next API endpoints;
- pure departure-planning service;
- bounded companion decision contract;
- `/health` and `/api/v1/agent/evaluate` endpoints;
- unit tests for normal, late, and missing-route conditions.

Gemini on Vertex AI, Firestore, Routes, Places, and Cloud Run are connected behind optional service boundaries. Deterministic fallbacks keep the demo runnable when external API keys are unavailable.

## Run the backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

Then open `http://127.0.0.1:8000/docs`.

### Reproducible local setup

Prerequisites: Python 3.11+, `curl`, and (for the companion demo) `jq`.

```bash
cd /Users/apple/Documents/Codex/2026-08-18/lo
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
export PYTHONPATH=backend
```

Run without external services using the in-memory fallback:

```bash
USE_FIRESTORE=false .venv/bin/uvicorn app.main:app --app-dir backend --port 8001
```

Verify the backend from another terminal:

```bash
curl http://127.0.0.1:8001/health
```

Open the local Swagger UI at `http://127.0.0.1:8001/docs`.

For Vertex AI, Firestore, Calendar, and Gmail, configure the variables below
before starting Uvicorn. Keep OAuth tokens and client secrets outside Git.

```bash
export USE_FIRESTORE=true
export GOOGLE_CLOUD_PROJECT=gen-lang-client-0563563702
export GOOGLE_CLOUD_LOCATION=global
export GOOGLE_GENAI_USE_VERTEXAI=true
export GEMINI_MODEL=gemini-3.5-flash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/application_default_credentials.json"
export GOOGLE_CALENDAR_CREDENTIALS="$PWD/client_secret_725797619054-gutqcc15kok56n1r83hodd9u2j6iual7.apps.googleusercontent.com.json"
export GOOGLE_CALENDAR_TOKEN="$PWD/google-calendar-token.json"
export GMAIL_NOTIFICATION_TO="your-real-email@gmail.com"
export GMAIL_TOKEN="$PWD/gmail-token.json"
```

The complete test suite is:

```bash
PYTHONPATH=backend .venv/bin/python -m unittest discover -s backend/tests -v
```

Run the reproducible scenarios while the backend is running:

```bash
./scripts/run_sipho_api_demo.sh
./scripts/run_supplier_errand_demo.sh
./scripts/run_nutrition_companion_demo.sh
./scripts/run_self_evolution_demo.sh
```

Use `USE_FIRESTORE=true` to demonstrate persistent user memory and evolution
records. Without it, the same APIs run locally with in-memory repositories.
Calendar and Gmail demos may open an OAuth consent flow on first use.

### Cloud Run deployment

From the repository root:

```bash
gcloud run deploy life-autopilot-agentic \
  --source . \
  --region us-central1 \
  --project gen-lang-client-0563563702 \
  --set-env-vars="USE_FIRESTORE=true,GOOGLE_CLOUD_PROJECT=gen-lang-client-0563563702,GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_VERTEXAI=true,GEMINI_MODEL=gemini-3.5-flash,FIRESTORE_DATABASE=(default)" \
  --allow-unauthenticated
```

Verify the deployed service:

```bash
curl https://life-autopilot-agentic-725797619054.us-central1.run.app/health
```

The deployed Swagger UI is at
`https://life-autopilot-agentic-725797619054.us-central1.run.app/docs`.
Local Calendar/Gmail OAuth token files are not copied to Cloud Run; use
Secret Manager or another production-safe credential flow for deployed
cross-app actions. Never commit `.env`, client-secret JSON, or token files.

Run the tests with:

```bash
PYTHONPATH=backend python3 -m unittest discover -s backend/tests -p 'test_*.py'
```

For the demo, create a commitment through `/docs`, post a location, then call the autonomous evaluation endpoint. The activity timeline at `/api/v1/students/{student_id}/events` shows the agent's decision and notification outcome.

For the Collaborative Partner flow, run
`./scripts/run_nutrition_companion_demo.sh` to demonstrate persistent profile
memory, campus lookup, proactive fitness suggestions, follow-up retrieval, and
Calendar mutation.

The Cloud Run image is defined in `Dockerfile`. Configure the values in `infrastructure/cloud-run.env.example` using Cloud Run environment variables; use the service account's application credentials rather than uploading a local key.

## Run the mobile shell

```bash
cd mobile
flutter pub get
flutter run
```

## Hackathon alignment

The target track is **The Collaborative Partner**. The core loop is:

```text
Observe → Calculate → Reason → Act → Monitor → Re-evaluate → Learn
```

The intended Google stack is Gemini via Vertex AI, Google ADK, Firestore, and Cloud Run. No Devpost registration or submission has been performed from this workspace yet.

## Project knowledge base

Start with [docs/knowledge-base/README.md](docs/knowledge-base/README.md). It is the durable context for future coding agents and includes the current implementation state, architecture, agent behavior, API contract, roadmap, testing workflow, decisions, disclosure record, and the prompt that defines how the knowledge base must be maintained.
