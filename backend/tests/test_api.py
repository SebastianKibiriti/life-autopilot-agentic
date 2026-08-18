import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app, get_commitment_repository
from app.repositories import InMemoryCommitmentRepository


class CommitmentApiTests(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryCommitmentRepository()
        app.dependency_overrides[get_commitment_repository] = lambda: self.repository
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_create_list_and_query_next_commitment(self):
        create_url = "/api/v1/students/student-demo/commitments"
        later = {
            "title": "Later class",
            "start_time": "2026-08-18T16:00:00Z",
            "destination": "Engineering Building B",
        }
        sooner = {
            "title": "Sooner class",
            "start_time": "2026-08-18T14:00:00Z",
            "destination": "Engineering Building A",
        }

        later_response = self.client.post(create_url, json=later)
        sooner_response = self.client.post(create_url, json=sooner)

        self.assertEqual(later_response.status_code, 201)
        self.assertEqual(sooner_response.status_code, 201)
        self.assertIsNotNone(sooner_response.json()["id"])

        listed = self.client.get(create_url)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 2)

        next_response = self.client.get(
            "/api/v1/students/student-demo/commitments/next",
            params={"now": "2026-08-18T12:00:00Z"},
        )
        self.assertEqual(next_response.status_code, 200)
        self.assertEqual(next_response.json()["title"], "Sooner class")

    def test_next_commitment_returns_null_for_empty_schedule(self):
        response = self.client.get(
            "/api/v1/students/empty/commitments/next",
            params={"now": "2026-08-18T12:00:00Z"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())

    def test_invalid_commitment_is_rejected(self):
        response = self.client.post(
            "/api/v1/students/student-demo/commitments",
            json={
                "title": "",
                "start_time": "2026-08-18T14:00:00Z",
                "destination": "Engineering Building A",
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()

