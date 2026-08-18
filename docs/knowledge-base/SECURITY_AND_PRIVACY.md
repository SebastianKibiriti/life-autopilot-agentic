# Security and privacy

## Location data

Collect only the current location needed to calculate the next action. Avoid continuous movement histories unless the product explicitly needs them. Store timestamps, accuracy, retention, and purpose with any persisted location snapshot. Delete or expire historical location data that is no longer needed for the demo.

## Authentication and authorization

Every student-scoped read and write must be tied to an authenticated student ID once authentication is added. Firestore rules must prevent one student from reading another student's commitments, locations, preparation profile, or agent events.

## Secrets and API keys

Keep Vertex AI, Routes, Places, Firebase, and service-account credentials server-side or in platform configuration. The Flutter app must never receive a privileged Google Cloud credential. `.env.example` may document names, not values.

## Firestore access

Use least-privilege service accounts and narrowly scoped collections. Validate ownership at the API boundary and enforce it again in rules where applicable. Avoid broad admin credentials in local or deployed application code.

## Logs and events

Operational logs may include decision type, timestamps, provider status, and concise reasons. Do not log raw location streams, access tokens, full user profiles, or private chain-of-thought. Redact sensitive request fields in error logs.

## Provider failures

Failures should reveal a safe status to the user without exposing credentials or internal stack traces. The system should prefer `ESCALATE`, an explicit unavailable state, or a labelled fallback over invented context.

