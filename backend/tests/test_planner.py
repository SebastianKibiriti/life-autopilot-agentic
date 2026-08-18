import unittest
from datetime import datetime, timezone

from app.agent import evaluate
from app.models import AgentDecision, Commitment, EvaluationRequest
from app.planner import plan_departure


class DeparturePlannerTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 8, 18, 12, 0, tzinfo=timezone.utc)

    def test_calculates_preparation_and_leave_thresholds(self):
        plan = plan_departure(
            now=datetime(2026, 8, 18, 11, 20, tzinfo=timezone.utc),
            commitment_start=self.start,
            travel_minutes=22,
            preparation_minutes=12,
            arrival_buffer_minutes=5,
        )
        self.assertEqual(plan.leave_at, datetime(2026, 8, 18, 11, 33, tzinfo=timezone.utc))
        self.assertEqual(plan.preparation_at, datetime(2026, 8, 18, 11, 21, tzinfo=timezone.utc))
        self.assertFalse(plan.is_late)

    def test_missing_route_escalates(self):
        request = EvaluationRequest(
            now=datetime(2026, 8, 18, 11, 20, tzinfo=timezone.utc),
            commitment=Commitment(title="Class", start_time=self.start, destination="Room A"),
            travel_minutes=None,
        )
        plan, decision, _ = evaluate(request)
        self.assertEqual(plan.route_provider, "unavailable")
        self.assertEqual(decision, AgentDecision.ESCALATE)

    def test_past_leave_threshold_replans_if_student_is_not_moving(self):
        request = EvaluationRequest(
            now=datetime(2026, 8, 18, 11, 40, tzinfo=timezone.utc),
            commitment=Commitment(title="Class", start_time=self.start, destination="Room A"),
            travel_minutes=22,
            preparation_minutes=12,
            arrival_buffer_minutes=5,
            student_has_started_moving=False,
        )
        _, decision, reason = evaluate(request)
        self.assertEqual(decision, AgentDecision.REPLAN)
        self.assertIn("movement", reason)

    def test_preparation_window_requests_prepare(self):
        request = EvaluationRequest(
            now=datetime(2026, 8, 18, 11, 22, tzinfo=timezone.utc),
            commitment=Commitment(title="Class", start_time=self.start, destination="Room A"),
            travel_minutes=22,
            preparation_minutes=12,
            arrival_buffer_minutes=5,
        )
        _, decision, _ = evaluate(request)
        self.assertEqual(decision, AgentDecision.PREPARE)


if __name__ == "__main__":
    unittest.main()
