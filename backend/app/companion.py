from datetime import datetime, timezone
from uuid import uuid4

from .models import CompanionProfile, CompanionSuggestion


class CompanionMemory:
    def __init__(self, client=None):
        self.client = client
        self.profiles = {}
        self.suggestions = {}

    def profile(self, student_id):
        if self.client:
            snap = self.client.collection("students").document(student_id).collection("memory").document("profile").get()
            if snap.exists:
                return CompanionProfile.model_validate(snap.to_dict())
        return self.profiles.get(student_id, CompanionProfile(student_id=student_id))

    def save_profile(self, profile):
        profile.updated_at = datetime.now(timezone.utc)
        if self.client:
            self.client.collection("students").document(profile.student_id).collection("memory").document("profile").set(profile.model_dump(mode="json"))
        self.profiles[profile.student_id] = profile.model_copy(deep=True)
        return profile

    def save_suggestion(self, suggestion):
        if self.client:
            self.client.collection("students").document(suggestion.student_id).collection("suggestions").document(suggestion.id).set(suggestion.model_dump(mode="json"))
        self.suggestions[(suggestion.student_id, suggestion.id)] = suggestion
        return suggestion

    def get_suggestion(self, student_id, suggestion_id):
        if self.client:
            snap = self.client.collection("students").document(student_id).collection("suggestions").document(suggestion_id).get()
            if snap.exists:
                return CompanionSuggestion.model_validate(snap.to_dict())
        return self.suggestions.get((student_id, suggestion_id))


def create_fitness_suggestion(student_id, profile, campus_name="Campus Cycling Track", generated=None):
    preferred = profile.preferred_activities[0] if profile.preferred_activities else "cycling"
    data = generated if isinstance(generated, dict) else {}
    fallback = {"why": "This matches your recent fitness focus and saved outdoor-activity preference.", "duration": "The main option takes about 35 minutes.", "alternatives": "You can also choose a 25-minute run or a 30-minute recovery walk."}
    raw_followups = data.get("follow_up_answers")
    if isinstance(raw_followups, dict):
        followups = {str(k): str(v) for k, v in raw_followups.items() if v is not None} or fallback
    elif isinstance(raw_followups, list):
        followups = dict(fallback)
        for question in raw_followups:
            q = str(question).lower()
            if "duration" in q or "long" in q: followups["duration"] = fallback["duration"]
            elif "alternative" in q or "instead" in q: followups["alternatives"] = fallback["alternatives"]
            elif "why" in q or "recommend" in q: followups["why"] = fallback["why"]
    else:
        followups = fallback
    alternatives = data.get("alternatives", ["A 25-minute campus run", "A 30-minute walking recovery route"])
    preparation = data.get("preparation", ["Bring water", "Check weather before leaving"])
    if not isinstance(alternatives, list): alternatives = [alternatives]
    if not isinstance(preparation, list): preparation = [preparation]
    return CompanionSuggestion(
        id=str(uuid4()), student_id=student_id,
        main_recommendation=data.get("main_recommendation", f"Try a 35-minute {preferred} session at {campus_name} after your next nutrition class."),
        alternatives=[str(item) for item in alternatives],
        rationale=data.get("rationale", "Your recent calendar pattern shows repeated fitness events, and your saved preferences favor outdoor activity."),
        estimated_duration_minutes=data.get("estimated_duration_minutes", 35), location=data.get("location", campus_name),
        preparation=[str(item) for item in preparation],
        uncertainty=data.get("uncertainty", "Availability and weather were not verified."),
        follow_up_answers=followups,
        source_memory=["calendar fitness pattern", "accepted outdoor suggestions", "student preference profile"],
    )
