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
        self.use_vertex = (
            os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true"
        )
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
        weather_observation: str | None = None,
        traffic_observation: str | None = None,
    ) -> str:
        """
        Generate concise, actionable user notification copy.

        Arithmetic is deterministic and performed here rather than delegated
        to Gemini. Gemini is responsible only for wording.
        """

        leave_str = leave_at.strftime("%H:%M") if leave_at else "soon"
        prep_str = preparation_at.strftime("%H:%M") if preparation_at else "now"

        expected_arrival: datetime | None = None
        expected_delay = 0

        if now is not None and travel_minutes is not None:
            expected_arrival = now + timedelta(minutes=travel_minutes)

            if commitment_start is not None:
                expected_delay = max(
                    0,
                    round(
                        (
                            expected_arrival - commitment_start
                        ).total_seconds()
                        / 60
                    ),
                )

        expected_arrival_utc_str = (
            expected_arrival.strftime("%H:%M UTC")
            if expected_arrival
            else "unknown"
        )

        # South Africa Standard Time is UTC+2.
        expected_arrival_sast_str = (
            (expected_arrival + timedelta(hours=2)).strftime("%H:%M SAST")
            if expected_arrival
            else "unknown"
        )

        # Deterministic fallbacks ensure the demo remains functional even
        # when Gemini is unavailable.
        defaults = {
            AgentDecision.PREPARE: (
                f"Time to get ready for {commitment_title}. "
                f"Leave by {leave_str}. "
                f"Weather: {weather_observation or 'unavailable'}. "
                f"Traffic: {traffic_observation or 'unavailable'}."
            ),

            AgentDecision.LEAVE: (
                f"Time to leave for {commitment_title} at {destination}. "
                f"Leave now to arrive as planned."
            ),

            AgentDecision.REPLAN: (
                f"You have not left yet. "
                f"If you leave now, you are expected to arrive at "
                f"{expected_arrival_sast_str}."
            ),

            AgentDecision.ESCALATE: (
                f"Location or route unavailable for {commitment_title}. "
                f"Please check your connection."
            ),

            AgentDecision.NO_ACTION: "",
        }

        if decision == AgentDecision.NO_ACTION:
            return ""

        client = self._get_client()

        if not client:
            return defaults.get(decision, "")

        try:
            prompt = (
                "You are Life Autopilot, a proactive personal student assistant. "
                "Write ONE concise, natural, actionable push notification for the "
                "student. You are writing the wording only; all times and arithmetic "
                "have already been calculated deterministically.\n\n"

                f"Event: {commitment_title}\n"
                f"Destination: {destination}\n"
                f"Decision: {decision.value}\n"
                f"Preparation threshold: {prep_str} UTC\n"
                f"Leave threshold: {leave_str} UTC\n"
                f"Current time: {now.strftime('%H:%M UTC') if now else 'unknown'}\n"
                f"Travel time from current location: "
                f"{travel_minutes if travel_minutes is not None else 'unknown'} minutes\n"
                f"Expected arrival if leaving now: {expected_arrival_utc_str}\n"
                f"Expected arrival if leaving now in South Africa: "
                f"{expected_arrival_sast_str}\n"
                f"Expected delay relative to meeting: {expected_delay} minutes\n"
                f"Meeting time: "
                f"{commitment_start.strftime('%H:%M UTC') if commitment_start else 'unknown'}\n"
                f"Weather: {weather_observation or 'unavailable'}\n"
                f"Traffic: {traffic_observation or 'unavailable'}\n\n"

                "Rules:\n"
                "- Do not invent times, delays, traffic, weather, or destinations.\n"
                "- For REPLAN, clearly tell the student what time they are expected "
                "to arrive IF THEY LEAVE NOW.\n"
                "- For REPLAN, if expected arrival is after the meeting time, "
                "make the lateness clear and state the expected arrival time.\n"
                "- For REPLAN, if expected arrival is before the meeting time, "
                "do not imply that the student is late. Instead explain that "
                "leaving now still keeps them on track.\n"
                "- For LEAVE, tell the student to leave now.\n"
                "- Keep the notification concise but informative. Do not use an "
                "artificial 15-word limit; use roughly 15–30 words when needed "
                "to communicate the expected arrival time clearly.\n"
                "- Output ONLY the notification text.\n"
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
        """Parse free-form timetable text into structured JSON items."""

        client = self._get_client()

        if not client:
            return []

        try:
            prompt = (
                "Extract upcoming academic or personal commitments from this "
                "timetable text into a JSON list.\n"
                "Each object must have:\n"
                "- 'title': name of class or commitment\n"
                "- 'start_time': ISO 8601 formatted datetime string in UTC\n"
                "- 'destination': location or room name\n\n"
                f"Text:\n{text}\n\n"
                "Return ONLY a valid JSON array of objects."
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

            parsed = json.loads(raw.strip())

            return parsed if isinstance(parsed, list) else []

        except Exception:
            return []

    def generate_companion_suggestion(
        self,
        *,
        profile: dict[str, Any],
        upcoming_context: str,
    ) -> dict[str, Any] | None:
        """Generate structured companion content; callers retain a deterministic fallback."""

        client = self._get_client()

        if not client:
            return None

        try:
            prompt = (
                "Return ONLY valid JSON with keys "
                "main_recommendation, alternatives, rationale, "
                "estimated_duration_minutes, location, preparation, "
                "uncertainty, follow_up_answers. "
                f"Personal profile: {json.dumps(profile)}. "
                f"Context: {upcoming_context}. "
                "Suggest a safe, practical outdoor fitness activity for this student."
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            raw = (
                response.text
                .strip()
                .removeprefix("```json")
                .removesuffix("```")
                .strip()
            )

            data = json.loads(raw)

            return data if isinstance(data, dict) else None

        except Exception:
            return None
