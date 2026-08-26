import os
import unittest
from unittest.mock import patch

from app.models import AgentDecision
from app.notifications import NotificationService
from app.repositories import InMemoryAgentEventRepository


class ExternalNotificationTests(unittest.TestCase):
    @patch("app.notifications.httpx.post")
    def test_chat_webhook_receives_notification(self, post):
        post.return_value.raise_for_status.return_value = None
        service = NotificationService(InMemoryAgentEventRepository())
        with patch.dict(os.environ, {"GOOGLE_CHAT_WEBHOOK_URL": "https://chat.example/hook"}):
            service.send(
                student_id="student-1",
                decision=AgentDecision.PREPARE,
                commitment_id="commitment-1",
                notification_title="Prepare",
                notification_body="Get ready.",
                reason="The preparation window is open.",
            )
        post.assert_called_once()
        self.assertEqual(post.call_args.kwargs["json"]["text"], "Prepare\nGet ready.")
