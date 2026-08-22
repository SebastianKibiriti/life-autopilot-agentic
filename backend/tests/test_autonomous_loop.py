import unittest
from datetime import datetime, timezone

from app.agent import autonomous_evaluate
from app.models import (
    AgentDecision,
    Commitment,
    Location,
    LocationProvider,
    PreparationProfile,
    RouteProvider,
    TravelEstimate,
)
from app.notifications import NotificationService
from app.repositories import (
    InMemoryAgentEventRepository,
    InMemoryPreparationProfileRepository,
)
from app.routing import PlacesResolver


class FakeRoutesEstimator:
    def estimate_walking(self, origin, destination):
        return TravelEstimate(
            origin=origin,
            destination=destination,
            distance_meters=1800,
            duration_seconds=1320,
            duration_minutes=22,
            provider=RouteProvider.FALLBACK,
            estimated_at=datetime(2026, 8, 18, 13, 0, tzinfo=timezone.utc),
        )


class FakeGemini:
    def generate_notification(self, **kwargs):
        return "Time to get ready for class."


class AutonomousLoopTests(unittest.TestCase):
    def setUp(self):
        self.events = InMemoryAgentEventRepository()
        self.notifications = NotificationService(self.events)
        self.now = datetime(2026, 8, 18, 11, 22, tzinfo=timezone.utc)
        self.commitment = Commitment(
            title="Database Systems",
            start_time=datetime(2026, 8, 18, 12, 0, tzinfo=timezone.utc),
            destination="Engineering Building B",
        )
        self.location = Location(
            latitude=37.4200,
            longitude=-122.1600,
            provider=LocationProvider.SIMULATED,
            captured_at=self.now,
        )
        self.profile = PreparationProfile(
            student_id="student-demo",
            average_prep_minutes=12,
            arrival_buffer_minutes=5,
        )

    def test_prepare_sends_notification_and_logs_event(self):
        response = autonomous_evaluate(
            student_id="student-demo",
            now=self.now,
            commitment=self.commitment,
            current_location=self.location,
            preparation_profile=self.profile,
            event_repo=self.events,
            notification_service=self.notifications,
            places_resolver=PlacesResolver(),
            routes_estimator=FakeRoutesEstimator(),
            gemini=FakeGemini(),
        )

        self.assertEqual(response.decision, AgentDecision.PREPARE)
        self.assertTrue(response.notification_sent)
        self.assertEqual(response.leave_at, datetime(2026, 8, 18, 11, 33, tzinfo=timezone.utc))
        events = self.events.list_events("student-demo")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].action, "NOTIFICATION_SENT")

    def test_unknown_destination_escalates_instead_of_inventing_coordinates(self):
        unknown = self.commitment.model_copy(update={"destination": "Mystery Annex 12"})
        response = autonomous_evaluate(
            student_id="student-demo",
            now=self.now,
            commitment=unknown,
            current_location=self.location,
            preparation_profile=self.profile,
            event_repo=self.events,
            notification_service=self.notifications,
            places_resolver=PlacesResolver(),
            routes_estimator=FakeRoutesEstimator(),
            gemini=FakeGemini(),
        )

        self.assertEqual(response.decision, AgentDecision.ESCALATE)
        self.assertEqual(response.route_provider, "unavailable")

    def test_missing_location_escalates(self):
        response = autonomous_evaluate(
            student_id="student-demo",
            now=self.now,
            commitment=self.commitment,
            current_location=None,
            preparation_profile=self.profile,
            event_repo=self.events,
            notification_service=self.notifications,
            gemini=FakeGemini(),
        )
        self.assertEqual(response.decision, AgentDecision.ESCALATE)

    def test_notification_dedup_does_not_persist_a_second_event(self):
        kwargs = dict(
            student_id="student-demo",
            now=self.now,
            commitment=self.commitment,
            current_location=self.location,
            preparation_profile=self.profile,
            event_repo=self.events,
            notification_service=self.notifications,
            places_resolver=PlacesResolver(),
            routes_estimator=FakeRoutesEstimator(),
            gemini=FakeGemini(),
        )
        autonomous_evaluate(**kwargs)
        autonomous_evaluate(**kwargs)
        self.assertEqual(len(self.events.list_events("student-demo")), 1)


class PreparationLearningTests(unittest.TestCase):
    def test_observation_updates_bounded_average(self):
        repo = InMemoryPreparationProfileRepository()
        first = repo.update_with_observation("student-demo", "default", 20)
        second = repo.update_with_observation("student-demo", "default", 10)

        self.assertEqual(first.sample_count, 2)
        self.assertEqual(second.sample_count, 3)
        self.assertGreaterEqual(second.average_prep_minutes, 5)
        self.assertLessEqual(second.average_prep_minutes, 60)
        self.assertGreater(second.confidence, first.confidence)


if __name__ == "__main__":
    unittest.main()
