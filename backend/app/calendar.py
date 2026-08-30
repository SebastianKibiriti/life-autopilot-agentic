"""Calendar ingestion boundary for the cross-app Taskmaster workflow."""
from __future__ import annotations

import os
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
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


class GoogleCalendarProvider:
    """Read-only Google Calendar provider using local OAuth credentials."""

    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(
        self,
        *,
        credentials_path: str,
        token_path: str = "google-calendar-token.json",
        calendar_id: str = "primary",
    ) -> None:
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.calendar_id = calendar_id

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
        return build("calendar", "v3", credentials=credentials, cache_discovery=False)

    def upcoming_events(self, *, student_id: str) -> list[CalendarEvent]:
        del student_id
        service = self._service()
        now = datetime.now(timezone.utc).isoformat()
        response = service.events().list(
            calendarId=self.calendar_id,
            timeMin=now,
            maxResults=50,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events: list[CalendarEvent] = []
        for item in response.get("items", []):
            start = item.get("start", {}).get("dateTime")
            if not start or not item.get("id") or not item.get("summary"):
                continue
            events.append(
                CalendarEvent(
                    id=item["id"],
                    summary=item["summary"],
                    start_time=start,
                    location=item.get("location"),
                    status=item.get("status", "confirmed"),
                    meeting_contact_email=next((a.get("email") for a in item.get("attendees", []) if a.get("email")), None),
                )
            )
        return events

    def create_action(self, *, action_id: str, title: str, start_time: datetime, description: str) -> dict:
        service = self._service()
        event_id = hashlib.sha256(action_id.encode("utf-8")).hexdigest()[:32]
        event = {
            "id": event_id,
            "summary": title,
            "description": description,
            "start": {"dateTime": start_time.isoformat()},
            "end": {"dateTime": (start_time + timedelta(minutes=1)).isoformat()},
        }
        try:
            return service.events().insert(calendarId=self.calendar_id, body=event).execute()
        except Exception as error:
            # Google Calendar rejects a repeated deterministic event ID with 409.
            # Treat an existing event as success so demo retries are idempotent.
            if getattr(error, "resp", None) is not None and getattr(error.resp, "status", None) == 409:
                existing = service.events().get(
                    calendarId=self.calendar_id, eventId=event_id
                ).execute()
                existing["life_autopilot_idempotent_replay"] = True
                return existing
            raise


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
            meeting_contact_email=event.meeting_contact_email,
            status=CommitmentStatus.ACTIVE,
        )
        if commitment_id in existing:
            previous = existing[commitment_id]
            commitment = previous.model_copy(update=commitment.model_dump(exclude={"id"}))
        imported.append(commitment_repository.save(student_id, commitment))
    return imported
