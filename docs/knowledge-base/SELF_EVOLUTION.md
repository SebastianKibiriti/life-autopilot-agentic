# Bounded self-evolution

Life Autopilot improves through an offline propose-and-promote loop. It stores
versioned policies, evaluates representative scenarios, proposes a candidate,
and promotes it only after deterministic safety and score gates pass.

Runtime requests never rewrite the active policy. Private user memory remains
separate from global policy evolution. Stored records contain structured
inputs, outputs, tool/event summaries, scores, and failure reasons—not private
chain-of-thought.

Run the local API proof with:

```bash
./scripts/run_self_evolution_demo.sh
```
