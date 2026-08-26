"""Gmail notification provider using local OAuth credentials."""
from __future__ import annotations

import base64
import os
from email.mime.text import MIMEText
from pathlib import Path


class GmailNotificationProvider:
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    def __init__(
        self,
        *,
        credentials_path: str,
        token_path: str = "gmail-token.json",
        recipient: str,
    ) -> None:
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.recipient = recipient

    def _service(self):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        credentials = None
        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                str(self.token_path), self.SCOPES
            )
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path), self.SCOPES
            )
            credentials = flow.run_local_server(port=0)
        self.token_path.write_text(credentials.to_json())
        return build("gmail", "v1", credentials=credentials, cache_discovery=False)

    def send(self, *, subject: str, body: str) -> dict:
        message = MIMEText(body, "plain", "utf-8")
        message["to"] = self.recipient
        message["subject"] = subject
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        return self._service().users().messages().send(
            userId="me", body={"raw": encoded}
        ).execute()


def configured_gmail_provider() -> GmailNotificationProvider | None:
    recipient = os.getenv("GMAIL_NOTIFICATION_TO")
    if not recipient:
        return None
    return GmailNotificationProvider(
        credentials_path=os.getenv(
            "GOOGLE_CALENDAR_CREDENTIALS",
            "client_secret_725797619054-gutqcc15kok56n1r83hodd9u2j6iual7.apps.googleusercontent.com.json",
        ),
        token_path=os.getenv("GMAIL_TOKEN", "gmail-token.json"),
        recipient=recipient,
    )
