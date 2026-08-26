# Nutrition Collaborative Partner Demo

This separate real-API scenario demonstrates persistent personalization. A
Nutrition and Dietetics student has a timetable, a fitness pattern, and saved
feedback showing a preference for outdoor cycling over generic gym suggestions.

Start the backend with `USE_FIRESTORE=true` for production persistence and with
the existing Calendar OAuth variables configured, then run:

```bash
cd /Users/apple/Documents/Codex/2026-08-18/lo
./scripts/run_nutrition_companion_demo.sh
```

The flow saves preferences, resolves `N204`, imports two schedule items,
generates and stores a multi-option fitness suggestion, answers a follow-up
from stored memory, and saves the selected recommendation to Google Calendar.
`jq` is required for extracting the suggestion ID.
