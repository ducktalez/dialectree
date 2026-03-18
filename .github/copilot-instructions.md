# Dialectree – Copilot Instructions

## What is this?
Dialectree structures discussions as logical argument trees. A debatable question (Topic) is the root; users attach ArgumentNode children (PRO / CONTRA / NEUTRAL) forming chains of reasoning down to moral premises.

## Development Phase Policy
The project is in early development. Only implement what is **technically necessary right now**.
- **Security, caching, styling, monitoring**: deferred. Mark placeholders with `# TODO: post-dev`.
- **No speculative features or database columns.** If it's not needed for the current task, don't build it.
- Priority: **Backend API → Tests → Seed data → Frontend (minimal).**
- See `.github/instructions/backend.instructions.md` and `frontend.instructions.md` for layer-specific rules.

## Coding Conventions
- All code, comments, docstrings, and documentation in **English**.
- Every new endpoint **must** have tests in `backend/tests/` (`test_{resource}.py`, one `Test{Resource}` class).
- Shared test fixtures live in `conftest.py`.
- New models → `models.py`, schemas → `schemas.py`, routes → `routers/{resource}.py` (register in `main.py`).
- Keep it simple – working and lean over complex and perfect.

## API Conventions
- All endpoints prefixed with `/api`.
- Auth is not implemented. Write endpoints take `user_id` as a **query parameter** (`# TODO: security`).
- Enum values are **uppercase strings** in JSON: `"PRO"`, `"CONTRA"`, `"NEUTRAL"`, `"STUDY"`, `"FALLACY"`, etc.
- `GET /api/topics/{id}/tree` returns a **nested** JSON structure (children embedded recursively).

## Known Pitfalls
- **Tests must run from `backend/`**: `cd backend && python -m pytest tests/ -v`.
- **In-memory SQLite** is the default (`sqlite://` with `StaticPool`). No DB files to manage. Data resets on every server restart. Set `DATABASE_URL` env var for persistence.
- The dev server **auto-seeds** on startup (via `lifespan`). Tests skip this via `TESTING=1` env var (set in `conftest.py`).
- After `db.commit()` + `db.close()`, do **not** access ORM attributes on detached objects → `DetachedInstanceError`.
- No Alembic. Schema changes just require a server restart (in-memory DB recreates automatically).

## Maintaining These Instructions
When a change introduces new conventions, pitfalls, or architectural decisions, **update the relevant instruction file** (this file, or `.github/instructions/*.instructions.md`). Keep them accurate and lean.

## Working process: Maintaining These Docs 
- Update architectural changes in  `docs/architecture.md`.
- Track deferred work in `docs/implementation-plan.md`.
- **`docs/taxonomy.md`** is the canonical reference for all argument types, fallacies, evidence tiers, tag categories, and categorisation dimensions. When adding a new enum, label type, or tag category, it **must** have an entry in taxonomy.md first.
