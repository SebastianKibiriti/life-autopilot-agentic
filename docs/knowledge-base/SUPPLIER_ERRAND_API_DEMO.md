# Supplier Errand API Demo

This is a separate scenario from the lecture demo. It shows that Life
Autopilot can monitor a planned errand: Sipho schedules a supplier pickup,
the agent observes his location, calculates travel context, advises preparation,
escalates when he misses the departure window, and re-evaluates when movement
begins.

With the backend running and Gmail configured, run:

```bash
cd /Users/apple/Documents/Codex/2026-08-18/lo
./scripts/run_supplier_errand_demo.sh
```

The three responses should show `PREPARE`, then `REPLAN`, then `LEAVE` (or a
safe escalation if route context is unavailable). Gmail messages and the event
timeline provide real-world evidence of each intervention.
