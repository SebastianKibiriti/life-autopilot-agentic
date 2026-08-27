from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class AgentDecision(str, Enum):
    NO_ACTION = "NO_ACTION"
    PREPARE = "PREPARE"
    LEAVE = "LEAVE"
    REPLAN = "REPLAN"
    ESCALATE = "ESCALATE"


class AgentPhase(str, Enum):
    IDLE = "IDLE"
    COMMITMENT_UPCOMING = "COMMITMENT_UPCOMING"
    PREPARATION_WINDOW = "PREPARATION_WINDOW"
    LEAVE_WINDOW = "LEAVE_WINDOW"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    COMPLETE = "COMPLETE"
    RUNNING_LATE = "RUNNING_LATE"
    LOCATION_UNAVAILABLE = "LOCATION_UNAVAILABLE"


class CommitmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CalendarEvent(BaseModel):
    id: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    start_time: datetime
    location: str | None = None
    status: str = "confirmed"

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value: datetime) -> datetime:
        return require_timezone(value)


class CalendarSyncRequest(BaseModel):
    events: list[CalendarEvent] = Field(default_factory=list)


class CalendarActionRequest(BaseModel):
    commitment_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    start_time: datetime
    description: str = ""

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value: datetime) -> datetime:
        return require_timezone(value)


class LocationProvider(str, Enum):
    GPS = "gps"
    SIMULATED = "simulated"
    UNAVAILABLE = "unavailable"


class DestinationProvider(str, Enum):
    PLACES = "places"
    MANUAL = "manual"
    CACHED = "cached"


class RouteProvider(str, Enum):
    ROUTES = "routes"
    FALLBACK = "fallback"


class EventOutcome(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    SUPERSEDED = "superseded"


def require_timezone(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError("datetime values must be timezone-aware")
    return value


class Location(BaseModel):
    latitude: float
    longitude: float
    accuracy_meters: float | None = None
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider: LocationProvider = LocationProvider.SIMULATED

    @field_validator("captured_at")
    @classmethod
    def validate_captured_at(cls, value: datetime) -> datetime:
        return require_timezone(value)


class Destination(BaseModel):
    label: str
    latitude: float
    longitude: float
    formatted_address: str | None = None
    resolution_confidence: float = 1.0
    provider: DestinationProvider = DestinationProvider.MANUAL


class TravelEstimate(BaseModel):
    origin: Location
    destination: Destination
    mode: str = "walking"
    distance_meters: int
    duration_seconds: int
    duration_minutes: int
    provider: RouteProvider = RouteProvider.FALLBACK
    estimated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PreparationProfile(BaseModel):
    student_id: str
    destination_key: str = "default"
    average_prep_minutes: int = 15
    arrival_buffer_minutes: int = 5
    usual_mode: str = "walking"
    confidence: float = 0.5
    sample_count: int = 1
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Commitment(BaseModel):
    id: str | None = None
    title: str = Field(min_length=1)
    start_time: datetime
    destination: str = Field(min_length=1)
    destination_coordinates: Location | None = None
    status: CommitmentStatus = CommitmentStatus.ACTIVE

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value: datetime) -> datetime:
        return require_timezone(value)


class CommitmentCreate(BaseModel):
    title: str = Field(min_length=1)
    start_time: datetime
    destination: str = Field(min_length=1)
    status: CommitmentStatus = CommitmentStatus.ACTIVE

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value: datetime) -> datetime:
        return require_timezone(value)

    def to_commitment(self) -> Commitment:
        return Commitment(**self.model_dump())


class AgentEvent(BaseModel):
    id: str | None = None
    student_id: str
    commitment_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decision: AgentDecision
    reason: str
    action: str | None = None
    outcome: EventOutcome = EventOutcome.DELIVERED
    notification_title: str | None = None
    notification_body: str | None = None


class StudentContext(BaseModel):
    student_id: str
    current_location: Location | None = None
    next_commitment: Commitment | None = None
    destination: Destination | None = None
    travel_estimate: TravelEstimate | None = None
    preparation_profile: PreparationProfile | None = None
    phase: AgentPhase = AgentPhase.IDLE


class EvaluationRequest(BaseModel):
    now: datetime
    commitment: Commitment
    travel_minutes: int | None = Field(default=None, ge=0)
    preparation_minutes: int = Field(default=15, ge=0)
    arrival_buffer_minutes: int = Field(default=5, ge=0)
    student_has_started_moving: bool = False

    @field_validator("now")
    @classmethod
    def validate_now(cls, value: datetime) -> datetime:
        return require_timezone(value)


class EvaluationResponse(BaseModel):
    commitment_title: str
    preparation_at: datetime | None
    leave_at: datetime | None
    decision: AgentDecision
    reason: str
    route_provider: str
    notification_sent: bool = False
    notification_body: str | None = None


class TimetableItem(BaseModel):
    title: str
    start_time: datetime
    destination: str

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value: datetime) -> datetime:
        return require_timezone(value)


class TimetableExtractRequest(BaseModel):
    content: str | None = None
    mime_type: str = "text/plain"
    image_base64: str | None = None


class TimetableExtractResponse(BaseModel):
    commitments: list[TimetableItem]
    notes: str | None = None


class CompanionProfile(BaseModel):
    student_id: str
    interests: list[str] = Field(default_factory=list)
    preferred_activities: list[str] = Field(default_factory=list)
    accepted_suggestions: list[str] = Field(default_factory=list)
    rejected_suggestions: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompanionProfileUpdate(BaseModel):
    interests: list[str] = Field(default_factory=list)
    preferred_activities: list[str] = Field(default_factory=list)
    accepted_suggestions: list[str] = Field(default_factory=list)
    rejected_suggestions: list[str] = Field(default_factory=list)


class CampusPlace(BaseModel):
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    latitude: float
    longitude: float
    confidence: float = Field(ge=0, le=1)
    source: str = "curated"


class CompanionSuggestion(BaseModel):
    id: str
    student_id: str
    main_recommendation: str
    alternatives: list[str] = Field(default_factory=list)
    rationale: str
    estimated_duration_minutes: int = Field(ge=1)
    location: str
    preparation: list[str] = Field(default_factory=list)
    uncertainty: str | None = None
    follow_up_answers: dict[str, str] = Field(default_factory=dict)
    source_memory: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompanionCalendarSaveRequest(BaseModel):
    start_time: datetime

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value: datetime) -> datetime:
        return require_timezone(value)


class PolicyStatus(str, Enum):
    CANDIDATE = "candidate"
    ACTIVE = "active"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


class AgentPolicy(BaseModel):
    policy_id: str
    version: int
    content: str
    score: float = 0.0
    status: PolicyStatus = PolicyStatus.CANDIDATE
    parent_version: int | None = None
    reason: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluationCase(BaseModel):
    case_id: str
    title: str
    category: str
    input_context: dict = Field(default_factory=dict)
    expected_behavior: str
    safety_constraints: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    case_id: str
    passed: bool
    score: float = Field(ge=0, le=1)
    checks: dict[str, bool] = Field(default_factory=dict)
    failure_reason: str | None = None


class EvaluationRun(BaseModel):
    run_id: str
    policy_version: int
    results: list[EvaluationResult] = Field(default_factory=list)
    overall_score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvolutionProposal(BaseModel):
    proposal_id: str
    candidate: AgentPolicy
    baseline_score: float
    candidate_score: float
    eligible: bool
    reason: str
    status: str = "proposed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearnRequest(BaseModel):
    actual_prep_minutes: int = Field(ge=0)
    actual_start_moving_at: datetime
    destination_key: str = "default"

    @field_validator("actual_start_moving_at")
    @classmethod
    def validate_moved_at(cls, value: datetime) -> datetime:
        return require_timezone(value)
