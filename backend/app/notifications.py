"""Idempotent notification service.

In the MVP there is no real push gateway. This service records the intended
notification as an AgentEvent and returns the message body so callers can
surface it through any available channel (API response, future FCM, etc.).

Idempotency: two notifications for the same (student_id, commitment_id,
decision) within the dedup window are considered duplicates; the second call
returns the original body without recording a new event.
"""
import os
from datetime import datetime, timedelta, timezone

import httpx

from .models import AgentDecision, AgentEvent, EventOutcome


# Deduplicate within this window so the agent doesn't spam the student
_DEDUP_WINDOW_MINUTES = 5


class NotificationService:
    def __init__(self, event_repo) -> None:
        self._event_repo = event_repo
        # In-memory dedup index: (student_id, commitment_id, decision) -> timestamp
        self._sent: dict[tuple, datetime] = {}

    def _dedup_key(
        self, student_id: str, commitment_id: str | None, decision: AgentDecision
    ) -> tuple:
        return (student_id, commitment_id or "", decision)

    def _is_duplicate(
        self, key: tuple, now: datetime
    ) -> bool:
        last = self._sent.get(key)
        if last is None:
            return False
        return (now - last) < timedelta(minutes=_DEDUP_WINDOW_MINUTES)

    def send(
        self,
        *,
        student_id: str,
        decision: AgentDecision,
        commitment_id: str | None,
        notification_title: str,
        notification_body: str,
        reason: str,
        now: datetime | None = None,
    ) -> AgentEvent:
        """Record and return the notification event.

        Returns an existing (deduplicated) event if an identical notification
        was already sent within the dedup window.
        """
        now = now or datetime.now(timezone.utc)
        key = self._dedup_key(student_id, commitment_id, decision)

        if self._is_duplicate(key, now):
            # Return a suppressed copy — not persisted again
            return AgentEvent(
                student_id=student_id,
                commitment_id=commitment_id,
                timestamp=now,
                decision=decision,
                reason=reason,
                action="NOTIFICATION_SUPPRESSED",
                outcome=EventOutcome.DELIVERED,
                notification_title=notification_title,
                notification_body=notification_body,
            )

        webhook_url = os.getenv("GOOGLE_CHAT_WEBHOOK_URL")
        if webhook_url:
            try:
                response = httpx.post(
                    webhook_url,
                    json={"text": f"{notification_title}\n{notification_body}"},
                    timeout=5.0,
                )
                response.raise_for_status()
            except httpx.HTTPError:
                # The audit event remains the source of truth if delivery fails.
                pass

        event = AgentEvent(
            student_id=student_id,
            commitment_id=commitment_id,
            timestamp=now,
            decision=decision,
            reason=reason,
            action="NOTIFICATION_SENT",
            outcome=EventOutcome.DELIVERED,
            notification_title=notification_title,
            notification_body=notification_body,
        )
        saved = self._event_repo.save_event(student_id, event)
        self._sent[key] = now
        return saved
