# Decision engine

The current decision engine calculates `leave_at` and `preparation_at` using ordinary datetime arithmetic, then chooses a bounded decision based on travel availability, timing, and movement. It does not call an LLM.

See [AGENT_BEHAVIOR.md](AGENT_BEHAVIOR.md) and [API_CONTRACT.md](API_CONTRACT.md).

