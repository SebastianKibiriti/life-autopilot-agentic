import os
import unittest
from datetime import datetime, timedelta, timezone

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

from google.cloud import firestore
from app.models import Commitment, CommitmentStatus
from app.repositories import FirestoreCommitmentRepository


class FirestoreIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.use_firestore = os.getenv("USE_FIRESTORE", "false").lower() == "true"
        cls.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        cls.database_id = os.getenv("FIRESTORE_DATABASE", "(default)")
        cls.student_id = "student-integration-test"

        if not cls.use_firestore or not cls.project_id:
            raise unittest.SkipTest("Firestore integration tests are skipped: USE_FIRESTORE or GOOGLE_CLOUD_PROJECT is not set.")
        if os.getenv("FIRESTORE_INTEGRATION", "false").lower() != "true":
            raise unittest.SkipTest(
                "Firestore integration tests are skipped unless FIRESTORE_INTEGRATION=true."
            )

        cls.client = firestore.Client(project=cls.project_id, database=cls.database_id)
        cls.repository = FirestoreCommitmentRepository(cls.client)

    def setUp(self):
        # Clean up any leftover test data before each test
        self.cleanup_test_data()

    def tearDown(self):
        # Clean up test data after each test
        self.cleanup_test_data()

    def cleanup_test_data(self):
        collection = (
            self.client.collection("students")
            .document(self.student_id)
            .collection("commitments")
        )
        for doc in collection.list_documents():
            doc.delete()

    def test_firestore_repository_lifecycle(self):
        # 1. Verify saving a commitment
        now = datetime.now(timezone.utc)
        start_time_1 = now + timedelta(hours=2)
        commitment_1 = Commitment(
            title="Integration Class 1",
            start_time=start_time_1,
            destination="Online Hall",
            status=CommitmentStatus.ACTIVE,
        )

        saved_1 = self.repository.save(self.student_id, commitment_1)
        self.assertIsNotNone(saved_1.id)
        self.assertEqual(saved_1.title, "Integration Class 1")
        # Start time fetched might be normalized or compare equal
        self.assertEqual(saved_1.destination, "Online Hall")

        # 2. Verify listing commitments
        loaded = self.repository.list_for_student(self.student_id)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].id, saved_1.id)
        self.assertEqual(loaded[0].title, "Integration Class 1")

        # 3. Verify get_next_commitment with one commitment
        next_commitment = self.repository.get_next_commitment(self.student_id, now)
        self.assertIsNotNone(next_commitment)
        self.assertEqual(next_commitment.id, saved_1.id)

        # 4. Save a second commitment starting sooner (in 1 hour)
        start_time_2 = now + timedelta(hours=1)
        commitment_2 = Commitment(
            title="Integration Class 2",
            start_time=start_time_2,
            destination="Physical Lab",
            status=CommitmentStatus.ACTIVE,
        )
        saved_2 = self.repository.save(self.student_id, commitment_2)
        self.assertIsNotNone(saved_2.id)

        # 5. Verify get_next_commitment returns the sooner commitment
        next_commitment = self.repository.get_next_commitment(self.student_id, now)
        self.assertIsNotNone(next_commitment)
        self.assertEqual(next_commitment.id, saved_2.id)
        self.assertEqual(next_commitment.title, "Integration Class 2")

        # 6. Verify completed/cancelled commitments are ignored
        saved_2.status = CommitmentStatus.COMPLETED
        self.repository.save(self.student_id, saved_2)

        next_commitment = self.repository.get_next_commitment(self.student_id, now)
        self.assertIsNotNone(next_commitment)
        self.assertEqual(next_commitment.id, saved_1.id)
        self.assertEqual(next_commitment.title, "Integration Class 1")


if __name__ == "__main__":
    unittest.main()
