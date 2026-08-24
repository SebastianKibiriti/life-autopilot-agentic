import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

from fastapi import Depends, FastAPI, HTTPException, Path, Query, status

from .agent import autonomous_evaluate, evaluate
from .location import InMemoryLocationRepository, FirestoreLocationRepository
from .models import (
    Commitment,
    CommitmentCreate,
    EvaluationRequest,
    EvaluationResponse,
    LearnRequest,
    Location,
    AgentEvent,
    TimetableExtractRequest,
    TimetableExtractResponse,
)
from .notifications import NotificationService
from .repositories import (
    CommitmentRepository,
    InMemoryCommitmentRepository,
    FirestoreCommitmentRepository,
    InMemoryAgentEventRepository,
    FirestoreAgentEventRepository,
    InMemoryPreparationProfileRepository,
    FirestorePreparationProfileRepository,
)
from .schedule import get_next_commitment
from .scheduler import AgentScheduler
from .timetable import extract_timetable

agent_scheduler: AgentScheduler | None = None


def _scheduler_tick(now: datetime) -> None:
    for student_id in commitment_repository.list_student_ids():
        commitment = get_next_commitment(commitment_repository, student_id=student_id, now=now)
        if commitment is None:
            continue
        autonomous_evaluate(
            student_id=student_id,
            now=now,
            commitment=commitment,
            current_location=location_repository.get_current_location(student_id),
            preparation_profile=profile_repository.get_profile(student_id, destination_key="default"),
            student_has_started_moving=False,
            event_repo=event_repository,
            notification_service=notification_service,
        )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global agent_scheduler
    enabled = os.getenv("AGENT_SCHEDULER_ENABLED", "false").lower() == "true"
    if enabled:
        interval = int(os.getenv("AGENT_SCHEDULER_INTERVAL_SECONDS", "60"))
        agent_scheduler = AgentScheduler(interval_seconds=interval, tick=_scheduler_tick)
        agent_scheduler.start()
    try:
        yield
    finally:
        if agent_scheduler is not None:
            agent_scheduler.stop()


app = FastAPI(title="Life Autopilot Agentic", version="0.2.0", lifespan=lifespan)

# ─── Repository wiring ────────────────────────────────────────────────────────
use_firestore = os.getenv("USE_FIRESTORE", "false").lower() == "true"

if use_firestore:
    from google.cloud import firestore as _firestore
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    database_id = os.getenv("FIRESTORE_DATABASE", "(default)")
    _fs_client = _firestore.Client(project=project_id, database=database_id)
    commitment_repository = FirestoreCommitmentRepository(_fs_client)
    location_repository = FirestoreLocationRepository(_fs_client)
    event_repository = FirestoreAgentEventRepository(_fs_client)
    profile_repository = FirestorePreparationProfileRepository(_fs_client)
else:
    _fs_client = None
    commitment_repository = InMemoryCommitmentRepository()
    location_repository = InMemoryLocationRepository()
    event_repository = InMemoryAgentEventRepository()
    profile_repository = InMemoryPreparationProfileRepository()

notification_service = NotificationService(event_repository)


# ─── Dependency providers ──────────────────────────────────────────────────────
def get_commitment_repository() -> CommitmentRepository:
    return commitment_repository


def get_location_repository():
    return location_repository


def get_event_repository():
    return event_repository


def get_profile_repository():
    return profile_repository


def get_notification_service() -> NotificationService:
    return notification_service


def validate_student_id(student_id: str = Path(min_length=1)) -> str:
    cleaned = student_id.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="student_id must not be empty")
    return cleaned


# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "life-autopilot-agentic"}


# ─── Commitments ──────────────────────────────────────────────────────────────
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
    return get_next_commitment(repository, student_id=student_id, now=evaluation_time)


# ─── Location ─────────────────────────────────────────────────────────────────
@app.post(
    "/api/v1/students/{student_id}/location",
    response_model=Location,
    status_code=status.HTTP_201_CREATED,
)
def update_location(
    payload: Location,
    student_id: str = Depends(validate_student_id),
    loc_repo=Depends(get_location_repository),
) -> Location:
    return loc_repo.save_location(student_id, payload)


@app.get(
    "/api/v1/students/{student_id}/location",
    response_model=Location | None,
)
def get_location(
    student_id: str = Depends(validate_student_id),
    loc_repo=Depends(get_location_repository),
) -> Location | None:
    return loc_repo.get_current_location(student_id)


# ─── Activity timeline ────────────────────────────────────────────────────────
@app.get(
    "/api/v1/students/{student_id}/events",
    response_model=list[AgentEvent],
)
def list_events(
    student_id: str = Depends(validate_student_id),
    limit: int = Query(default=50, ge=1, le=200),
    ev_repo=Depends(get_event_repository),
) -> list[AgentEvent]:
    return ev_repo.list_events(student_id, limit=limit)


# ─── Autonomous evaluation ────────────────────────────────────────────────────
@app.post(
    "/api/v1/students/{student_id}/evaluate",
    response_model=EvaluationResponse,
)
def evaluate_autonomous(
    student_id: str = Depends(validate_student_id),
    now: datetime | None = Query(default=None),
    student_has_started_moving: bool = Query(default=False),
    commitment_repo: CommitmentRepository = Depends(get_commitment_repository),
    loc_repo=Depends(get_location_repository),
    ev_repo=Depends(get_event_repository),
    prof_repo=Depends(get_profile_repository),
    notif_service: NotificationService = Depends(get_notification_service),
) -> EvaluationResponse:
    evaluation_time = now or datetime.now(timezone.utc)
    commitment = get_next_commitment(
        commitment_repo, student_id=student_id, now=evaluation_time
    )
    if commitment is None:
        raise HTTPException(
            status_code=404, detail="No upcoming active commitment found for this student."
        )
    current_location = loc_repo.get_current_location(student_id)
    profile = prof_repo.get_profile(student_id, destination_key="default")

    return autonomous_evaluate(
        student_id=student_id,
        now=evaluation_time,
        commitment=commitment,
        current_location=current_location,
        preparation_profile=profile,
        student_has_started_moving=student_has_started_moving,
        event_repo=ev_repo,
        notification_service=notif_service,
    )


# ─── Legacy evaluation endpoint (kept for tests) ──────────────────────────────
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


# ─── Learning ─────────────────────────────────────────────────────────────────
@app.post(
    "/api/v1/students/{student_id}/learn",
    response_model=dict,
)
def update_learning(
    payload: LearnRequest,
    student_id: str = Depends(validate_student_id),
    prof_repo=Depends(get_profile_repository),
) -> dict:
    updated = prof_repo.update_with_observation(
        student_id=student_id,
        destination_key=payload.destination_key,
        observed_prep_minutes=payload.actual_prep_minutes,
    )
    return {
        "student_id": student_id,
        "destination_key": updated.destination_key,
        "average_prep_minutes": updated.average_prep_minutes,
        "confidence": updated.confidence,
        "sample_count": updated.sample_count,
    }


# ─── Timetable extraction ─────────────────────────────────────────────────────
@app.post(
    "/api/v1/students/{student_id}/timetable/extract",
    response_model=TimetableExtractResponse,
)
def timetable_extract(
    student_id: str = Depends(validate_student_id),
    payload: TimetableExtractRequest = ...,
) -> TimetableExtractResponse:
    return extract_timetable(payload)


@app.post(
    "/api/v1/students/{student_id}/timetable/confirm",
    response_model=list[Commitment],
    status_code=status.HTTP_201_CREATED,
)
def timetable_confirm(
    payload: TimetableExtractResponse,
    student_id: str = Depends(validate_student_id),
    repository: CommitmentRepository = Depends(get_commitment_repository),
) -> list[Commitment]:
    saved = []
    for item in payload.commitments:
        c = Commitment(
            title=item.title,
            start_time=item.start_time,
            destination=item.destination,
        )
        saved.append(repository.save(student_id, c))
    return saved
