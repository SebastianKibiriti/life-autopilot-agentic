from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class DeparturePlan:
    preparation_at: datetime | None
    leave_at: datetime | None
    is_late: bool
    route_provider: str


def plan_departure(
    *,
    now: datetime,
    commitment_start: datetime,
    travel_minutes: int | None,
    preparation_minutes: int,
    arrival_buffer_minutes: int,
) -> DeparturePlan:
    """Calculate thresholds without asking a language model to do arithmetic."""
    if travel_minutes is None:
        return DeparturePlan(None, None, False, "unavailable")

    leave_at = commitment_start - timedelta(
        minutes=travel_minutes + arrival_buffer_minutes
    )
    preparation_at = leave_at - timedelta(minutes=preparation_minutes)
    return DeparturePlan(
        preparation_at=preparation_at,
        leave_at=leave_at,
        is_late=now >= leave_at,
        route_provider="provided",
    )

