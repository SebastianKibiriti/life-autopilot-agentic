# Project Briefing: Life Autopilot Agentic

## Executive Summary

Life Autopilot is a persistent personal companion that combines schedules, current context, travel, learned behavior, and user feedback to proactively personalize assistance. This is a hackathon rebuild for the All Things Agentic Hackathon targeting The Collaborative Partner category, using Gemini 3.5+, Google Gen AI SDK, and Google Cloud infrastructure.

## Product Summary

The product helps students who know a commitment exists but still discover too late that preparation and travel make the original plan impossible. It understands commitments, current context, and personal preparation patterns, then chooses the smallest useful intervention to keep students on schedule.

## User Problem

Students often know that a commitment exists but still discover too late that preparation and travel make the original plan impossible. A static calendar knows the start time. A reminder knows a fixed time. Life Autopilot should understand the commitment, current context, and personal preparation pattern, then choose the smallest useful intervention.

## Core Agent Workflow

1. **Observe** - Detect upcoming commitment and retrieve details
2. **Calculate** - Retrieve location, resolve destination, estimate route, get preparation profile
3. **Reason** - Calculate preparation and departure thresholds
4. **Act** - Agent evaluates and chooses intervention (PREPARE/LEAVE/REPLAN/ESCALATE)
5. **Monitor** - Verify student has moved or acted
6. **Re-evaluate** - Refresh context if circumstances changed
7. **Learn** - Update preparation profile based on actual outcomes

## Architecture Summary

**Target Hackathon Architecture:**
- Flutter + Riverpod mobile shell (user interface, permissions, timetable import)
- Cloud Run: FastAPI + Google ADK backend (orchestration, API boundary, provider adapters)
- Vertex AI: Gemini 3.5+ (contextual reasoning, notification copy, timetable extraction)
- Firestore: Persistent operational state and agent memory
- Google Routes API: Walking travel estimates
- Google Places API: Destination resolution
- Firebase: Authentication and push notifications (future)

**Current Local Implementation:**
- FastAPI with 9 endpoints for commitments, location, evaluation, learning, timetable
- Deterministic departure planner, bounded companion policy, and personalized suggestion memory
- In-memory repositories with Firestore adapter boundaries
- Gemini client wrapper with deterministic fallback
- Unit tests covering golden scenario (14:00 class with 22min travel, 12min prep)

## Technology Stack

**Frontend:** Flutter (Material 3), Riverpod, Dart
**Backend:** Python 3.14, FastAPI, Google ADK, Gemini via Vertex AI
**Database:** Firestore-backed persistence with in-memory local fallback
**Cloud:** Google Cloud Platform with Cloud Run deployment
**Testing:** unittest, FastAPI TestClient

## Current Verified State

**Implemented (Working):**
- Deterministic timing and decision logic
- Commitment repository interface and fake implementation
- Commitment CRUD and next-commitment query endpoints
- Location tracking and Places resolver (with campus cache)
- Routes estimator with Haversine fallback
- Gemini client wrapper with fallback for notifications
- Autonomous evaluation loop with bounded decisions
- Event log and notification recorder with dedup
- Preparation profile learning with conservative updates
- Timetable extract/confirm endpoints
- Timezone-aware datetime validation
- 39+ unit tests passing (1 Firestore integration test skipped by default)

**Partially Working:**
- Gemini 3.5+ configured but not verified with live Vertex API calls
- Places/Routes APIs require credentials
- Flutter dashboard is shell only, not connected to backend
- No background scheduler yet

**Not Started:**
- Google ADK orchestration
- Cloud Run deployment
- Firebase Authentication
- Push notifications
- Autonomous scheduler (immediate target)
- Timetable PDF/image extraction
- Real Flutter-to-backend integration

## Gaps

1. **Missing Background Scheduler** - autonomous evaluation without manual trigger
2. **Incomplete Mobile Client** - no network integration, permissions, notifications
3. **Missing Cloud Integration** - no ADK, no Firestore persistence, no Cloud Run
4. **Testing Gaps** - timezone DST, provider timeouts, notification idempotency
5. **Documentation** - activity timeline in Flutter, Cloud deployment procedures

## Risks

**Technical Risks:**
- External API dependencies (Gemini, Places, Routes) require credentials
- Timezone and DST handling not fully implemented
- Background threading and scheduling may introduce concurrency issues

**Hackathon Risks:**
- Current architecture uses GenAI SDK instead of ADK (may need adjustment)
- Demo requires working Google Cloud integration to impress judges
- Notification delivery system needs to move from event log to real push

## Documentation Contradictions

**Identified:**
- Documentation claims Gemini 3.5+ but only GenAI SDK is used
- Architecture documents ADK but implementation uses the SDK
- No explicit authentication or student identity boundaries

**Status:** The code (GenAI SDK) reflects current implementation; architecture needs updating

## Recommended Immediate Priority

**Add background scheduler (Phase 5, item 1):**
- Implement `AGENT_SCHEDULER_ENABLED` with configurable interval
- Start scheduler in FastAPI lifespan with dependency injection
- Evaluate registered students every 60 seconds by default
- Suppress duplicate PREPARE/LEAVE notifications within dedup window
- Integrate with existing autonomous evaluation logic

**Acceptance Criteria:**
- A configured interval evaluates students with upcoming commitments
- Duplicate PREPARE/LEAVE notifications are suppressed
- Scheduler can be disabled via environment config
- Missing location or unknown destination still escalates

## Recommended Next Five Tasks

1. **Background Scheduler Integration** - Add AgentScheduler to FastAPI with lifespan management
2. **Flutter Backend Integration** - Connect mobile shell to evaluate/location/event APIs
3. **Cloud Run Deployment** - Package FastAPI + ADK for Google Cloud deployment
4. **Live API Verification** - Test Gemini 3.5+, Places, and Routes with real credentials
5. **Authentication Integration** - Add student identity boundary and Firestore security

## Questions Requiring Clarification

1. **ADK vs SDK:** Should the project use Google ADK or the GenAI SDK for the hackathon?
2. **Authentication:** How should student identity be managed and scoped?
3. **Push Notifications:** What notification channel should be used (Firebase FCM, web push, custom)?
4. **Timetable Extraction:** Should PDF/image extraction be included, or just text?
5. **Deployment:** What's the expected demo deployment architecture?

## Summary

Life Autopilot is a well-architected but incomplete hackathon submission. The core deterministic logic works perfectly, but autonomous operation depends on the background scheduler. The project is at Phase 5 of development, with clear path to Phase 6 when the scheduler is implemented and cloud integration is established.
