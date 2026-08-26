# Submission evidence plan

This is the practical evidence package for the All Things Agentic Hackathon Taskmaster submission.

## Google Cloud proof links

- [Cloud Run service page](https://console.cloud.google.com/run/detail/us-central1/life-autopilot-agentic/metrics?project=gen-lang-client-0563563702)
- [Cloud Run service URL](https://life-autopilot-agentic-725797619054.us-central1.run.app)
- [Firestore databases](https://console.cloud.google.com/firestore/databases?project=gen-lang-client-0563563702)
- [Vertex AI console](https://console.cloud.google.com/vertex-ai?project=gen-lang-client-0563563702)
- [Successful Vertex AI test](https://console.cloud.google.com/logs/query?project=gen-lang-client-0563563702)
- [Deployed API Swagger](https://life-autopilot-agentic-725797619054.us-central1.run.app/docs)

## What the demo must prove

The agent receives several signals at once: multiple upcoming commitments, current location, destination/route context, preparation history, current time, and whether movement has started. It evaluates the whole set, chooses bounded actions, sends Gemini-generated intervention text, and records each result in the activity timeline.

## Four-minute recording plan

1. Explain the friction: a calendar knows the start time but does not decide when the student must act.
2. Show the Cloud Run URL and Swagger interface.
3. Create two commitments and post one simulated location.
4. Call the autonomous-cycle endpoint and show one decision per commitment.
5. Change movement state and call it again to show a different decision.
6. Open the events endpoint and show the recorded actions/notifications; show the Calendar action in Google Calendar.
7. Show Cloud Run, Firestore, and Vertex AI consoles as proof of the Google stack.

## Evidence checklist

- [ ] Video is public on YouTube or Vimeo and is no longer than four minutes.
- [ ] Architecture diagram is uploaded.
- [ ] Repository URL is included: https://github.com/SebastianKibiriti/life-autopilot-agentic
- [ ] Cloud Run URL and Swagger URL are included.
- [ ] Gemini 3.5 Flash via Vertex AI `global` is named explicitly.
- [ ] Google Gen AI SDK, Cloud Run, and Firestore are named explicitly.
- [ ] Demo shows autonomous action and event persistence, not only generated text.

Google Chat is not required for this account. A personal Gmail account cannot create incoming Chat webhooks; Calendar actions plus the Firestore audit trail provide the visible cross-app action for the MVP.
