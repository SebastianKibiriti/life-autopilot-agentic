import os
import json
from datetime import datetime, timedelta
from typing import Any

from .models import AgentDecision


class GeminiClient:
    """Wrapper around google-genai for reasoning, notification generation, and extraction."""

    def __init__(self) -> None:
        self.project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        self.use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true"
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from google import genai
                if self.use_vertex and self.project:
                    self._client = genai.Client(
                        vertexai=True,
                        project=self.project,
                        location=self.location,
                    )
                else:
                    self._client = genai.Client()
            except Exception:
                self._client = False
        return self._client if self._client is not False else None

    def generate_notification(
        self,
        decision: AgentDecision,
        commitment_title: str,
        destination: str,
        leave_at: datetime | None = None,
        preparation_at: datetime | None = None,
        now: datetime | None = None,
        travel_minutes: int | None = None,
        commitment_start: datetime | None = None,
    ) -> str:
        """Generates friendly, actionable copy using Gemini with deterministic fallback."""
        leave_str = leave_at.strftime("%H:%M") if leave_at else "soon"
        prep_str = preparation_at.strftime("%H:%M") if preparation_at else "now"

        # Deterministic fallback defaults
        expected_delay = 0
        if decision == AgentDecision.REPLAN and now and travel_minutes is not None:
            expected_arrival = now + timedelta(minutes=travel_minutes)
            if commitment_start:
                expected_delay = max(0, round((expected_arrival - commitment_start).total_seconds() / 60))

        defaults = {
            AgentDecision.PREPARE: f"Time to get ready for {commitment_title}! You'll need to head out by {leave_str}.",
            AgentDecision.LEAVE: f"Time to head out for {commitment_title} at {destination}. Leave now to arrive on time.",
            AgentDecision.REPLAN: f"Since you still haven't left, you'll arrive about {expected_delay} minutes later to {destination}.",
            AgentDecision.ESCALATE: f"Location or route unavailable for {commitment_title}. Please check your connection.",
            AgentDecision.NO_ACTION: "",
        }

        if decision == AgentDecision.NO_ACTION:
            return ""

        client = self._get_client()
        if not client:
            return defaults.get(decision, "")

        try:
            prompt = (
                f"You are Life Autopilot, a proactive personal student assistant. "
                f"Write a single concise, helpful, friendly push notification (max 15 words) for this event:\n"
                f"Event: {commitment_title} at {destination}\n"
                f"Action needed: {decision.value}\n"
                f"Preparation starts: {prep_str}\n"
                f"Departure time: {leave_str}\n"
                f"Current time: {now.strftime('%H:%M') if now else 'unknown'}\n"
                f"Estimated delay if stationary: {expected_delay} minutes\n"
                f"Output only the notification text."
            )
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            text = response.text.strip().strip('"')
            return text if text else defaults.get(decision, "")
        except Exception:
            return defaults.get(decision, "")

    def parse_timetable_text(self, text: str) -> list[dict[str, Any]]:
        """Parses free-form timetable text or syllabus into structured JSON items."""
        client = self._get_client()
        if not client:
            return []

    def generate_companion_suggestion(self, *, profile: dict[str, Any], upcoming_context: str) -> dict[str, Any] | None:
        """Generate structured companion content; callers retain a deterministic fallback."""
        client = self._get_client()
        if not client:
            return None
        try:
            prompt = (
                "Return ONLY valid JSON with keys main_recommendation, alternatives, rationale, "
                "estimated_duration_minutes, location, preparation, uncertainty, follow_up_answers. "
                f"Personal profile: {json.dumps(profile)}. Context: {upcoming_context}. "
                "Suggest a safe, practical outdoor fitness activity for this student."
            )
            response = client.models.generate_content(model=self.model_name, contents=prompt)
            raw = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            data = json.loads(raw)
            return data if isinstance(data, dict) else None
        except Exception:
            return None

        try:
            prompt = (
                f"Extract upcoming academic or personal commitments from this timetable text into a JSON list.\n"
                f"Each object must have:\n"
                f"- 'title': name of class or commitment\n"
                f"- 'start_time': ISO 8601 formatted datetime string in UTC\n"
                f"- 'destination': location or room name\n"
                f"Text:\n{text}\n\n"
                f"Return ONLY a valid JSON array of objects."
            )
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            raw = response.text.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            return json.loads(raw.strip())
        except Exception:
            return []
