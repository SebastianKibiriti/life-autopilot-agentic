import unittest
from datetime import datetime, timezone

from app.models import Commitment
from app.repositories import FirestoreCommitmentRepository


class FakeSnapshot:
    def __init__(self, document_id, data):
        self.id = document_id
        self._data = data

    def to_dict(self):
        return dict(self._data)


class FakeDocument:
    def __init__(self, collection, document_id):
        self.collection_ref = collection
        self.id = document_id

    def collection(self, name):
        return self.collection_ref.client.collection_store(
            f"{self.collection_ref.path}/{self.id}/{name}"
        )

    def set(self, data):
        self.collection_ref.documents[self.id] = dict(data)


class FakeCollection:
    def __init__(self, client, path):
        self.client = client
        self.path = path
        self.documents = client.documents.setdefault(path, {})

    def document(self, document_id=None):
        if document_id is None:
            document_id = f"generated-{len(self.documents) + 1}"
        return FakeDocument(self, document_id)

    def stream(self):
        return [FakeSnapshot(doc_id, data) for doc_id, data in self.documents.items()]


class FakeFirestoreClient:
    def __init__(self):
        self.documents = {}

    def collection_store(self, path):
        return FakeCollection(self, path)

    def collection(self, name):
        return self.collection_store(name)


class FirestoreCommitmentRepositoryTests(unittest.TestCase):
    def test_adapter_persists_and_reads_commitments_through_client_boundary(self):
        repository = FirestoreCommitmentRepository(FakeFirestoreClient())
        commitment = Commitment(
            title="Database Systems",
            start_time=datetime(2026, 8, 18, 14, 0, tzinfo=timezone.utc),
            destination="Engineering Building B",
        )

        saved = repository.save("student-demo", commitment)
        loaded = repository.list_for_student("student-demo")

        self.assertEqual(saved.id, "generated-1")
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].title, "Database Systems")
        self.assertEqual(loaded[0].id, saved.id)

    def test_adapter_supports_next_commitment_query(self):
        repository = FirestoreCommitmentRepository(FakeFirestoreClient())
        repository.save(
            "student-demo",
            Commitment(
                title="Later",
                start_time=datetime(2026, 8, 18, 16, 0, tzinfo=timezone.utc),
                destination="Room B",
            ),
        )
        repository.save(
            "student-demo",
            Commitment(
                title="Sooner",
                start_time=datetime(2026, 8, 18, 14, 0, tzinfo=timezone.utc),
                destination="Room A",
            ),
        )

        next_commitment = repository.get_next_commitment(
            "student-demo", datetime(2026, 8, 18, 12, 0, tzinfo=timezone.utc)
        )

        self.assertEqual(next_commitment.title, "Sooner")


if __name__ == "__main__":
    unittest.main()

