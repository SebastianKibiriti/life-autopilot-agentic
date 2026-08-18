# Life Autopilot Agentic

Life Autopilot is a Taskmaster-style agent for keeping a student on schedule. It watches an upcoming commitment and the student's context, calculates when preparation and departure must happen, chooses an intervention, and records the operational outcome.

This is a new hackathon project inspired by the historical Life Autopilot product. The implementation is being rebuilt in this repository for the All Things Agentic Hackathon.

## Current slice

The first vertical slice is local and deliberately deterministic:

- Flutter mobile shell;
- FastAPI backend;
- structured student and commitment models;
- commitment repository interface with an in-memory fake;
- Firestore-shaped repository adapter with injected client boundary;
- next-commitment query service;
- student commitment create/list/next API endpoints;
- pure departure-planning service;
- Taskmaster decision contract;
- `/health` and `/api/v1/agent/evaluate` endpoints;
- unit tests for normal, late, and missing-route conditions.

Google ADK, Gemini on Vertex AI, Firestore, Routes, Places, and Cloud Run are represented as boundaries in the architecture and will be connected after the local contract is stable.

## Run the backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

Then open `http://127.0.0.1:8000/docs`.

Run the tests with:

```bash
PYTHONPATH=backend python3 -m unittest discover -s backend/tests -p 'test_*.py'
```

## Run the mobile shell

```bash
cd mobile
flutter pub get
flutter run
```

## Hackathon alignment

The target track is **The Taskmaster**. The core loop is:

```text
Observe → Calculate → Reason → Act → Monitor → Re-evaluate → Learn
```

The intended Google stack is Gemini via Vertex AI, Google ADK, Firestore, and Cloud Run. No Devpost registration or submission has been performed from this workspace yet.

## Project knowledge base

Start with [docs/knowledge-base/README.md](docs/knowledge-base/README.md). It is the durable context for future coding agents and includes the current implementation state, architecture, agent behavior, API contract, roadmap, testing workflow, decisions, disclosure record, and the prompt that defines how the knowledge base must be maintained.
