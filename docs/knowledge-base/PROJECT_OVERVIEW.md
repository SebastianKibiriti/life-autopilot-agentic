# Project overview

## Identity

- Project: Life Autopilot Agentic
- Hackathon: All Things Agentic Hackathon
- Target category: The Collaborative Partner
- Repository status: fresh hackathon rebuild
- Current baseline: `9c97420 feat: establish hackathon agent foundation`

## Product definition

Life Autopilot is an autonomous student operations agent that combines upcoming commitments, current location, travel time, and learned preparation behavior to determine when the student needs to act, then proactively intervenes before the student asks.

The product is not primarily a calendar, reminder, or chatbot. Its differentiator is responsibility for the outcome: keeping the student on schedule through autonomous observation, action, verification, and replanning.

## User problem

Students often know that a commitment exists but still discover too late that preparation and travel make the original plan impossible. A static calendar knows the start time. A reminder knows a fixed time. Life Autopilot should understand the commitment, current context, and personal preparation pattern, then choose the smallest useful intervention.

## Primary demo

1. A student has Database Systems at 14:00.
2. The agent has a 22-minute travel estimate, a 5-minute arrival buffer, and a 12-minute preparation estimate.
3. It calculates `PREPARE` at 13:21 and `LEAVE` at 13:33.
4. The student does nothing; the agent sends the preparation and departure notifications without a chat request.
5. At 13:37, the student is still stationary; the agent refreshes context and chooses `REPLAN`.

## Judging fit

The build is aimed at the Collaborative Partner concept: a persistent companion that retrieves context, learns preferences, synthesizes messy schedule and campus data, and takes lightweight actions. It should visibly personalize assistance, show disciplined state and failure handling, and provide a live, reproducible Google Cloud demonstration.

## Non-goals

This hackathon version is not a general life-management suite, social network, budgeting tool, email manager, study-planning platform, campus knowledge graph, multi-agent system, or commercial-scale rewrite.
