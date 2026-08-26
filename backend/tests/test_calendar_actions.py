import unittest
from datetime import datetime, timezone
from unittest.mock import Mock

from app.calendar import GoogleCalendarProvider


class CalendarActionTests(unittest.TestCase):
    def test_action_uses_calendar_safe_id(self):
        provider = GoogleCalendarProvider(credentials_path="unused.json")
        service = Mock()
        service.events.return_value.insert.return_value.execute.return_value = {"id": "ok"}
        provider._service = lambda: service

        provider.create_action(
            action_id="life-autopilot:commitment-1",
            title="Leave now",
            start_time=datetime(2026, 8, 26, 16, tzinfo=timezone.utc),
            description="Test action",
        )

        body = service.events.return_value.insert.call_args.kwargs["body"]
        self.assertRegex(body["id"], r"^[a-f0-9]{32}$")
