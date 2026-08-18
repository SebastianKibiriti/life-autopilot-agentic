# Backend

The current backend is FastAPI under `backend/app/`. `main.py` exposes health and evaluation endpoints; `planner.py` owns deterministic timing; `agent.py` owns the local bounded policy; `models.py` owns the current Pydantic contract.

