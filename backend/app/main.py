from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Path, Query, status

from .agent import evaluate
from .models import Commitment, CommitmentCreate, EvaluationRequest, EvaluationResponse
from .repositories import CommitmentRepository, InMemoryCommitmentRepository
from .schedule import get_next_commitment

app = FastAPI(title="Life Autopilot Agentic", version="0.1.0")
commitment_repository = InMemoryCommitmentRepository()


def get_commitment_repository() -> CommitmentRepository:
    return commitment_repository


def validate_student_id(student_id: str = Path(min_length=1)) -> str:
    cleaned = student_id.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="student_id must not be empty")
    return cleaned


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "life-autopilot-agentic"}


@app.post(
    "/api/v1/students/{student_id}/commitments",
    response_model=Commitment,
    status_code=status.HTTP_201_CREATED,
)
def create_commitment(
    payload: CommitmentCreate,
    student_id: str = Depends(validate_student_id),
    repository: CommitmentRepository = Depends(get_commitment_repository),
) -> Commitment:
    return repository.save(student_id, payload.to_commitment())


@app.get(
    "/api/v1/students/{student_id}/commitments",
    response_model=list[Commitment],
)
def list_commitments(
    student_id: str = Depends(validate_student_id),
    repository: CommitmentRepository = Depends(get_commitment_repository),
) -> list[Commitment]:
    return repository.list_for_student(student_id)


@app.get(
    "/api/v1/students/{student_id}/commitments/next",
    response_model=Commitment | None,
)
def next_commitment(
    student_id: str = Depends(validate_student_id),
    now: datetime | None = Query(default=None),
    repository: CommitmentRepository = Depends(get_commitment_repository),
) -> Commitment | None:
    evaluation_time = now or datetime.now(timezone.utc)
    return get_next_commitment(
        repository, student_id=student_id, now=evaluation_time
    )


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
