import unittest
from datetime import datetime, timezone

from app.calendar import sync_calendar_events
from app.models import CalendarEvent
from app.repositories import InMemoryCommitmentRepository


class CalendarSyncTests(unittest.TestCase):
    def test_sync_is_idempotent_and_updates_event(self):
        repository = InMemoryCommitmentRepository()
        first = CalendarEvent(
            id="event-1",
            summary="Engineering lecture",
            start_time=datetime(2026, 8, 26, 10, tzinfo=timezone.utc),
            location="library",
        )
        updated = first.model_copy(update={"location": "Engineering Building B"})

        first_result = sync_calendar_events(
            student_id="student-1", events=[first], commitment_repository=repository
        )
        second_result = sync_calendar_events(
            student_id="student-1", events=[updated], commitment_repository=repository
        )

        self.assertEqual(first_result[0].id, "calendar:event-1")
        self.assertEqual(second_result[0].id, "calendar:event-1")
        self.assertEqual(len(repository.list_for_student("student-1")), 1)
        self.assertEqual(second_result[0].destination, "Engineering Building B")

    def test_cancelled_events_are_not_imported(self):
        repository = InMemoryCommitmentRepository()
        event = CalendarEvent(
            id="event-2",
            summary="Cancelled lecture",
            start_time=datetime(2026, 8, 26, 10, tzinfo=timezone.utc),
            status="cancelled",
        )
        self.assertEqual(
            sync_calendar_events(
                student_id="student-1", events=[event], commitment_repository=repository
            ),
            [],
        )
