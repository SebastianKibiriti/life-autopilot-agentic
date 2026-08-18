Create a complete project knowledge base for the current Life Autopilot hackathon rebuild.

The purpose of this knowledge base is to let another AI coding agent enter the repository later, read the documentation, and understand the project accurately without needing access to this conversation history.

The project is Life Autopilot, being rebuilt as a fresh submission for the All Things Agentic Hackathon.

The target category is:
The Taskmaster.

The central product definition is:

Life Autopilot is an autonomous student operations agent that continuously combines upcoming commitments, the student's current location, travel time, and learned preparation behavior to determine when the student needs to act, then proactively intervenes before the student has to ask.

The core autonomous loop is:

Observe
→ Calculate
→ Reason
→ Act
→ Monitor
→ Re-evaluate
→ Learn

The most important workflow is:

Upcoming commitment detected
→ retrieve commitment details
→ retrieve current location
→ resolve destination
→ estimate route/travel time
→ retrieve preparation profile
→ calculate preparation and departure thresholds
→ agent evaluates the situation
→ take appropriate action
→ verify whether the student acted
→ re-evaluate if circumstances changed
→ update learned behavior where appropriate

The primary demo scenario is:

A student has a class at 14:00.

Life Autopilot determines:
- current location;
- destination;
- current travel duration;
- arrival safety buffer;
- learned preparation duration.

It calculates when preparation should start and when the student should leave.

The student does nothing.

Life Autopilot autonomously sends the preparation notification and later the departure notification.

If the student has not moved after the planned departure time, Life Autopilot checks fresh context, determines whether the original plan is still viable, and changes its recommendation if necessary.

This autonomous intervention, verification, and replanning loop is the single most important feature in the hackathon build.

Hackathon-required stack currently planned:

Mobile:
- Flutter
- Dart
- Riverpod

Backend:
- Python
- FastAPI

Agent framework:
- Google ADK

AI:
- Gemini 3.5 or newer
- accessed through Vertex AI unless there is a documented technical reason to change this

Google Cloud:
- Cloud Run for the FastAPI + ADK backend
- Firestore for persistent operational state and agent memory

Other planned services:
- Firebase Authentication
- Firebase Cloud Messaging and/or Flutter local notifications
- Google Routes API
- Google Places API
- Gemini multimodal for timetable extraction
- Cloud Scheduler and/or Pub/Sub only where actually necessary for autonomous scheduling

Architecture principles:

1. The AI model is not responsible for basic arithmetic.
   Deterministic application code calculates travel thresholds, preparation thresholds, lateness, and similar values.

2. Gemini reasons about ambiguous or changing circumstances:
   - whether intervention is necessary;
   - whether the original plan is still viable;
   - whether to replan;
   - whether escalation is appropriate;
   - how contextual changes affect the next action.

3. Google ADK is the orchestration layer for the agent and its tools.

4. Firestore is the persistent operational source of truth for the hackathon backend.

5. The application should use explicit state rather than relying entirely on LLM conversation history.

6. The system must fail safely and degrade gracefully if Gemini, Routes, location, notifications, or another provider is unavailable.

7. Avoid unnecessary complexity and scope creep.

8. This is a hackathon build, not a complete commercial Life Autopilot rebuild.

Important planned agent states:

Normal:
- IDLE
- COMMITMENT_UPCOMING
- PREPARATION_WINDOW
- LEAVE_WINDOW
- IN_TRANSIT
- ARRIVED
- COMPLETE

Exceptional:
- RUNNING_LATE
- ROUTE_CHANGED
- LOCATION_UNAVAILABLE
- ROUTE_PROVIDER_FAILED
- DESTINATION_UNKNOWN
- NOTIFICATION_FAILED

Important planned agent decisions:
- NO_ACTION
- PREPARE
- LEAVE
- REPLAN
- ESCALATE

Important planned tools:

Schedule:
- get_next_commitment
- get_commitment_details
- get_destination

Context:
- get_current_location
- get_student_state
- get_preparation_profile

Travel:
- estimate_route
- get_alternative_routes

Memory:
- get_departure_history
- record_departure_event
- update_preparation_profile

Actions:
- send_prepare_notification
- send_leave_notification
- send_escalation
- record_agent_decision

Important domain models should include at minimum:
- Student
- Commitment
- Location
- Destination
- TravelEstimate
- PreparationProfile
- AgentState
- AgentDecision
- AgentEvent

The deterministic timing model should conceptually follow:

latest_leave_time =
commitment_start
- travel_duration
- arrival_buffer

prepare_time =
latest_leave_time
- preparation_duration

Example golden scenario:

Commitment:
Database Systems

Start:
14:00

Travel:
22 minutes

Preparation:
12 minutes

Arrival buffer:
5 minutes

Expected:
13:21 → PREPARE
13:33 → LEAVE
13:37 and student still stationary → REPLAN

Use this scenario as a recurring reference test throughout development.

Persistent behavioral learning should remain conservative.

Initially learn things such as:
- planned preparation time;
- actual departure/movement time;
- planned departure time;
- estimated real preparation duration.

Use simple, explainable updating before attempting sophisticated machine learning.

The project should eventually support timetable import through:
PDF/image/photo
→ Gemini extraction
→ structured data
→ validation
→ user review
→ save.

Never automatically trust extracted timetable data.

Scope that is explicitly lower priority or deferred:
- large campus knowledge graph;
- generic chatbot;
- full lifestyle management;
- budgeting;
- social features;
- complex multi-agent architecture;
- elaborate animations;
- advanced analytics;
- iOS;
- voice;
- large productivity suite;
- email management.

The old Life Autopilot project existed before this hackathon.

The hackathon repository should be treated as a fresh implementation.

Do not silently copy historical code into the new project.

If pre-existing code is reused:
- identify it;
- document where it came from;
- explain why it was reused;
- include it in the hackathon disclosure documentation.

The project knowledge base must be maintained as development progresses.

Create a structured documentation system under a suitable directory such as:

docs/
  knowledge-base/
    PROJECT_OVERVIEW.md
    PRODUCT_VISION.md
    HACKATHON_CONTEXT.md
    ARCHITECTURE.md
    AGENT_DESIGN.md
    DATA_MODEL.md
    AUTONOMOUS_WORKFLOW.md
    SERVICES_AND_INTEGRATIONS.md
    MOBILE_APP.md
    BACKEND.md
    DECISION_ENGINE.md
    MEMORY_AND_LEARNING.md
    SECURITY_AND_PRIVACY.md
    TESTING_STRATEGY.md
    DEMO_AND_SUBMISSION.md
    DEVELOPMENT_HISTORY.md
    CURRENT_STATE.md
    NEXT_STEPS.md
    DECISIONS.md
    KNOWN_ISSUES.md
    GLOSSARY.md

Also create:

KNOWLEDGE_BASE.md

at the repository root.

KNOWLEDGE_BASE.md should act as the entry point for future AI agents.

It should explain:
- what this project is;
- what problem it solves;
- hackathon category;
- current scope;
- core architecture;
- required Google technologies;
- where each knowledge-base document lives;
- which documents should be read first;
- current development phase;
- latest known working state;
- major constraints;
- next recommended task.

Create an AI onboarding section in KNOWLEDGE_BASE.md called:

"Instructions for a New AI Agent"

It should tell a new agent to:

1. Read KNOWLEDGE_BASE.md first.
2. Read CURRENT_STATE.md.
3. Read DECISIONS.md.
4. Read NEXT_STEPS.md.
5. Read the relevant subsystem document before editing code.
6. Inspect the actual repository before assuming documentation is correct.
7. Update the knowledge base whenever meaningful implementation changes are made.
8. Never silently change architecture decisions.
9. Record important architectural changes in DECISIONS.md.
10. Record completed milestones in DEVELOPMENT_HISTORY.md.
11. Update CURRENT_STATE.md at the end of substantial development sessions.
12. Keep NEXT_STEPS.md synchronized with the actual project.
13. Clearly distinguish:
    - implemented;
    - partially implemented;
    - planned;
    - deferred;
    - abandoned.
14. Never claim something works unless verified.
15. Preserve hackathon eligibility and mandatory Google technology requirements.

For DECISIONS.md, use an Architecture Decision Record style.

Each decision should include:
- ID;
- date;
- title;
- status;
- context;
- decision;
- reasoning;
- alternatives considered;
- consequences.

For CURRENT_STATE.md, maintain sections for:
- Working
- Partially Working
- Not Started
- Broken / Known Problems
- External Configuration Required
- Last Verified Tests
- Current Git branch
- Latest relevant commit
- Current development phase

For DEVELOPMENT_HISTORY.md, use chronological entries that explain:
- what was attempted;
- what changed;
- what was verified;
- what failed;
- why important decisions were made.

For NEXT_STEPS.md:
- identify the next immediate implementation target;
- list dependencies;
- define acceptance criteria;
- identify blockers;
- list the next 3–5 tasks in priority order.

For SERVICES_AND_INTEGRATIONS.md, document each external dependency including:
- service;
- purpose;
- where it is used;
- credentials/configuration required;
- environment variables;
- fallback behavior;
- expected failure modes;
- whether it is mandatory for the hackathon.

For SECURITY_AND_PRIVACY.md, pay particular attention to:
- location data;
- authentication;
- server-side secrets;
- Firestore access controls;
- API keys;
- retention of location history;
- logs;
- least-privilege principles.

For TESTING_STRATEGY.md, define:
- unit tests;
- integration tests;
- agent tool tests;
- failure tests;
- end-to-end tests;
- the golden 14:00 commitment scenario.

For DEMO_AND_SUBMISSION.md, preserve the intended demo story:

Problem:
Calendars know when class starts, but they do not continuously determine when the student actually needs to act.

Demo:
- show next commitment;
- show current context;
- let the system act autonomously;
- show preparation notification;
- show departure notification;
- simulate the student not moving;
- show agent verification;
- show replanning;
- show behavioral learning affecting a later decision;
- show agent activity log;
- show Google Cloud deployment proof.

Also document submission requirements including:
- Gemini 3.5+;
- Google ADK or another qualifying Google agent framework if architecture changes;
- Google Cloud infrastructure;
- hosted/testable project where practical;
- public repository or judge-accessible private repository;
- README setup instructions;
- architecture diagram;
- public demo video under four minutes;
- Google Cloud proof in the demo;
- pre-existing work disclosure.

Repository structure should initially aim for:

life-autopilot-agentic/
  mobile/
  backend/
  docs/
    knowledge-base/
    architecture/
    testing/
    hackathon/
  infrastructure/
  README.md
  KNOWLEDGE_BASE.md
  PROJECT_STATE.md
  .env.example

Do not blindly create duplicate documentation if equivalent files already exist.

First:
1. inspect the entire repository;
2. identify existing files and implementation state;
3. determine what is actually built;
4. determine what documentation already exists;
5. reconcile any contradictions between code and documentation.

Then build the knowledge base from verified repository evidence.

Very important:

Do not treat this prompt as proof that planned features are already implemented.

Anything described here as planned must remain marked as planned until verified in code.

Use the repository as the final source of truth for implementation status.

At the end, provide a summary containing:

1. every documentation file created or updated;
2. the current verified project state;
3. major architectural decisions recorded;
4. any contradictions found between project plans and implementation;
5. missing information that future development should resolve;
6. the recommended next engineering task.

The final knowledge base should be detailed enough that a capable AI coding agent with no access to previous chat history can read it and continue building Life Autopilot without first asking for a complete project explanation.
