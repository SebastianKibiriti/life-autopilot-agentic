import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import (
    app,
    get_commitment_repository,
    get_event_repository,
    get_location_repository,
    get_notification_service,
    get_profile_repository,
)
from app.location import InMemoryLocationRepository
from app.models import LocationProvider
from app.notifications import NotificationService
from app.repositories import (
    InMemoryAgentEventRepository,
    InMemoryCommitmentRepository,
    InMemoryPreparationProfileRepository,
)


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


class AutonomousApiTests(unittest.TestCase):
    def setUp(self):
        self.commitments = InMemoryCommitmentRepository()
        self.locations = InMemoryLocationRepository()
        self.events = InMemoryAgentEventRepository()
        self.profiles = InMemoryPreparationProfileRepository()
        app.dependency_overrides[get_commitment_repository] = lambda: self.commitments
        app.dependency_overrides[get_location_repository] = lambda: self.locations
        app.dependency_overrides[get_event_repository] = lambda: self.events
        app.dependency_overrides[get_profile_repository] = lambda: self.profiles
        app.dependency_overrides[get_notification_service] = lambda: NotificationService(
            self.events
        )
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_location_round_trip_and_events_list(self):
        created = self.client.post(
            "/api/v1/students/student-demo/location",
            json={
                "latitude": 37.42,
                "longitude": -122.16,
                "provider": LocationProvider.SIMULATED.value,
                "captured_at": "2026-08-18T11:00:00Z",
            },
        )
        self.assertEqual(created.status_code, 201)
        fetched = self.client.get("/api/v1/students/student-demo/location")
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json()["latitude"], 37.42)

        events = self.client.get("/api/v1/students/student-demo/events")
        self.assertEqual(events.status_code, 200)
        self.assertEqual(events.json(), [])

    def test_naive_datetime_is_rejected(self):
        response = self.client.post(
            "/api/v1/students/student-demo/commitments",
            json={
                "title": "Naive class",
                "start_time": "2026-08-18T14:00:00",
                "destination": "Engineering Building A",
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_learn_updates_profile(self):
        response = self.client.post(
            "/api/v1/students/student-demo/learn",
            json={
                "actual_prep_minutes": 18,
                "actual_start_moving_at": "2026-08-18T13:30:00Z",
                "destination_key": "default",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sample_count"], 2)


if __name__ == "__main__":
    unittest.main()

