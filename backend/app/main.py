from fastapi import FastAPI

from .agent import evaluate
from .models import EvaluationRequest, EvaluationResponse

app = FastAPI(title="Life Autopilot Agentic", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "life-autopilot-agentic"}


@app.post("/api/v1/agent/evaluate", response_model=EvaluationResponse)
def evaluate_agent(request: EvaluationRequest) -> EvaluationResponse:
    plan, decision, reason = evaluate(request)
    return EvaluationResponse(
        commitment_title=request.commitment.title,
        preparation_at=plan.preparation_at,
        leave_at=plan.leave_at,
        decision=decision,
        reason=reason,
        route_provider=plan.route_provider,
    )

