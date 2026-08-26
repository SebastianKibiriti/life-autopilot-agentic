# Memory and learning

Persistent companion memory is implemented for the focused MVP. Firestore stores
user-scoped profiles under `students/{id}/memory` and structured suggestions
under `students/{id}/suggestions`. Profiles retain interests, preferred
activities, and explicit feedback; preparation profiles retain explainable
timing observations. Avoid sophisticated model training.

See [DOMAIN_MODEL.md](DOMAIN_MODEL.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
