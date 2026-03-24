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
- New functionality requires tests. Tests must pass before a change is complete.
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

## Documentation Is a First-Class Artifact
This repository consists of **two equally important parts**:
1. **Code** – the running application (backend, frontend, tests, seed data).
2. **Instructions & reasoning** – the architectural decisions, design rationale, taxonomies, and plans that accompany and explain the code.

Both parts must stay in sync. Code without updated documentation is **incomplete work**. A change is not finished until every affected doc file has been updated.

### Where documentation lives
Documentation exists at **two levels** that complement each other:

- **`docs/`** — the bird's-eye view. `architecture.md` is the comprehensive technical reference (data model, endpoints, design decisions). The other `docs/*.md` files capture design reasoning, plans, and taxonomies — the thinking behind the code that emerges from discussions and must not be lost. `implementation-plan.md` tracks deferred and planned work so the code doesn't fill up with TODOs.
- **Code comments** — the detail view. Rationale for specific implementations, edge cases, non-obvious decisions. In Python (docstrings, `#`) these are naturally visible. In HTML, comments can get buried — use marked blocks (`<!-- DESIGN: … -->`) so they don't get lost.

Neither level replaces the other. `docs/` describes the big picture; code comments explain the specifics.

### The change workflow: think → document → implement → verify

Every change follows this cycle:

1. **Think** — Understand the requirement. Break it into concepts.
2. **Document first** — Update or create the relevant doc file (`architecture.md`, `zigzag-plan.md`, etc.) with the planned approach *before* writing code. This forces clarity.
3. **Implement** — Write the code, adding detail-level comments where the *why* isn't obvious.
4. **Verify docs** — After implementation, check both directions:
   - Does the code match the docs?
   - Did implementation reveal something the docs didn't anticipate?
   - Update both if needed — in the same change, not as a follow-up.

When modifying existing code, reverse the check: *"Does this change affect the architecture or any documented decision?"* If yes, update docs in the same change.

## Maintaining These Docs

### `docs/architecture.md` — the architectural overview
The **comprehensive overview** of how the system is built. It must always reflect the current state. Update it when:
- A **model or enum** is added, removed, or changed → update the Data Model section (entities table, ER diagram, ArgumentNode detail, enums table).
- A **new endpoint or router** is added → update the Backend section.
- A **new static page or frontend component** is added → update the relevant UI section.
- A **design decision** is made (e.g. "no edge comments for now") → add it to Key Design Decisions.
- The **refinement stages** (Zigzag 0–5) change → update the stage table.

**Rule of thumb**: if you touch `models.py`, `schemas.py`, `main.py`, or add a router, check whether `architecture.md` needs an update.

### All doc files at a glance
| File | Purpose | Update trigger |
|------|---------|---------------|
| `docs/architecture.md` | Technical overview: data model, endpoints, UI, design decisions, refinement stages | Model/enum/router/page/decision change |
| `docs/zigzag-plan.md` | Zigzag refinement model: stage definitions, conceptual rationale, blueprint data | Changes to the stage model, visualization approach, or blueprint data |
| `docs/discussion-flow.md` | How a full discussion should flow — use-case thinking that guides implementation priority | New use-case understanding, changed discussion workflow |
| `docs/visualization-strategy.md` | Three-function model (Raw Data → Evaluation → Overview) and visualization concepts | Changed visualization approach or new view concept |
| `docs/taxonomy.md` | **Canonical reference** for all argument types, fallacies, evidence tiers, tag categories | **Before** adding a new enum, label type, or tag category — it must have an entry here first |
| `docs/implementation-plan.md` | Tracks deferred and planned work, open technology decisions | New TODO, deferred feature, or completed milestone |
| `docs/meme-catalog.md` | Maps meme templates to argumentative concepts | New meme mapping (must reference corresponding taxonomy section) |
| `.github/copilot-instructions.md` | Global coding & process rules (this file) | New conventions, pitfalls, or process changes |
| `.github/instructions/*.instructions.md` | Layer-specific rules (backend, frontend) | Layer-specific convention changes |

