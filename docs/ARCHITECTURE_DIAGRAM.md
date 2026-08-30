# Life Autopilot Agentic architecture

```mermaid
flowchart TD
    U[Student / Flutter shell] -->|HTTPS| R[FastAPI on Cloud Run]
    R --> C[Companion orchestration]
    R --> S[Schedule and location services]
    R --> E[Evaluation and evolution APIs]
    R --> X[Calendar and Gmail adapters]
    R --> K[Curated campus knowledge resolver]
    C --> V[Vertex AI: Gemini 3.5 Flash]
    C --> M[(Firestore: user-scoped memory)]
    E --> P[(Firestore: policies, cases, runs, proposals)]
    R --> A[(Firestore: structured audit events)]
    X --> G[Google Calendar]
    X --> N[Gmail]
    K --> D[Campus places, aliases, confidence]
    T[Offline propose / evaluate / promote workflow] --> E
    T -. explicit promotion only .-> P
    T -. no runtime self-rewriting .-> R
```

User memory and global policy evolution are separate Firestore areas. Gemini
provides contextual synthesis; deterministic code controls timing, schemas,
safety gates, and side effects. Routes/Places use APIs when configured and a
labelled fallback otherwise.
