# Sipho Real API Demo

This is the hackathon-facing test for the supported consumer story. Sipho has
planned an errand to collect imported flour from a supplier. It uses
real HTTP calls against the running backend, the real decision engine, the
configured Vertex/Gemini client, and Gmail when `GMAIL_NOTIFICATION_TO` is set.
The route uses the application's known-destination fallback unless production
Routes/Places credentials are configured.

Start the backend in one terminal with the Calendar and Gmail variables from
the setup instructions, including a real recipient address. Then run:

```bash
cd /Users/apple/Documents/Codex/2026-08-18/lo
./scripts/run_sipho_api_demo.sh
```

The script creates a fictional supplier pickup 40 minutes ahead, posts Sipho's
simulated bakery location, and evaluates the errand at three points in time:

1. preparation window: the agent advises Sipho to get ready;
2. missed departure: the agent sends an urgent re-plan message;
3. movement detected: the agent re-evaluates and sends a leave-now message.

Each stage uses the API and the event timeline proves the action was recorded.
The response exposes the reason, route provider, and whether Gmail delivery
succeeded. The timestamps are generated at runtime, so the test remains usable.

For a deployed test, set the URL without changing the script:

```bash
LIFE_AUTOPILOT_URL=https://life-autopilot-agentic-725797619054.us-central1.run.app \
  ./scripts/run_sipho_api_demo.sh
```

Cloud Run cannot use the local OAuth token files automatically. Run the local
version for the real Gmail end-to-end proof unless Gmail credentials have been
configured in Secret Manager or another production-safe deployment mechanism.
