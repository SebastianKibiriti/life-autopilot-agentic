import os
import unittest
from unittest.mock import Mock, patch

from app.gmail import GmailNotificationProvider


class GmailNotificationTests(unittest.TestCase):
    @patch("app.gmail.GmailNotificationProvider._service")
    def test_send_builds_gmail_message(self, service_factory):
        service = Mock()
        service.users.return_value.messages.return_value.send.return_value.execute.return_value = {"id": "mail-1"}
        service_factory.return_value = service
        provider = GmailNotificationProvider(
            credentials_path="unused.json", recipient="student@example.com"
        )

        result = provider.send(subject="Time to leave", body="Leave now.")

        self.assertEqual(result["id"], "mail-1")
        body = service.users.return_value.messages.return_value.send.call_args.kwargs["body"]
        self.assertIn("raw", body)
