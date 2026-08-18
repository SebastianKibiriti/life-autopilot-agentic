# Services and integrations

| Service | Purpose | Current use | Configuration | Fallback / failure | Hackathon mandatory |
|---|---|---|---|---|---|
| Gemini 3.5+ via Vertex AI | Contextual reasoning and timetable extraction | Not started | Google Cloud project, Vertex AI access, model name | Bounded deterministic policy; escalate when reasoning unavailable | Yes, Gemini required |
| Google ADK | Agent orchestration and tool execution | Not started | ADK runtime and model configuration | Local policy/fake tools during development | Yes, or another qualifying Google framework |
| Cloud Run | Host FastAPI + ADK backend | Not started | Project, region, service account, deploy command | Local Uvicorn for development | Google Cloud infrastructure required; Cloud Run planned |
| Firestore | Operational source of truth and agent memory | Adapter implemented and fake-tested; real SDK/project not verified | `google-cloud-firestore`, project/database, service account, security rules | Local in-memory repository | Google Cloud infrastructure required; Firestore planned |
| Google Routes API | Travel duration and distance | Not started; duration is currently supplied directly | API credentials/key and enabled API | Clearly labelled fallback or escalation | No, but central to product behavior |
| Google Places API | Destination resolution | Not started | API credentials/key and enabled API | Manual destination, cache, or `DESTINATION_UNKNOWN` | No |
| Device location | Current student context | Not started | Mobile permission and platform configuration | `LOCATION_UNAVAILABLE`; no fabricated coordinates | No |
| Firebase Authentication | Student identity | Not started | Firebase project and client config | Anonymous/local demo identity only during development | No |
| Flutter local notifications / FCM | Agent actions | Not started | Platform notification permissions; FCM config if remote | Record `NOTIFICATION_FAILED` and surface status | No |
| Cloud Scheduler / Pub/Sub | Background evaluations | Not started | Trigger, service auth, retry policy | Manual evaluation endpoint for development | No, use only if necessary |

## Environment variables

See `.env.example`. Never commit `.env`, service-account keys, API keys, or personal location data.
