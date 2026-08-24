# Agent behavior

NON-NEGOTIABLE PRODUCT PRINCIPLE

Life Autopilot is not a chat application.

Life Autopilot is not intended to be actively used throughout the day.

The primary user experience occurs while the application is in the background.

The agent is expected to initiate interactions.

The user should not need to open the application in order for the core value of the product to be delivered.

Opening the application should primarily serve:

- onboarding
- configuration
- reviewing agent activity
- viewing upcoming commitments
- reviewing learned behavior
- troubleshooting

The core product value is delivered through autonomous monitoring, decision making, and intervention.

## Core loop

```text
Observe → Calculate → Reason → Act → Monitor → Re-evaluate → Learn
```

The agent should act without waiting for a chat prompt when an upcoming commitment crosses an intervention threshold.

## Normal states

```text
IDLE
  ↓ relevant commitment found
COMMITMENT_UPCOMING
  ↓ preparation threshold reached
PREPARATION_WINDOW
  ↓ leave threshold reached
LEAVE_WINDOW
  ↓ movement detected
IN_TRANSIT
  ↓ destination reached
ARRIVED
  ↓ commitment complete
COMPLETE
```

## Exceptional states

- `RUNNING_LATE` — the current plan cannot meet the commitment without a changed intervention.
- `ROUTE_CHANGED` — a fresh route differs enough to invalidate the active plan.
- `LOCATION_UNAVAILABLE` — no trustworthy current location exists.
- `ROUTE_PROVIDER_FAILED` — live routing failed; a clearly labelled fallback may be used.
- `DESTINATION_UNKNOWN` — a human-readable destination could not be resolved confidently.
- `NOTIFICATION_FAILED` — the action was chosen but delivery was not confirmed.

## Bounded decisions

- `NO_ACTION` — context is on track or intervention would be premature.
- `PREPARE` — tell the student to begin preparation and include the calculated leave time.
- `LEAVE` — tell the student to leave now.
- `REPLAN` — refresh context and choose a different viable plan because the original is no longer safe.
- `ESCALATE` — ask for missing input or make the provider failure visible instead of guessing.

## Deterministic timing

```text
latest_leave_time = commitment_start - travel_duration - arrival_buffer
prepare_time = latest_leave_time - preparation_duration
```

Golden scenario:

| Time | Context | Expected decision |
|---|---|---|
| 13:21 | preparation threshold reached | `PREPARE` |
| 13:33 | leave threshold reached | `LEAVE` |
| 13:37 | student still stationary | `REPLAN` |

The current local implementation uses the same arithmetic and decision vocabulary. It does not yet send notifications or retrieve fresh context.

## Intervention policy

Prefer the smallest useful action. Avoid repeated notifications when the student has already acknowledged or started moving. Re-evaluate after a meaningful context change, not on arbitrary LLM conversation turns.

## Learning policy

Initially record planned preparation time, planned departure time, actual movement time, and estimated real preparation duration. Update simple averages or bounded estimates with sample counts and confidence. Never let one anomalous trip radically rewrite the profile.

