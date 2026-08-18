from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AgentDecision(str, Enum):
    NO_ACTION = "NO_ACTION"
    PREPARE = "PREPARE"
    LEAVE = "LEAVE"
    REPLAN = "REPLAN"
    ESCALATE = "ESCALATE"


class CommitmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Commitment(BaseModel):
    id: str | None = None
    title: str = Field(min_length=1)
    start_time: datetime
    destination: str = Field(min_length=1)
    status: CommitmentStatus = CommitmentStatus.ACTIVE


class EvaluationRequest(BaseModel):
    now: datetime
    commitment: Commitment
    travel_minutes: int | None = Field(default=None, ge=0)
    preparation_minutes: int = Field(default=15, ge=0)
    arrival_buffer_minutes: int = Field(default=5, ge=0)
    student_has_started_moving: bool = False


class EvaluationResponse(BaseModel):
    commitment_title: str
    preparation_at: datetime | None
    leave_at: datetime | None
    decision: AgentDecision
    reason: str
    route_provider: str
