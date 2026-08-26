"""Calendar ingestion boundary for the cross-app Taskmaster workflow."""
from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .models import CalendarEvent, Commitment, CommitmentStatus


class CalendarProvider(Protocol):
    def upcoming_events(self, *, student_id: str) -> list[CalendarEvent]:
        """Return normalized upcoming events from an external calendar."""


class InMemoryCalendarProvider:
    """Deterministic provider for local demos and tests."""

    def __init__(self, events: list[CalendarEvent] | None = None) -> None:
        self.events = events or []

    def upcoming_events(self, *, student_id: str) -> list[CalendarEvent]:
        return [event.model_copy(deep=True) for event in self.events]


def sync_calendar_events(
    *,
    student_id: str,
    events: list[CalendarEvent],
    commitment_repository,
) -> list[Commitment]:
    """Upsert calendar events as commitments using stable source IDs.

    A real Google Calendar adapter can implement ``CalendarProvider`` without
    changing this sync boundary. Stable IDs make repeated syncs idempotent.
    """
    imported: list[Commitment] = []
    existing = {item.id: item for item in commitment_repository.list_for_student(student_id)}
    for event in events:
        if event.status == "cancelled":
            continue
        commitment_id = f"calendar:{event.id}"
        commitment = Commitment(
            id=commitment_id,
            title=event.summary,
            start_time=event.start_time,
            destination=event.location or "Unknown destination",
            status=CommitmentStatus.ACTIVE,
        )
        if commitment_id in existing:
            previous = existing[commitment_id]
            commitment = previous.model_copy(update=commitment.model_dump(exclude={"id"}))
        imported.append(commitment_repository.save(student_id, commitment))
    return imported
