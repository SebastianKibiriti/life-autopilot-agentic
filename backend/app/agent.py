"""Full Taskmaster agent loop.

Observe → Calculate → Reason → Act → Monitor → Re-evaluate → Learn

The deterministic planner handles arithmetic.  Gemini handles contextual
notification copy.  The notification service handles idempotent delivery.
All decisions are bounded to the explicit enum; no free-form LLM actions.
"""
from datetime import datetime, timezone

from .gemini import GeminiClient
from .context import departure_context
from .models import (
    AgentDecision,
    AgentEvent,
    AgentPhase,
    Commitment,
    EvaluationRequest,
    EvaluationResponse,
    EventOutcome,
    Location,
    PreparationProfile,
    TravelEstimate,
)
from .notifications import NotificationService
from .planner import plan_departure
from .routing import PlacesResolver, RoutesEstimator

_places_resolver = PlacesResolver()
_routes_estimator = RoutesEstimator()
_gemini = GeminiClient()


def evaluate(request: EvaluationRequest) -> tuple:
    """Legacy interface preserved for the /api/v1/agent/evaluate endpoint and existing tests."""
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


def autonomous_evaluate(
    *,
    student_id: str,
    now: datetime | None = None,
    commitment: Commitment,
    current_location: Location | None = None,
    preparation_profile: PreparationProfile | None = None,
    student_has_started_moving: bool = False,
    event_repo,
    notification_service: NotificationService,
    places_resolver: PlacesResolver | None = None,
    routes_estimator: RoutesEstimator | None = None,
    gemini: GeminiClient | None = None,
) -> EvaluationResponse:
    """Full autonomous evaluation: resolve location, route, decide, act, log."""
    now = now or datetime.now(timezone.utc)
    profile = preparation_profile or PreparationProfile(
        student_id=student_id, destination_key="default"
    )
    places = places_resolver or _places_resolver
    routes = routes_estimator or _routes_estimator
    gemini_client = gemini or _gemini

    # --- Resolve destination & travel estimate ---
    travel_minutes: int | None = None
    route_provider = "unavailable"
    travel_estimate: TravelEstimate | None = None

    if current_location:
        dest = places.resolve(commitment.destination)
        if dest is None:
            route_provider = "unavailable"
        else:
            travel_estimate = routes.estimate_walking(current_location, dest)
            travel_minutes = travel_estimate.duration_minutes
            route_provider = travel_estimate.provider.value

    # --- Deterministic planning ---
    plan = plan_departure(
        now=now,
        commitment_start=commitment.start_time,
        travel_minutes=travel_minutes,
        preparation_minutes=profile.average_prep_minutes,
        arrival_buffer_minutes=profile.arrival_buffer_minutes,
    )

    # --- Bounded decision ---
    if travel_minutes is None:
        decision = AgentDecision.ESCALATE
        reason = "Travel time is unavailable; location or route context is missing."
    elif plan.is_late and not student_has_started_moving:
        decision = AgentDecision.REPLAN
        reason = "The leave threshold has passed and movement has not started."
    elif plan.is_late and student_has_started_moving:
        decision = AgentDecision.LEAVE
        reason = "The leave threshold has arrived and movement is underway."
    elif plan.preparation_at and now >= plan.preparation_at:
        decision = AgentDecision.PREPARE
        reason = "The preparation window is open."
    else:
        decision = AgentDecision.NO_ACTION
        reason = "The commitment is currently on track."

    # --- Generate notification copy ---
    notification_body: str | None = None
    weather_observation: str | None = None
    traffic_observation: str | None = None
    notification_sent = False

    if decision not in (AgentDecision.NO_ACTION,):
        weather_observation, traffic_observation = departure_context(
            now=now, origin=current_location, destination=dest if current_location else None
        )
        notification_body = gemini_client.generate_notification(
            decision=decision,
            commitment_title=commitment.title,
            destination=commitment.destination,
            leave_at=plan.leave_at,
            preparation_at=plan.preparation_at,
            now=now,
            travel_minutes=travel_minutes,
            commitment_start=commitment.start_time,
            weather_observation=weather_observation,
            traffic_observation=traffic_observation,
        )
        title_map = {
            AgentDecision.PREPARE: "⏰ Time to get ready",
            AgentDecision.LEAVE: "🚶 Time to leave now",
            AgentDecision.REPLAN: "⚠️ Plan adjustment needed",
            AgentDecision.ESCALATE: "❗ Action required",
        }
        notification_title = title_map.get(decision, "Life Autopilot")

        notification_service.send(
            student_id=student_id,
            decision=decision,
            commitment_id=commitment.id,
            notification_title=notification_title,
            notification_body=notification_body or reason,
            reason=reason,
            now=now,
        )
        notification_sent = True
    else:
        # Still log NO_ACTION for the activity timeline
        event_repo.save_event(
            student_id,
            AgentEvent(
                student_id=student_id,
                commitment_id=commitment.id,
                timestamp=now,
                decision=decision,
                reason=reason,
                action="NO_ACTION",
                outcome=EventOutcome.DELIVERED,
            ),
        )

    return EvaluationResponse(
        commitment_title=commitment.title,
        preparation_at=plan.preparation_at,
        leave_at=plan.leave_at,
        decision=decision,
        reason=reason,
        route_provider=route_provider,
        notification_sent=notification_sent,
        notification_body=notification_body,
        weather_observation=weather_observation,
        traffic_observation=traffic_observation,
    )
