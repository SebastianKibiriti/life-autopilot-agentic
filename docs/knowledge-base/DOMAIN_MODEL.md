# Domain model

The current API has only a minimal `Commitment` and evaluation snapshot. The entities below are the target model; fields marked as planned are not yet implemented.

## Student (planned)

```text
id: string
name: string
timezone: IANA timezone
university: string | null
preferences: map
```

## Commitment

Implemented fields:

```text
title: string
start_time: datetime
destination: string
```

Planned additions:

```text
id: string
end_time: datetime | null
destination_coordinates: Location | null
source: manual | import | calendar
status: active | completed | cancelled
```

## Location (planned)

```text
latitude: decimal
longitude: decimal
accuracy_meters: decimal | null
captured_at: datetime
provider: gps | simulated | unavailable
```

## Destination (planned)

```text
label: string
latitude: decimal
longitude: decimal
formatted_address: string | null
resolution_confidence: decimal | null
provider: places | manual | cached
```

## TravelEstimate (planned)

```text
origin: Location
destination: Destination
mode: walking | driving | transit
distance_meters: integer
duration_seconds: integer
provider: routes | fallback
estimated_at: datetime
```

## PreparationProfile (planned)

```text
student_id: string
destination_key: string
average_prep_minutes: integer
arrival_buffer_minutes: integer
usual_mode: string
confidence: decimal
sample_count: integer
updated_at: datetime
```

Learning must start with explainable aggregates, not opaque model training.

## AgentState (planned)

```text
student_id: string
current_commitment_id: string | null
phase: explicit state enum
last_evaluation_at: datetime | null
next_evaluation_at: datetime | null
last_known_location: Location | null
active_plan: plan snapshot | null
version: integer
```

## AgentDecision

Implemented enum values:

```text
NO_ACTION
PREPARE
LEAVE
REPLAN
ESCALATE
```

## AgentEvent (planned)

```text
id: string
student_id: string
commitment_id: string | null
timestamp: datetime
observation: structured snapshot
context: structured operational inputs
decision: AgentDecision
action: structured action result
outcome: pending | delivered | acknowledged | failed | superseded
```

Do not persist private chain-of-thought. Persist only operational facts and concise reasons.

