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
from .calendar import GoogleCalendarProvider, sync_calendar_events
from .location import InMemoryLocationRepository, FirestoreLocationRepository
from .models import (
    Commitment,
    CommitmentCreate,
    EvaluationRequest,
    EvaluationResponse,
    LearnRequest,
    Location,
    AgentEvent,
    CalendarSyncRequest,
    CalendarActionRequest,
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
from .companion import CompanionMemory, create_fitness_suggestion
from .campus import resolve_campus
from .gemini import GeminiClient
from .models import CompanionProfile, CompanionProfileUpdate, CompanionSuggestion, CampusPlace, CompanionCalendarSaveRequest

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
companion_memory = CompanionMemory(_fs_client if use_firestore else None)
companion_gemini = GeminiClient()


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


@app.get("/api/v1/students/{student_id}/companion/profile", response_model=CompanionProfile)
def companion_profile(student_id: str = Depends(validate_student_id)):
    return companion_memory.profile(student_id)


@app.put("/api/v1/students/{student_id}/companion/profile", response_model=CompanionProfile)
def update_companion_profile(payload: CompanionProfileUpdate, student_id: str = Depends(validate_student_id)):
    return companion_memory.save_profile(CompanionProfile(student_id=student_id, **payload.model_dump()))


@app.get("/api/v1/campus/resolve", response_model=CampusPlace | None)
def campus_resolve(query: str = Query(min_length=1)):
    return resolve_campus(query)


@app.post("/api/v1/students/{student_id}/companion/fitness-suggestion", response_model=CompanionSuggestion)
def fitness_suggestion(student_id: str = Depends(validate_student_id)):
    profile = companion_memory.profile(student_id)
    generated = companion_gemini.generate_companion_suggestion(profile=profile.model_dump(mode="json"), upcoming_context="upcoming nutrition timetable and fitness calendar events")
    suggestion = create_fitness_suggestion(student_id, profile, generated=generated)
    return companion_memory.save_suggestion(suggestion)


@app.get("/api/v1/students/{student_id}/companion/suggestions/{suggestion_id}", response_model=CompanionSuggestion)
def get_companion_suggestion(student_id: str = Depends(validate_student_id), suggestion_id: str = Path(min_length=1)):
    suggestion = companion_memory.get_suggestion(student_id, suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return suggestion


@app.post("/api/v1/students/{student_id}/companion/suggestions/{suggestion_id}/calendar")
def save_suggestion_to_calendar(payload: CompanionCalendarSaveRequest, student_id: str = Depends(validate_student_id), suggestion_id: str = Path(min_length=1)):
    suggestion = companion_memory.get_suggestion(student_id, suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "client_secret_725797619054-gutqcc15kok56n1r83hodd9u2j6iual7.apps.googleusercontent.com.json")
    provider = GoogleCalendarProvider(credentials_path=credentials_path, token_path=os.getenv("GOOGLE_CALENDAR_TOKEN", "google-calendar-token.json"), calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"))
    return provider.create_action(action_id=f"companion-{suggestion.id}", title=suggestion.main_recommendation, start_time=payload.start_time, description=suggestion.rationale)


@app.get("/api/v1/students/{student_id}/companion/suggestions/{suggestion_id}/follow-up")
def companion_follow_up(question: str = Query(min_length=1), student_id: str = Depends(validate_student_id), suggestion_id: str = Path(min_length=1)):
    suggestion = companion_memory.get_suggestion(student_id, suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    q = question.lower()
    for key, answer in suggestion.follow_up_answers.items():
        if key in q:
            return {"answer": answer, "source": "stored_suggestion", "gemini_called": False}
    return {"answer": "I can explain the recommendation, duration, or alternatives.", "source": "stored_suggestion", "gemini_called": False}


# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "life-autopilot-agentic"}


@app.post(
    "/api/v1/students/{student_id}/calendar/sync",
    response_model=list[Commitment],
    status_code=status.HTTP_200_OK,
)
def calendar_sync(
    payload: CalendarSyncRequest,
    student_id: str = Depends(validate_student_id),
    repository: CommitmentRepository = Depends(get_commitment_repository),
) -> list[Commitment]:
    """Import normalized calendar events; the external provider is replaceable."""
    return sync_calendar_events(
        student_id=student_id,
        events=payload.events,
        commitment_repository=repository,
    )


@app.post(
    "/api/v1/students/{student_id}/calendar/sync/google",
    response_model=list[Commitment],
)
def google_calendar_sync(
    student_id: str = Depends(validate_student_id),
    repository: CommitmentRepository = Depends(get_commitment_repository),
) -> list[Commitment]:
    credentials_path = os.getenv(
        "GOOGLE_CALENDAR_CREDENTIALS",
        "client_secret_725797619054-gutqcc15kok56n1r83hodd9u2j6iual7.apps.googleusercontent.com.json",
    )
    provider = GoogleCalendarProvider(
        credentials_path=credentials_path,
        token_path=os.getenv("GOOGLE_CALENDAR_TOKEN", "google-calendar-token.json"),
        calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
    )
    return sync_calendar_events(
        student_id=student_id,
        events=provider.upcoming_events(student_id=student_id),
        commitment_repository=repository,
    )


@app.post("/api/v1/students/{student_id}/calendar/actions")
def calendar_action(
    payload: CalendarActionRequest,
    student_id: str = Depends(validate_student_id),
) -> dict:
    """Create an autonomous preparation/departure action in Google Calendar."""
    del student_id
    credentials_path = os.getenv(
        "GOOGLE_CALENDAR_CREDENTIALS",
        "client_secret_725797619054-gutqcc15kok56n1r83hodd9u2j6iual7.apps.googleusercontent.com.json",
    )
    provider = GoogleCalendarProvider(
        credentials_path=credentials_path,
        token_path=os.getenv("GOOGLE_CALENDAR_TOKEN", "google-calendar-token.json"),
        calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
    )
    return provider.create_action(
        action_id=f"life-autopilot-{payload.commitment_id}",
        title=payload.title,
        start_time=payload.start_time,
        description=payload.description,
    )


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


@app.post(
    "/api/v1/students/{student_id}/autonomous-cycle",
    response_model=list[EvaluationResponse],
)
def autonomous_cycle(
    student_id: str = Depends(validate_student_id),
    now: datetime | None = Query(default=None),
    student_has_started_moving: bool = Query(default=False),
    commitment_repo: CommitmentRepository = Depends(get_commitment_repository),
    loc_repo=Depends(get_location_repository),
    ev_repo=Depends(get_event_repository),
    prof_repo=Depends(get_profile_repository),
    notif_service: NotificationService = Depends(get_notification_service),
) -> list[EvaluationResponse]:
    """Evaluate every active commitment in one autonomous background cycle."""
    evaluation_time = now or datetime.now(timezone.utc)
    current_location = loc_repo.get_current_location(student_id)
    results: list[EvaluationResponse] = []
    for commitment in commitment_repo.list_for_student(student_id):
        status_value = getattr(commitment.status, "value", commitment.status)
        if status_value != "active":
            continue
        profile = prof_repo.get_profile(student_id, destination_key="default")
        results.append(
            autonomous_evaluate(
                student_id=student_id,
                now=evaluation_time,
                commitment=commitment,
                current_location=current_location,
                preparation_profile=profile,
                student_has_started_moving=student_has_started_moving,
                event_repo=ev_repo,
                notification_service=notif_service,
            )
        )
    return results


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
