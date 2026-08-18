from datetime import datetime

from .models import Commitment
from .repositories import CommitmentRepository


def get_next_commitment(
    repository: CommitmentRepository,
    *,
    student_id: str,
    now: datetime,
) -> Commitment | None:
    """Return the earliest active commitment at or after the evaluation time."""
    return repository.get_next_commitment(student_id, now)

