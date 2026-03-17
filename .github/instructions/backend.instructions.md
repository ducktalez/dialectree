---
applyTo: "backend/**"
---
# Backend Instructions

## Deferred until go-live
- **Security & auth**: passwords are plaintext, `user_id` is a query parameter. No tokens, sessions, hashing, or input sanitization.
- **Migrations**: no Alembic. Model changes are applied directly (in-memory DB recreates on restart).
- **Data collection & analytics**: no tracking, logging pipelines, or data mining.
