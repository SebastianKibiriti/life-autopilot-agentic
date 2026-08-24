# Demo and submission

## Problem

Calendars know when class starts, but they do not continuously determine when the student actually needs to act.

## Intended demo

1. Show the next commitment.
2. Show current location, destination, travel duration, buffer, and learned preparation context.
3. Let the system act autonomously without a chat request.
4. Show the preparation notification.
5. Show the departure notification.
6. Simulate the student not moving.
7. Show agent verification with fresh context.
8. Show replanning.
9. Show behavioral learning affecting a later decision.
10. Show the structured agent activity log.
11. Show Google Cloud deployment proof.

## Submission requirements to preserve

- Gemini 3.5+.
- Google ADK or another qualifying Google agent framework if the architecture changes.
- At least one Google Cloud infrastructure service.
- Hosted/testable project where practical.
- Public repository or judge-accessible private repository.
- README setup instructions.
- Uploaded architecture diagram.
- Public demo video under four minutes.
- Google Cloud proof in the demo video.
- Disclosure of pre-existing work and third-party material.

## Minimal readiness checklist

- [x] Public repository with setup instructions.
- [x] Backend autonomous loop, event log, scheduler, and Firestore adapter.
- [x] Flutter client passes `flutter analyze`.
- [x] Backend tests pass locally.
- [x] Cloud Run packaging is committed.
- [ ] Deploy the backend to Cloud Run and record the URL.
- [ ] Verify one live Vertex AI evaluation using the configured project.
- [ ] Record a short demo video showing the autonomous decision and event log.
- [ ] Upload the architecture diagram and video to Devpost.

Firebase push notifications, production Places/Routes keys, and user authentication are optional for this MVP and should not delay submission.
