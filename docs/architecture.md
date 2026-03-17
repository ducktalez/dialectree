# Dialectree – Architecture

## Overview
```
Client (React)  ──►  FastAPI  ──►  SQLAlchemy  ──►  SQLite (in-memory)
                      /api                            (StaticPool)
```

## Backend (`backend/app/`)
- **main.py** – FastAPI app, CORS, router registration, lifespan (auto-seed).
- **database.py** – engine, session factory, `get_db` dependency. In-memory SQLite by default, override via `DATABASE_URL`.
- **models.py** – all SQLAlchemy models and enums (single file).
- **schemas.py** – all Pydantic request/response schemas (single file).
- **seed.py** – example data ("Sollte Rauchen verboten werden?"), runnable via `python -m app.seed`.
- **routers/** – one file per resource: `users`, `topics`, `arguments`, `votes`, `tags`, `comments`, `evidence`, `labels`.

## Frontend (`frontend/src/`)
- **App.tsx** – topic list, tree view selection.
- **components/ArgumentTree.tsx** – React Flow visualisation of the nested tree.
- **api.ts** – fetch wrappers for `/api` endpoints.
- Vite proxies `/api` → `http://localhost:8000`.

## Data flow
1. Server starts → `lifespan` creates tables and seeds if empty.
2. Client fetches `GET /api/topics/{id}/tree` → nested JSON with vote scores.
3. Write operations pass `user_id` as query parameter (no auth yet).

## Key design decisions
- **Single-file models/schemas**: small project, avoids circular imports.
- **In-memory SQLite + StaticPool**: zero-friction dev, no files to manage, auto-resets.
- **Tests use a separate engine**: own `StaticPool` in-memory DB, `TESTING=1` env var skips auto-seed.

