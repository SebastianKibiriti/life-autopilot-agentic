"""Gemini-powered timetable extraction from free-form text."""
from .gemini import GeminiClient
from .models import TimetableExtractRequest, TimetableExtractResponse, TimetableItem
from datetime import datetime, timezone

_gemini = GeminiClient()


def extract_timetable(request: TimetableExtractRequest) -> TimetableExtractResponse:
    """Extract structured commitments from plain text or base64 content."""
    if not request.content and not request.image_base64:
        return TimetableExtractResponse(
            commitments=[],
            notes="No content provided.",
        )

    text = request.content or "[Image content provided — extraction requires Gemini Vision]"
    raw_items = _gemini.parse_timetable_text(text)

    commitments: list[TimetableItem] = []
    notes_parts: list[str] = []

    for item in raw_items:
        try:
            start_time = item.get("start_time")
            if isinstance(start_time, str):
                # Attempt to parse ISO 8601 format
                dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            elif isinstance(start_time, datetime):
                dt = start_time
            else:
                notes_parts.append(f"Skipped item with invalid start_time: {item}")
                continue

            commitments.append(
                TimetableItem(
                    title=str(item.get("title", "Unknown")),
                    start_time=dt,
                    destination=str(item.get("destination", "Unknown Location")),
                )
            )
        except Exception as e:
            notes_parts.append(f"Skipped item due to error: {e}")

    notes = "; ".join(notes_parts) if notes_parts else None
    return TimetableExtractResponse(commitments=commitments, notes=notes)
