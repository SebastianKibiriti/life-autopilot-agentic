You are joining an existing software project called Life Autopilot.

Your first responsibility is NOT to write code.

Your first responsibility is to fully understand the project before making any architectural, implementation, or product decisions.

The repository contains a project knowledge base. Treat the knowledge base as the primary source of project intent, but treat the actual codebase as the final source of truth for implementation status.

Your task is to perform a complete project onboarding and understanding process.

PHASE 1 — READ THE KNOWLEDGE BASE

Read the following documents in this order if they exist:

1. KNOWLEDGE_BASE.md
2. CURRENT_STATE.md
3. PROJECT_OVERVIEW.md
4. PRODUCT_VISION.md
5. HACKATHON_CONTEXT.md
6. ARCHITECTURE.md
7. AGENT_DESIGN.md
8. AUTONOMOUS_WORKFLOW.md
9. DATA_MODEL.md
10. DECISION_ENGINE.md
11. MEMORY_AND_LEARNING.md
12. SERVICES_AND_INTEGRATIONS.md
13. SECURITY_AND_PRIVACY.md
14. TESTING_STRATEGY.md
15. DEMO_AND_SUBMISSION.md
16. DECISIONS.md
17. DEVELOPMENT_HISTORY.md
18. NEXT_STEPS.md
19. KNOWN_ISSUES.md
20. GLOSSARY.md

Do not skip documents.

Build an internal understanding of:
- project purpose;
- problem being solved;
- target users;
- architecture;
- technologies;
- agent design;
- current implementation status;
- development priorities;
- known limitations;
- hackathon requirements.

--------------------------------------------------

PHASE 2 — INSPECT THE REPOSITORY

Inspect the actual repository structure.

Determine:

- what code exists;
- what services exist;
- what APIs exist;
- what screens exist;
- what tests exist;
- what infrastructure exists;
- what integrations exist;
- what documentation exists.

Do not assume documentation is accurate.

Verify documentation claims against code.

Identify:

- implemented features;
- partially implemented features;
- planned features;
- missing features;
- abandoned features.

--------------------------------------------------

PHASE 3 — RECONCILE DOCUMENTATION AND CODE

Create a comparison between:

A. Intended architecture
B. Actual implementation

For every major subsystem determine:

Status:
- Implemented
- Partially Implemented
- Planned
- Missing
- Unknown

Examples:

- Flutter mobile app
- FastAPI backend
- Google ADK
- Gemini integration
- Vertex AI
- Firestore
- Routes API
- Places API
- Notifications
- Timetable import
- Behavioral learning
- Agent decision engine
- Activity log
- Replanning logic
- Background execution
- Testing framework

Highlight any contradictions.

Example:

"Documentation says Firestore is implemented but no Firestore integration exists."

or

"Current code uses local storage despite architecture specifying Firestore."

--------------------------------------------------

PHASE 4 — UNDERSTAND THE PRODUCT

Explain the product in your own words.

Answer:

1. What problem is Life Autopilot solving?

2. Why is it different from a normal reminder app?

3. Why is it considered an autonomous agent?

4. What is the most important workflow in the project?

5. What is the golden demonstration scenario?

6. What are the most important judging points for the hackathon?

7. Which features are mission-critical?

8. Which features are optional?

9. Which features should not be built during the hackathon?

--------------------------------------------------

PHASE 5 — UNDERSTAND THE AGENT

Explain:

- agent goals;
- agent responsibilities;
- agent state machine;
- agent tools;
- agent memory;
- decision process;
- learning process;
- replanning process.

Describe the intended loop:

Observe
→ Calculate
→ Reason
→ Act
→ Verify
→ Re-evaluate
→ Learn

Explain how each step is expected to work in this project.

--------------------------------------------------

PHASE 6 — UNDERSTAND THE HACKATHON

Determine:

- hackathon category;
- required technologies;
- submission requirements;
- architectural constraints;
- disclosure requirements;
- deployment expectations.

Verify whether the project appears aligned with those requirements.

Identify risks that could hurt judging.

--------------------------------------------------

PHASE 7 — PRODUCE A PROJECT BRIEFING

After completing all analysis, create a structured report containing:

# Executive Summary

A concise explanation of the project.

# Product Summary

What the product does.

# User Problem

What pain point is being solved.

# Core Agent Workflow

Step-by-step explanation.

# Architecture Summary

Major systems and their responsibilities.

# Technology Stack

Frontend, backend, AI, cloud, storage, integrations.

# Current Verified State

What is actually working.

# Gaps

What is missing.

# Risks

Technical and hackathon risks.

# Documentation Contradictions

Any mismatch between docs and code.

# Recommended Immediate Priority

The single most important next task.

# Recommended Next Five Tasks

Ordered by priority.

# Questions Requiring Clarification

Anything that cannot be determined from the repository.

--------------------------------------------------

IMPORTANT RULES

- Do not write code yet.
- Do not refactor anything yet.
- Do not redesign the architecture yet.
- Do not create new features yet.

Your goal is understanding before action.

Assume nothing.

Verify everything.

Distinguish clearly between:
- documented;
- implemented;
- verified;
- assumed;
- planned.

If documentation and code disagree, trust the code and report the discrepancy.

Only after completing this onboarding process should implementation work begin.