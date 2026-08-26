# Consumer Story: Sipho's Wednesday Lecture (Demo Slice)

Sipho Mbeki runs a premium bakery and studies part-time. On Wednesday he has a
14:00 Entrepreneurship lecture at Engineering Building B. His upcoming event
is imported from Google Calendar and his current position is supplied by the
mobile client (or simulated during the demo).

## What Life Autopilot can do today

The agent autonomously:

1. imports the upcoming commitment from Google Calendar;
2. combines the commitment, destination, current location, walking route, and
   learned preparation profile;
3. chooses `PREPARE`, `LEAVE`, `REPLAN`, or `ESCALATE` using Gemini;
4. sends the chosen intervention by Gmail and records an audit event;
5. re-evaluates when Sipho starts moving and learns from the outcome.

The demo uses a known destination and simulated location so it is deterministic
and does not require production Places/Routes keys.

## Deliberate scope boundary

The original story also described university-portal access, downloading and
printing notes, battery telemetry, WhatsApp, banking, POS, inventory, social
media, and a task manager. Those are future adapters, not current capabilities.
The agent must report those signals as unavailable rather than claim it acted
on them. The hackathon demo therefore proves the complete supported loop:
Calendar -> context -> route -> Gemini decision -> Gmail action -> audit ->
re-evaluation/learning.

## Honest demo outcome

If location or destination is missing, `ESCALATE` is the correct safety result.
With both present, the same commitment can produce a preparation or departure
intervention and later a moving/re-evaluation result.

## Companion Partner scenario

Sipho's lecture and supplier-errand stories remain regression and scenario
demonstrations. The primary Collaborative Partner story is now the separate
[Nutrition Companion demo](NUTRITION_COMPANION_API_DEMO.md), which proves
persistent preferences, campus knowledge, proactive fitness synthesis, a
Calendar action, and fast follow-up from stored context.
