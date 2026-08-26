import unittest
from datetime import datetime, timezone

from app.agent import autonomous_evaluate
from app.models import Commitment, Location, LocationProvider, PreparationProfile, RouteProvider, TravelEstimate, AgentDecision
from app.notifications import NotificationService
from app.repositories import InMemoryAgentEventRepository
from app.routing import PlacesResolver


class DemoRoutes:
    def estimate_walking(self, origin, destination):
        return TravelEstimate(
            origin=origin,
            destination=destination,
            mode="walking",
            distance_meters=1800,
            duration_seconds=1320,
            duration_minutes=22,
            provider=RouteProvider.FALLBACK,
            estimated_at=datetime(2026, 8, 26, 11, 30, tzinfo=timezone.utc),
        )


class DemoGemini:
    def generate_notification(self, **kwargs):
        return "Sipho has an upcoming lecture; follow the recommended preparation plan."


class SiphoConsumerStoryTests(unittest.TestCase):
    def test_complete_supported_autonomous_loop(self):
        events = InMemoryAgentEventRepository()
        notifications = NotificationService(events)
        commitment = Commitment(
            title="Entrepreneurship lecture",
            start_time=datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc),
            destination="Engineering Building B",
        )
        location = Location(
            latitude=37.42,
            longitude=-122.16,
            provider=LocationProvider.SIMULATED,
            captured_at=datetime(2026, 8, 26, 11, 30, tzinfo=timezone.utc),
        )
        common = dict(
            student_id="sipho-demo",
            commitment=commitment,
            current_location=location,
            preparation_profile=PreparationProfile(student_id="sipho-demo", average_prep_minutes=12),
            event_repo=events,
            notification_service=notifications,
            places_resolver=PlacesResolver(),
            routes_estimator=DemoRoutes(),
            gemini=DemoGemini(),
        )

        first = autonomous_evaluate(now=datetime(2026, 8, 26, 11, 30, tzinfo=timezone.utc), student_has_started_moving=False, **common)
        self.assertIn(first.decision, {AgentDecision.PREPARE, AgentDecision.LEAVE, AgentDecision.REPLAN})
        self.assertTrue(first.notification_sent)
        self.assertEqual(first.route_provider, "fallback")

        moving = autonomous_evaluate(now=datetime(2026, 8, 26, 11, 45, tzinfo=timezone.utc), student_has_started_moving=True, **common)
        self.assertIn(moving.decision, {AgentDecision.LEAVE, AgentDecision.NO_ACTION, AgentDecision.REPLAN})
        self.assertGreaterEqual(len(events.list_events("sipho-demo")), 1)


if __name__ == "__main__":
    unittest.main()
