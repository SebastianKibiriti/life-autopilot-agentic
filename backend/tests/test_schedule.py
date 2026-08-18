import unittest
from datetime import datetime, timezone

from app.models import Commitment, CommitmentStatus
from app.repositories import InMemoryCommitmentRepository
from app.schedule import get_next_commitment


class CommitmentRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryCommitmentRepository()
        self.student_id = "student-demo"
        self.now = datetime(2026, 8, 18, 12, 0, tzinfo=timezone.utc)

    def commitment(self, title, hour, *, status=CommitmentStatus.ACTIVE):
        return Commitment(
            title=title,
            start_time=datetime(2026, 8, 18, hour, 0, tzinfo=timezone.utc),
            destination="Engineering Building B",
            status=status,
        )

    def test_save_assigns_id_and_list_is_scoped_to_student(self):
        saved = self.repository.save(self.student_id, self.commitment("Class", 14))
        self.repository.save("another-student", self.commitment("Other", 13))

        self.assertIsNotNone(saved.id)
        commitments = self.repository.list_for_student(self.student_id)
        self.assertEqual([item.title for item in commitments], ["Class"])

    def test_next_commitment_returns_earliest_active_future_commitment(self):
        self.repository.save(self.student_id, self.commitment("Later", 16))
        self.repository.save(self.student_id, self.commitment("Sooner", 14))
        self.repository.save(
            self.student_id,
            self.commitment("Cancelled", 13, status=CommitmentStatus.CANCELLED),
        )
        self.repository.save(
            self.student_id,
            self.commitment("Completed", 15, status=CommitmentStatus.COMPLETED),
        )

        next_commitment = get_next_commitment(
            self.repository, student_id=self.student_id, now=self.now
        )

        self.assertIsNotNone(next_commitment)
        self.assertEqual(next_commitment.title, "Sooner")

    def test_empty_or_past_schedule_returns_none(self):
        self.repository.save(self.student_id, self.commitment("Past", 11))

        self.assertIsNone(
            get_next_commitment(
                self.repository, student_id=self.student_id, now=self.now
            )
        )
        self.assertIsNone(
            get_next_commitment(
                self.repository, student_id="missing", now=self.now
            )
        )

    def test_save_replaces_existing_commitment_with_same_id(self):
        saved = self.repository.save(self.student_id, self.commitment("Original", 14))
        replacement = saved.model_copy(update={"title": "Updated"})
        self.repository.save(self.student_id, replacement)

        commitments = self.repository.list_for_student(self.student_id)
        self.assertEqual(len(commitments), 1)
        self.assertEqual(commitments[0].title, "Updated")


if __name__ == "__main__":
    unittest.main()

