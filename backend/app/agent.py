from .models import AgentDecision, EvaluationRequest
from .planner import plan_departure


def evaluate(request: EvaluationRequest):
    """Local Taskmaster policy; the ADK/Gemini adapter will replace reasoning later."""
    plan = plan_departure(
        now=request.now,
        commitment_start=request.commitment.start_time,
        travel_minutes=request.travel_minutes,
        preparation_minutes=request.preparation_minutes,
        arrival_buffer_minutes=request.arrival_buffer_minutes,
    )

    if request.travel_minutes is None:
        return plan, AgentDecision.ESCALATE, "Travel time is unavailable; destination context needs attention."
    if plan.is_late:
        if not request.student_has_started_moving:
            return plan, AgentDecision.REPLAN, "The leave threshold has passed and movement has not started."
        return plan, AgentDecision.LEAVE, "The leave threshold has arrived and movement is underway."
    if plan.preparation_at and request.now >= plan.preparation_at:
        return plan, AgentDecision.PREPARE, "The preparation window is open."
    return plan, AgentDecision.NO_ACTION, "The commitment is currently on track."
