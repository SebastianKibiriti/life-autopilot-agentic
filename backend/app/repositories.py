from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from .models import (
    AgentDecision,
    AgentEvent,
    Commitment,
    CommitmentStatus,
    EventOutcome,
    PreparationProfile,
)


class CommitmentRepository(Protocol):
    """Storage boundary for student commitments."""

    def save(self, student_id: str, commitment: Commitment) -> Commitment:
        ...

    def list_for_student(self, student_id: str) -> list[Commitment]:
        ...

    def get_next_commitment(
        self, student_id: str, now: datetime
    ) -> Commitment | None:
        ...

    def list_student_ids(self) -> list[str]:
        ...


class InMemoryCommitmentRepository:
    """Local repository for tests and development without cloud credentials."""

    def __init__(self) -> None:
        self._commitments: dict[str, dict[str, Commitment]] = {}

    def save(self, student_id: str, commitment: Commitment) -> Commitment:
        if not student_id.strip():
            raise ValueError("student_id must not be empty")

        stored = commitment.model_copy(deep=True)
        stored.id = stored.id or str(uuid4())
        self._commitments.setdefault(student_id, {})[stored.id] = stored
        return stored.model_copy(deep=True)

    def list_for_student(self, student_id: str) -> list[Commitment]:
        commitments = self._commitments.get(student_id, {}).values()
        return [commitment.model_copy(deep=True) for commitment in commitments]

    def get_next_commitment(
        self, student_id: str, now: datetime
    ) -> Commitment | None:
        upcoming = [
            commitment
            for commitment in self.list_for_student(student_id)
            if commitment.status == CommitmentStatus.ACTIVE
            and commitment.start_time >= now
        ]
        if not upcoming:
            return None
        return min(upcoming, key=lambda commitment: commitment.start_time)

    def list_student_ids(self) -> list[str]:
        return list(self._commitments.keys())


class FirestoreCommitmentRepository:
    """Firestore-backed implementation using an injected Firestore client."""

    def __init__(self, client) -> None:
        self.client = client

    def _collection(self, student_id: str):
        if not student_id.strip():
            raise ValueError("student_id must not be empty")
        return (
            self.client.collection("students")
            .document(student_id)
            .collection("commitments")
        )

    def save(self, student_id: str, commitment: Commitment) -> Commitment:
        stored = commitment.model_copy(deep=True)
        document = (
            self._collection(student_id).document(stored.id)
            if stored.id
            else self._collection(student_id).document()
        )
        stored.id = document.id
        document.set(stored.model_dump(mode="json"))
        self.client.collection("students").document(student_id).set(
            {"updated_at": datetime.now(timezone.utc).isoformat()},
            merge=True,
        )
        return stored.model_copy(deep=True)

    def list_for_student(self, student_id: str) -> list[Commitment]:
        collection = self._collection(student_id)
        commitments = []
        for snapshot in collection.stream():
            data = snapshot.to_dict()
            data["id"] = snapshot.id
            commitments.append(Commitment.model_validate(data))
        return commitments

    def get_next_commitment(
        self, student_id: str, now: datetime
    ) -> Commitment | None:
        upcoming = [
            commitment
            for commitment in self.list_for_student(student_id)
            if commitment.status == CommitmentStatus.ACTIVE
            and commitment.start_time >= now
        ]
        if not upcoming:
            return None
        return min(upcoming, key=lambda commitment: commitment.start_time)

    def list_student_ids(self) -> list[str]:
        return [snapshot.id for snapshot in self.client.collection("students").stream()]


# =========================================================================
# Agent Events (Activity Timeline & Audit Log)
# =========================================================================


class AgentEventRepository(Protocol):
    def save_event(self, student_id: str, event: AgentEvent) -> AgentEvent:
        ...

    def list_events(self, student_id: str, limit: int = 50) -> list[AgentEvent]:
        ...


class InMemoryAgentEventRepository:
    def __init__(self) -> None:
        self._events: dict[str, list[AgentEvent]] = {}

    def save_event(self, student_id: str, event: AgentEvent) -> AgentEvent:
        stored = event.model_copy(deep=True)
        stored.id = stored.id or str(uuid4())
        self._events.setdefault(student_id, []).insert(0, stored)
        return stored.model_copy(deep=True)

    def list_events(self, student_id: str, limit: int = 50) -> list[AgentEvent]:
        return [
            e.model_copy(deep=True)
            for e in self._events.get(student_id, [])[:limit]
        ]


class FirestoreAgentEventRepository:
    def __init__(self, client) -> None:
        self.client = client

    def _collection(self, student_id: str):
        return (
            self.client.collection("students")
            .document(student_id)
            .collection("events")
        )

    def save_event(self, student_id: str, event: AgentEvent) -> AgentEvent:
        stored = event.model_copy(deep=True)
        document = (
            self._collection(student_id).document(stored.id)
            if stored.id
            else self._collection(student_id).document()
        )
        stored.id = document.id
        document.set(stored.model_dump(mode="json"))
        return stored.model_copy(deep=True)

    def list_events(self, student_id: str, limit: int = 50) -> list[AgentEvent]:
        docs = (
            self._collection(student_id)
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        events = []
        for snapshot in docs:
            data = snapshot.to_dict()
            data["id"] = snapshot.id
            events.append(AgentEvent.model_validate(data))
        return events


# =========================================================================
# Preparation Profile & Behavioral Learning
# =========================================================================


class PreparationProfileRepository(Protocol):
    def get_profile(
        self, student_id: str, destination_key: str = "default"
    ) -> PreparationProfile:
        ...

    def save_profile(
        self, student_id: str, profile: PreparationProfile
    ) -> PreparationProfile:
        ...

    def update_with_observation(
        self, student_id: str, destination_key: str, observed_prep_minutes: int
    ) -> PreparationProfile:
        ...


class InMemoryPreparationProfileRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, PreparationProfile]] = {}

    def get_profile(
        self, student_id: str, destination_key: str = "default"
    ) -> PreparationProfile:
        if student_id in self._profiles and destination_key in self._profiles[student_id]:
            return self._profiles[student_id][destination_key].model_copy(deep=True)
        return PreparationProfile(
            student_id=student_id,
            destination_key=destination_key,
            average_prep_minutes=15,
            arrival_buffer_minutes=5,
            confidence=0.5,
            sample_count=1,
        )

    def save_profile(
        self, student_id: str, profile: PreparationProfile
    ) -> PreparationProfile:
        self._profiles.setdefault(student_id, {})[profile.destination_key] = (
            profile.model_copy(deep=True)
        )
        return profile.model_copy(deep=True)

    def update_with_observation(
        self, student_id: str, destination_key: str, observed_prep_minutes: int
    ) -> PreparationProfile:
        current = self.get_profile(student_id, destination_key)
        n = current.sample_count
        new_avg = round((current.average_prep_minutes * n + observed_prep_minutes) / (n + 1))
        # Keep prep time within bounded limits [5, 60] minutes
        bounded_avg = max(5, min(60, new_avg))
        new_confidence = min(0.95, round(current.confidence + 0.05, 2))

        updated = PreparationProfile(
            student_id=student_id,
            destination_key=destination_key,
            average_prep_minutes=bounded_avg,
            arrival_buffer_minutes=current.arrival_buffer_minutes,
            usual_mode=current.usual_mode,
            confidence=new_confidence,
            sample_count=n + 1,
            updated_at=datetime.now(timezone.utc),
        )
        return self.save_profile(student_id, updated)


class FirestorePreparationProfileRepository:
    def __init__(self, client) -> None:
        self.client = client

    def _doc(self, student_id: str, destination_key: str):
        return (
            self.client.collection("students")
            .document(student_id)
            .collection("profiles")
            .document(destination_key)
        )

    def get_profile(
        self, student_id: str, destination_key: str = "default"
    ) -> PreparationProfile:
        snapshot = self._doc(student_id, destination_key).get()
        if snapshot.exists:
            return PreparationProfile.model_validate(snapshot.to_dict())
        return PreparationProfile(
            student_id=student_id,
            destination_key=destination_key,
            average_prep_minutes=15,
            arrival_buffer_minutes=5,
            confidence=0.5,
            sample_count=1,
        )

    def save_profile(
        self, student_id: str, profile: PreparationProfile
    ) -> PreparationProfile:
        doc = self._doc(student_id, profile.destination_key)
        doc.set(profile.model_dump(mode="json"))
        return profile.model_copy(deep=True)

    def update_with_observation(
        self, student_id: str, destination_key: str, observed_prep_minutes: int
    ) -> PreparationProfile:
        current = self.get_profile(student_id, destination_key)
        n = current.sample_count
        new_avg = round((current.average_prep_minutes * n + observed_prep_minutes) / (n + 1))
        bounded_avg = max(5, min(60, new_avg))
        new_confidence = min(0.95, round(current.confidence + 0.05, 2))

        updated = PreparationProfile(
            student_id=student_id,
            destination_key=destination_key,
            average_prep_minutes=bounded_avg,
            arrival_buffer_minutes=current.arrival_buffer_minutes,
            usual_mode=current.usual_mode,
            confidence=new_confidence,
            sample_count=n + 1,
            updated_at=datetime.now(timezone.utc),
        )
        return self.save_profile(student_id, updated)
