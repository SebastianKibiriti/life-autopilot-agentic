import unittest
from datetime import datetime, timezone

from app.agent import autonomous_evaluate
from app.gemini import GeminiClient
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
            estimated_at=datetime(
                2026,
                8,
                18,
                13,
                0,
                tzinfo=timezone.utc,
            ),
        )


class FakeGemini:
    last_kwargs = None

    def generate_notification(self, **kwargs):
        self.last_kwargs = kwargs
        return "Time to get ready for class."


class AutonomousLoopTests(unittest.TestCase):

    def setUp(self):
        self.events = InMemoryAgentEventRepository()
        self.notifications = NotificationService(self.events)

        self.commitment = Commitment(
            title="Team Meeting with Client",
            start_time=datetime(
                2026,
                8,
                18,
                12,
                0,
                tzinfo=timezone.utc,
            ),
            destination="Engineering Building B",
            meeting_contact_email="client@example.com",
        )

        self.location = Location(
            latitude=37.4200,
            longitude=-122.1600,
            provider=LocationProvider.SIMULATED,
            captured_at=datetime(
                2026,
                8,
                18,
                11,
                22,
                tzinfo=timezone.utc,
            ),
        )

        self.profile = PreparationProfile(
            student_id="student-demo",
            average_prep_minutes=12,
            arrival_buffer_minutes=5,
        )

    def build_kwargs(
        self,
        *,
        now,
        moving=False,
        gemini=None,
    ):
        return dict(
            student_id="student-demo",
            now=now,
            commitment=self.commitment,
            current_location=self.location,
            preparation_profile=self.profile,
            student_has_started_moving=moving,
            event_repo=self.events,
            notification_service=self.notifications,
            places_resolver=PlacesResolver(),
            routes_estimator=FakeRoutesEstimator(),
            gemini=gemini or FakeGemini(),
        )

    def test_prepare_sends_notification_and_logs_event(self):
        now = datetime(
            2026,
            8,
            18,
            11,
            22,
            tzinfo=timezone.utc,
        )

        response = autonomous_evaluate(
            **self.build_kwargs(now=now)
        )

        self.assertEqual(
            response.decision,
            AgentDecision.PREPARE,
        )

        self.assertTrue(response.notification_sent)

        self.assertEqual(
            response.leave_at,
            datetime(
                2026,
                8,
                18,
                11,
                33,
                tzinfo=timezone.utc,
            ),
        )

        events = self.events.list_events("student-demo")

        self.assertEqual(len(events), 1)
        self.assertEqual(
            events[0].action,
            "NOTIFICATION_SENT",
        )

        # Preparation should not contact the meeting recipient.
        self.assertFalse(
            response.meeting_contact_notification_sent
        )

    def test_supplied_departure_observations_are_preserved(self):
        gemini = FakeGemini()

        now = datetime(
            2026,
            8,
            18,
            11,
            22,
            tzinfo=timezone.utc,
        )

        autonomous_evaluate(
            **self.build_kwargs(
                now=now,
                gemini=gemini,
            ),
            weather_observation="light rain, 17°C",
            traffic_observation="moderate traffic, highway delays",
        )

        self.assertEqual(
            gemini.last_kwargs["weather_observation"],
            "light rain, 17°C",
        )

        self.assertEqual(
            gemini.last_kwargs["traffic_observation"],
            "moderate traffic, highway delays",
        )

    def test_unknown_destination_escalates_instead_of_inventing_coordinates(self):
        unknown = self.commitment.model_copy(
            update={
                "destination": "Mystery Annex 12",
            }
        )

        now = datetime(
            2026,
            8,
            18,
            11,
            22,
            tzinfo=timezone.utc,
        )

        response = autonomous_evaluate(
            **self.build_kwargs(now=now)
            | {
                "commitment": unknown,
            }
        )

        self.assertEqual(
            response.decision,
            AgentDecision.ESCALATE,
        )

        self.assertEqual(
            response.route_provider,
            "unavailable",
        )

        self.assertFalse(
            response.meeting_contact_notification_sent
        )

    def test_missing_location_escalates(self):
        now = datetime(
            2026,
            8,
            18,
            11,
            22,
            tzinfo=timezone.utc,
        )

        response = autonomous_evaluate(
            **self.build_kwargs(now=now)
            | {
                "current_location": None,
            }
        )

        self.assertEqual(
            response.decision,
            AgentDecision.ESCALATE,
        )

    def test_replan_does_not_contact_meeting_recipient(self):
        """Being past the leave threshold is not itself enough to contact the client."""

        now = datetime(
            2026,
            8,
            18,
            11,
            40,
            tzinfo=timezone.utc,
        )

        response = autonomous_evaluate(
            **self.build_kwargs(
                now=now,
                moving=False,
            )
        )

        self.assertEqual(
            response.decision,
            AgentDecision.REPLAN,
        )

        self.assertTrue(
            response.notification_sent
        )

        self.assertFalse(
            response.meeting_contact_notification_sent
        )

        self.assertIsNone(
            response.meeting_contact_notification_body
        )

    def test_replan_eta_is_calculated_from_simulated_now(self):
        """The user-facing REPLAN response has enough context to report ETA."""

        now = datetime(
            2026,
            8,
            18,
            11,
            40,
            tzinfo=timezone.utc,
        )

        gemini = FakeGemini()

        response = autonomous_evaluate(
            **self.build_kwargs(
                now=now,
                moving=False,
                gemini=gemini,
            )
        )

        self.assertEqual(
            response.decision,
            AgentDecision.REPLAN,
        )

        self.assertEqual(
            gemini.last_kwargs["travel_minutes"],
            22,
        )

        self.assertEqual(
            gemini.last_kwargs["now"],
            now,
        )

        self.assertEqual(
            gemini.last_kwargs["commitment_start"],
            self.commitment.start_time,
        )

        # At 11:40 + 22 minutes = 12:02 UTC.
        expected_arrival = now.replace(
            hour=12,
            minute=2,
        )

        self.assertGreater(
            expected_arrival,
            self.commitment.start_time,
        )

    def test_replan_while_still_on_time_does_not_contact_client(self):
        """
        A REPLAN can occur after the leave threshold while the user
        could still arrive before the meeting. The recipient must
        remain untouched.
        """

        # Meeting at 12:00 UTC.
        # Leave threshold = 12:00 - 22 min travel - 5 min buffer
        #                 = 11:33 UTC.
        #
        # At 11:35 UTC, the leave threshold has passed, so the agent
        # must REPLAN because the student is still stationary.
        #
        # However, leaving immediately would produce:
        # 11:35 + 22 min = 11:57 UTC
        #
        # That is still 3 minutes before the 12:00 meeting.
        now = datetime(
            2026,
            8,
            18,
            11,
            35,
            tzinfo=timezone.utc,
        )

        response = autonomous_evaluate(
            **self.build_kwargs(
                now=now,
                moving=False,
            )
        )

        self.assertEqual(
            response.decision,
            AgentDecision.REPLAN,
        )

        # The user is still capable of arriving before the meeting,
        # so Life Autopilot must NOT contact the meeting recipient.
        self.assertFalse(
            response.meeting_contact_notification_sent
        )
    def test_leave_before_meeting_does_not_contact_client(self):
        """
        LEAVE alone is not enough to contact the recipient.
        The estimated arrival must actually be after the meeting.
        """

        now = datetime(
            2026,
            8,
            18,
            11,
            35,
            tzinfo=timezone.utc,
        )

        # 11:35 + 22 = 11:57, before the 12:00 meeting.
        response = autonomous_evaluate(
            **self.build_kwargs(
                now=now,
                moving=True,
            )
        )

        self.assertEqual(
            response.decision,
            AgentDecision.LEAVE,
        )

        self.assertTrue(
            response.notification_sent
        )

        self.assertFalse(
            response.meeting_contact_notification_sent
        )

    def test_late_leave_contacts_meeting_recipient(self):
        """
        This is the important courtesy-to-client scenario.

        Meeting: 12:00 UTC
        Current simulated time: 11:45 UTC
        Travel: 22 minutes
        ETA: 12:07 UTC

        Therefore the client should be informed.
        """

        now = datetime(
            2026,
            8,
            18,
            11,
            45,
            tzinfo=timezone.utc,
        )

        response = autonomous_evaluate(
            **self.build_kwargs(
                now=now,
                moving=True,
            )
        )

        self.assertEqual(
            response.decision,
            AgentDecision.LEAVE,
        )

        self.assertTrue(
            response.notification_sent
        )

        self.assertTrue(
            response.meeting_contact_notification_sent
        )

        self.assertIsNotNone(
            response.meeting_contact_notification_body
        )

        self.assertIn(
            "12:07 UTC",
            response.meeting_contact_notification_body,
        )

        self.assertIn(
            "12:00 UTC",
            response.meeting_contact_notification_body,
        )

    def test_notification_dedup_does_not_persist_a_second_event(self):
        now = datetime(
            2026,
            8,
            18,
            11,
            22,
            tzinfo=timezone.utc,
        )

        kwargs = self.build_kwargs(now=now)

        autonomous_evaluate(**kwargs)
        autonomous_evaluate(**kwargs)

        self.assertEqual(
            len(self.events.list_events("student-demo")),
            1,
        )

    def test_preparation_window_requests_prepare(self):
        now = datetime(
            2026,
            8,
            18,
            11,
            22,
            tzinfo=timezone.utc,
        )

        response = autonomous_evaluate(
            **self.build_kwargs(now=now)
        )

        self.assertEqual(
            response.decision,
            AgentDecision.PREPARE,
        )


class PreparationLearningTests(unittest.TestCase):

    def test_observation_updates_bounded_average(self):
        repo = InMemoryPreparationProfileRepository()

        first = repo.update_with_observation(
            "student-demo",
            "default",
            20,
        )

        second = repo.update_with_observation(
            "student-demo",
            "default",
            10,
        )

        self.assertEqual(
            first.sample_count,
            2,
        )

        self.assertEqual(
            second.sample_count,
            3,
        )

        self.assertGreaterEqual(
            second.average_prep_minutes,
            5,
        )

        self.assertLessEqual(
            second.average_prep_minutes,
            60,
        )

        self.assertGreater(
            second.confidence,
            first.confidence,
        )


if __name__ == "__main__":
    unittest.main()