from datetime import datetime
from typing import Protocol
from uuid import uuid4

from .models import Commitment, CommitmentStatus


class CommitmentRepository(Protocol):
    """Storage boundary the future Firestore repository will implement."""

    def save(self, student_id: str, commitment: Commitment) -> Commitment:
        ...

    def list_for_student(self, student_id: str) -> list[Commitment]:
        ...

    def get_next_commitment(
        self, student_id: str, now: datetime
    ) -> Commitment | None:
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

