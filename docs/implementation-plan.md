# Dialectree – Implementation Plan

> Companion docs:
> [`discussion-flow.md`](discussion-flow.md) (guiding example) ·
> [`taxonomy.md`](taxonomy.md) (argument types, tags, fallacies) ·
> [`visualization-strategy.md`](visualization-strategy.md) (visualization model) ·
> [`architecture.md`](architecture.md) (technical reference)

This document is a **concise list of ideas and future work**. Details are
written up only when implementation starts (in the relevant doc or PR).

Structure (top = now, bottom = later):
1. Next Up – the immediate next tasks
2. Phase Z – open zigzag stages (Z.4–Z.6)
3. Phase 2 – larger feature clusters
4. Phase 1 / 3 – security / infra / extended tests (pre-go-live)
5. Design principles
6. Open technology decisions
7. Design discussions
8. Changelog

---

## Next Up

1. **Z.5 — Meta Categorisation** (see Phase Z below). Next zigzag step now
   that Z.4 + Z.4b have shipped.
2. **Per-user vote tracking on sources** — blocked by auth (Phase 1).
3. **Multi-node pattern auto-detection** — needs the KI stack.
4. **Twitter/X import** — n8n sketch exists; better ingestion approach still open.

---

## Phase Z – Open Zigzag Stages

> Stages 0–3 + Z.4 + Z.4b done (see Changelog). Conventions: no
> `is_thread_primary`, no edge commenting (for now), no hard deletes.

### Z.4 — Categorisation (done — see Changelog)

### Z.4b — Inadmissible / off-topic edge marker (done — see Changelog)

### Z.5 — Meta Categorisation
Grouping + meta roles.
- Render `ArgumentGroup` as a clustered card
- Meta classification (thesis / source / premise / example)
- Spin a sub-discussion out of an `ArgumentGroup`
- Mark terminal moral premises (leaves of the goal tree)

### Z.6 — Discussion Network (planned)
Embed a concrete discussion into a topic-spanning argument network.
**Needs its own spec before implementation** (new models `AbstractArgument`,
`ConcreteToAbstractLink`, `DiscussionVersion`; cross-topic edge semantics;
version selection steelman/neutral/radical/…).

---

## Phase 2 – Advanced Features

### Sources collection — remaining
- Server-side per-user voting (needs auth)
- Embedding-based similarity (replacing the Jaccard stand-in)

### Twitter/X import
- n8n workflow, Twitter API v2, position detection, duplicate detection

### SRT import — speaker diarization
Today: SRT → flowing text → manual speaker assignment via LLM.
Later: `POST /api/topics/{id}/diarize` endpoint with LLM API.
Fallback if needed: audio diarization (`pyannote.audio` / `WhisperX`).

### AI & embeddings
- Embedding-based similarity for grouping
- Simulation: rational vs. derailing discussant
- GROK-style fact-check
- Gamification: reward quality, penalise spam
- KI extraction of argument anatomy from prose
- Automatic tag suggestions

### Multi-node patterns
- Auto-detection (Gish-gallop, creeping relativisation) via embeddings

### Definition forks
- Dispute / voting on competing definitions (mini-discussion per term)

### Conflict & sub-discussions
- Conflict detection on contradicting arguments
- Auto sub-topic from conflict
- Separate normative vs. positive
- Resolution workflow → validity score back into the parent argument

### User reputation
- Domain-specific reputation
- Track-record-weighted voting
- Effects from label confirmations / overturns

### Meme representation (see `meme-catalog.md`)
- Tagging → preview → KI suggestion → auto-generation → shareability

---

## Phase 1 – Pre-go-live: Security & Infrastructure

### Security & auth
- Password hashing, JWT, login/register, email verify, rate limiting,
  input sanitization, CORS whitelist

### Database & infra
- Alembic, PostgreSQL, caching (Redis), monitoring/logging

### Frontend (if the static HTML view is replaced)
- Design system (Tailwind/Radix), component library,
  form validation, error UI, responsiveness/a11y,
  routing (React Router), state management (Zustand/React Query)

---

## Phase 3 – Extended Test Coverage (pre-go-live)

- **Security:** auth/authz on write endpoints, input sanitization, rate-limit, CORS
- **Data integrity:** cascade deletes, race conditions on votes/tags,
  performance with 1000+ nodes, soft-delete transitions
- **Business logic:** visibility rules, tag-origin hierarchy,
  moral-foundation soft-assignment (sum=1), uncertainty propagation,
  meta-discussion → reputation, scope-violation → relocation,
  ArgumentGroup merge/unmerge, MECE branching
- **Frontend:** deep trees, position slider → enum, tag/vote/dispute flow

---

## Design Principles

Architectural decisions that should inform every implementation:

- **Complex behind, simple in front** – the data model may be rich, the UI
  stays minimal. Tags are the primary input surface.
- **Nothing is deleted** – hidden content gets an `IrrelevanceType`
  (`taxonomy.md` §13); it can seed a new discussion.
- **Three tagging origins** – user (votable) / moderator (authoritative) /
  KI (suggestive). Different authority, see `taxonomy.md` §12.5.
- **Continuous position slider** – stepless input, stored as float + discrete enum.
- **Surface contradicting sources** – do not average them away; open a
  sub-discussion instead.
- **Goal hierarchy tracking** – separate terminal vs. intermediate goals
  explicitly (`taxonomy.md` §19.3).
- **Tag disputability** – every assessment can become a meta-discussion.
- **Debug-first** – verify a new model field via Swagger + tests before
  pulling it into the UI.

---

## Open Technology Decisions

Must be made before go-live:

| Area | Default now | Final candidate | Trade-off |
|---|---|---|---|
| Database | In-memory SQLite | PostgreSQL | Full-text, concurrent writes, JSONB |
| Search | – | PG `tsvector` / Meilisearch | Tag similarity, dedup, argument search |
| Auth | `user_id` query param | JWT + OAuth2 | Multi-user deployment |
| Real-time | Polling | WebSockets / SSE | Multiple concurrent users |
| KI / embeddings | – | OpenAI / sentence-transformers | Tag suggestions, real dedup, anatomy |
| Task queue | – | Celery+Redis / ARQ | Async KI, n8n webhooks |
| Frontend state | `useState` | Zustand / React Query | Does not scale past ~4 components |
| CSS | Inline | Tailwind / Radix | Maintainability |
| Migrations | – (in-memory recreate) | Alembic | Data must survive restarts |
| Deployment | `uvicorn` local | Docker Compose | Shared instance |
| SRT parsing | `srt` (3.5.x) | locked in | – |

---

## Design Discussions

Open conceptual questions not yet ready as tasks.

### Edge semantics & edge attacks
Prototype in `zickzack.html`, no backend model yet.

- **Edge types** (semantic annotation, *how* an argument responds):
  `community_note`, `consequences`, `weakening`, `reframe`, `concession`.
  Candidates: `steelmanning`, `question`, `analogy`, `scope_shift`.
- **Edge attacks** = cards that attack the *connection* between two
  arguments rather than their content (undercutting defeater).
  Example: R2 attacks the inference R1→L1 because the underlying definition
  of racism is disputed.
- Open questions: dedicated `EdgeAttack` model vs. `ArgumentNode` with
  `target_type='EDGE'`? How to reference the target edge
  (`parent_id`+`target_parent_id` vs. dedicated `Edge` model)?
  Should an edge attack auto-open a sub-discussion?

**Rejected:** edge-challenge popup with 7 buttons — every category is
already covered by `FALLACY` / `SCOPE_VIOLATION` / `KILLER_ARGUMENT` /
follow-up.

### Drag & drop
Enabled, not persisted (`DRAG_ENABLED=true`). The zigzag view has a shared
geometry core (anchor resolution + SVG updates); stages only decide
*which* connection types are drawn.

### UI collaboration
- Blueprint step names (B₁, A₁, …) + view mode as a shared vocabulary
- Edit-and-point in `zickzack.html`, ASCII mock-ups, annotated screenshots,
  HTML as a whiteboard

---

## Changelog (completed work)

Newest first.

### 2026-Q2 — Z.4b: inadmissible-edge marker
Annotates a single parent→child *connection* as inadmissible without
attacking the child argument itself (e.g. someone hangs a true-but-unrelated
statement under an off-topic parent).

- **New enum `EdgeAdmissibility`** with values `ADMISSIBLE` (default),
  `OFF_TOPIC`, `SCOPE_VIOLATION`, `NON_SEQUITUR` (taxonomy §27). Stored on
  `ArgumentNode.edge_admissibility` (non-null, server default `ADMISSIBLE`).
  Migrates to a dedicated `Edge` model later — for now the edge has no row
  of its own.
- **Schemas extended**: `ArgumentNodeCreate`, `ArgumentNodeUpdate`,
  `ArgumentNodeOut`, `ArgumentTreeNode`, `ZigzagStepOut` all carry the new
  field.
- **New endpoint** `PATCH /api/arguments/{id}/edge-admissibility` with body
  `{admissibility: str|null}`. `null` resets to `ADMISSIBLE` so the UI can
  offer a one-click "Markierung entfernen". Root nodes (no parent) → 400.
  The generic `PATCH /api/arguments/{id}` accepts it too.
- **Frontend (Stage 4)**: new `⊘` action button on non-root cards opens an
  inline form with the three reason options + a clear button. Marked edges
  render as dashed red lines (`stroke=#f85149`, `dasharray="5,4"`) and the
  child card gets a ⊘-badge in its bottom-left corner. Line styling applies
  to all three connection drawers (main parent line, Stage-2 split-to-split,
  Stage-3 logical reference) so the marker is consistently visible.
- **9 new tests** in `TestEdgeAdmissibility` (227 total).

### 2026-Q2 — Card chrome polish (drag handle, short-ID plate, collapse arrow, floating reply, outside-click dismiss)
A batch of zigzag-card UX tweaks driven by user feedback:
- **Bigger dedicated drag handle (`.card-drag-handle`, 28×28)** in the
  top-left corner. The card body is now `user-select: text` so quotes can be
  copied; drag is bound to the handle only.
- **Floating short-ID plate (`#1`, `#2`, …)** absolutely positioned over the
  top-right corner. IDs are a flat per-discussion counter (no `L`/`R`
  prefixes), making "siehe #2" the shortest possible reference.
- **Collapse line with chevron** replaces the old `▸/▾` toggle: a thin
  divider under the title with a centered down-arrow when collapsed
  (suggesting "click to drop content"). The collapsed title doubles as the
  click target to re-expand.
- **Floating "+" reply button** (`.btn-reply-float`) hangs slightly below
  the card edge — implies "a new connection grows out here".
- **Outside-click / Escape dismiss** for inline forms (reply / comment /
  label). Forms with already-typed text are preserved; explicit Cancel /
  Submit still always close.
- **Stage 4 split-origin handling**: L-originals now stay hidden in Stage 4
  exactly like in Stage 3; the `🔄 Original` / `← Splits` toggle continues
  to work in both stages (`currentStage >= 3` filter).

### 2026-Q2 — Stage descriptions, short IDs, clean titles
Three coupled UX changes in `zickzack.html` + `seed.py`:
- **Enumerated stage descriptions**: each stage's banner now lists exactly
  the new pieces of information that appear in that stage (Stage 1 adds
  the per-side short IDs, Stage 2 the splits, Stage 3 the steelman titles
  and definition forks, Stage 4 the ratings/labels/comments/late additions
  + the planned inadmissible-edge marker).
- **Auto-derived short IDs**: every card now carries a small monospace
  reference plate (`#L1`, `#R2`, `#L1.1`, `#N1`, …) computed in the frontend
  from `position` + chronological order + `split_from_id`. IDs are *not*
  stored in the DB so the seed stays clean.
- **Titles cleaned**: the seed used to bake `R1` / `L2` / `(2.1) ↩ 2.1:`
  prefixes into the `title` column. Those are gone — titles are now plain
  short summaries ("Quoten sind rassistisch gegenüber Weißen", "Doch,
  Rassismus gegen Weiße gibt es", …). The notation lives only as the
  derived plate.

### 2026-Q2 — Seed: blueprint topic removed, transcript cleaned up
The two seed topics ("Quoten-Diskussion" and "Blueprint Quotenrassismus")
overlapped heavily. The blueprint topic and its `quoten_blueprint.md` file
were deleted; only one feature that wasn't otherwise represented in the
remaining topic was ported across: a **NEUTRAL `CONCESSION` consensus node**
("Begriff Rassismus muss erst geklärt werden") and one **Evidence record**
attached to L2 (McKinsey diversity study). `quoten_diskussion.md` was
rewritten as a readable speaker-prefixed dialogue (Anna/Ben) without the
former "Notation" header block. The line "Bist du bescheuert?" was added
into the transcript and flagged via a comment on L4 as an ad-hominem aside —
deliberately *not* a standalone `ArgumentNode`, so it appears in the raw
Stage-0 record but never in the structured argument tree.

### 2026-Q2 — Zigzag UI polish (Stage 4 legend, dangling siblings, copy-text)
Three small UX fixes on `zickzack.html`:
- **Stage-4 legend**: the legend/settings panel is now visible in Stages 2–4
  (previously only 2–3) and carries a single consistent heading
  ("Legende & Einstellungen") across all stages. Stage-4 omits the
  "Verbindungen" and "Abwählbar" sections (no chrono/origin overlays there)
  but keeps Bereiche and Muster.
- **Dangling Stage-4 arguments**: child arguments grouped as "siblings" under
  the same `parent_id` were stacked visually but had no SVG line. They now
  receive a regular parent→child line; live-updated during drag.
- **Copy-paste**: card bodies are no longer `user-select: none`. Drag is bound
  to a dedicated `.card-drag-handle` (⠿ grip in the top-right corner), so
  users can select and copy text without triggering a drag. Polygon/pattern
  selection modes still react to a click anywhere on the card.

### 2026-Q2 — Z.4 Zigzag Categorisation
Stage 4 ("teacher's view") shipped end-to-end.

- **Backend** (`routers/topics.py`, `schemas.py`): `GET /api/topics/{id}/zigzag?stage=4`
  bulk-loads labels and comment counts per topic (single query each, not N+1)
  and embeds them in each `ZigzagStepOut` as `labels: [{id, label_type,
  justification, confirmed}]` and `comment_count: int`. `POST /api/arguments/`
  now respects `stage_added` on the payload so late additions can be recorded
  as Stage-4 nodes.
- **Frontend** (`zickzack.html`): the Stage-4 button is no longer deferred;
  the canvas renders. Each card shows label chips (FALLACY-family in
  warning-red, rest neutral), a comment-count badge on the comment button,
  a dedicated label button with inline form (label-type select + mandatory
  justification), and a vote-score next to the up/down arrows. Replies
  created in Stage 4 are persisted with `stage_added=4` and marked on the
  card with a dashed "Nachtrag" badge. Clicking an existing label chip
  prompts to delete it (no edit flow yet — delete + recreate covers the
  rare case).
- **Tests** (`tests/test_topics.py`): +2 tests covering the new bulk fields
  (label list + comment count) and `stage_added=4` filter behaviour.
- **Deferred**: per-label voting / confirmation flow, label editing,
  edge commenting.

### 2026-Q2 — Implementation plan: restructured & condensed
Plan rewritten end-to-end: Next-Up at the top (including Z.4 as the next
zigzag step), Phase Z / 2 / 1 / 3 as concise lists, technology decisions
and design discussions at the bottom. Verbose Phase-Z detail spec removed
(redundant with `architecture.md`). English-only, no emojis.

### 2026-Q2 — Seed data: minimal Stage-0 transcripts
`quoten_blueprint.yaml` replaced by a minimal `quoten_blueprint.md`
(speaker + raw text only, analogous to `quoten_diskussion.md`). Structured
nodes are still created in seed code; YAML stage descriptions were moved
to `implementation-plan.md`. 216/216 tests green.

### 2026-Q2 — Definition forks: inline edit in the Stage-3 panel
Pencil button per fork row opens an inline editor (term + variant +
description), PATCH via the existing endpoint. Frontend-only change.

### 2026-Q2 — Seed cleanup: "Migration" demo topic removed
Third seed topic dropped (it only demonstrated Phase-0 features); topics
1+2 (Quoten / Blueprint) remain. Tests unchanged.

### 2026-Q2 — Definition forks UI (Stage 3) + backend polish
- `POST` validates `argument_node_id` → 404
- `PATCH /api/definition-forks/{id}` added
- `GET /api/definition-forks/?topic_id=…` for topic-wide listing
- Stage-3 cards: badge with inline panel (add/delete). +5 tests.

### 2026-Q2 — Sources JSON → SQLAlchemy
`Source`, `SourceTag` (n:m), `SourceComment`, `SourceUsage` as SQL models;
`SourceUsage.argument_id` with `ON DELETE SET NULL`. Router surface
unchanged. `seed.py` imports `sources.json` idempotently. Deferred:
per-user voting, embedding similarity.

### 2026-Q2 — Multi-node patterns (manual UI)
"Mark pattern" mode in the zigzag view, persistent server patterns
(`POST/GET/DELETE /api/patterns/`). Convex-hull overlay, colour by
`pattern_type`. Auto-detection remains open.

### 2026-Q2 — Z.2c GUI editing for splits (Stage 2)
- `POST /api/arguments/{id}/split` (N children with `split_from_id`)
- `PATCH /api/arguments/{id}/connect` (parent_id (re)wiring)
- Stage-2 inline forms `Aufteilen` + `Connect`. +13 tests.

### 2026-Q2 — Retired views: Baum, Waage, Konflikt
Three standalone pages removed (`/baum`, `/entscheidung`, `/konflikt`,
`/dialog`) — functionality now covered by Zigzag. 192/192 tests green.

### 2026-Q2 — Z.2b split toggle (Stage 3)
Toggle buttons reveal original / restore splits; preserves the rule
"never show original + splits simultaneously".

### 2026-Q2 — Sources collection MVP (`/quellen`)
pr0gramm-style 8×128px grid with inline detail. CRUD, voting, inline
media player (YouTube/Vimeo + upload), Jaccard similarity, tag
conventions, keyboard navigation. 47 tests.

### 2026-Q2 — SRT import pipeline (YouTube → Stage 0)
`srt_parser.py` + `POST /api/topics/{id}/import-srt`. 14 tests.

### 2026-Q1 — URL routing & unified header
Hash-based deep linking in `zickzack.html` (`#topic=N&stage=M`); unified
header across all static pages.

### 2026-Q1 — Phase Z stages 0–3
- **Z.0 Transcript:** `Topic.transcript_yaml`, `GET/PUT /api/topics/{id}/transcript`,
  minimal `.md` transcripts under `backend/app/data/`
- **Z.1 Basis:** `ArgumentNode.stage_added`, `GET /api/topics/{id}/zigzag?stage=N`
- **Z.2 Split:** `ArgumentNode.split_from_id`, 4 connection types,
  legend panel with toggleable chronology line
- **Z.2a:** Stage-3 distinct connection types (chronological vs. logical)
- **Z.3 Verfeinerung:** splits replace originals, bodies become visible,
  collapsible cards, same-side column stacking
- **Z.3a Polygon overlay:** convex-hull marking for argument branches
  (auto + custom)
- **Z.UI:** Stage tabs 0–6 with placeholders for 4–6

### 2025-Q4 — Phase 0 core (complete)

| Step | Feature |
|---|---|
| 0.1 | Argument anatomy (`claim` / `reason` / `example` / `implication`) |
| 0.2 | Visibility & soft-delete (`IrrelevanceType`, 6 values) |
| 0.3 | Evidence types (15 tiers, `default_quality`) |
| 0.4 | Label types (12+, `confirmed` / `confirmed_at`, visibility effects) |
| 0.5 | Tag origin & meta categories (`TagCategory`, `TagOrigin`) |
| 0.6 | `StatementType` (POSITIVE / NORMATIVE / MIXED / UNCLASSIFIED) |
| 0.7 | Continuous position score (`position_score` float 0–1) |
| 0.8 | (removed 2026-Q2) Migration seed topic |
| 0.9 | Frontend rich tree view (anatomy, badges, tag chips, severity) |
| 0.10 | ArgumentGroup merge / unmerge |

                                             le