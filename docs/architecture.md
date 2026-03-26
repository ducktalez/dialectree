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
- **seed.py** – example data: two topics ("Sind Quotenregelungen rassistisch?" + "🔧 Blueprint: Quotenrassismus-Diskussion"), runnable via `python -m app.seed`. Both topics demonstrate full zigzag features: branching, edge attacks, sibling alternatives, conflict zones.
- **routers/** – one file per resource: `users`, `topics`, `arguments`, `votes`, `tags`, `comments`, `evidence`, `labels`, `argument_groups` (incl. merge/unmerge), `definition_forks`, `multi_node_patterns`.

## Static UI (`backend/app/static/`)
- **zickzack.html** – API-backed zig-zag view with chronological layout, interactive input (add arguments, vote, comment), served at `/` and `/zickzack`. Fan/Fächer mode is implemented but commented out (`# TODO: post-dev`).
- **dialog.html** – zig-zag dialectical dialogue visualisation (step 1 of three-step analysis), served at `/dialog`. Contains Quotenrassismus discussion example; Rauchen/Klima dialogues are commented out.
- **index.html** – layered argument tree visualisation with SVG connectors, served at `/baum`.
- **entscheidung.html** – weighted balance/scale visualisation, served at `/entscheidung`.
- **konflikt.html** – conflict zone analysis, served at `/konflikt`.
- **rauchen.html** – archived snapshot (route removed).

## Frontend (`frontend/src/`)
- **App.tsx** – topic list, tree view selection, dark theme.
- **components/ArgumentTree.tsx** – React Flow tree visualisation with all Phase 0.1–0.8 features:
  - Gradient border colour from `position_score` (red → grey → green)
  - Ⓕ/Ⓥ/Ⓜ badges for `statement_type`
  - Argument anatomy display (💬 claim, 📐 reason, 📋 example, ➡ implication)
  - Tags grouped by `category` with origin icon (👤/🛡️/🤖)
  - Label badges (⚠ FALLACY, SPAM, etc.)
  - Evidence & comment counts
  - Hidden nodes: greyed-out, half-opacity, with "Show hidden" toggle
  - `opens_conflict` badges for sub-discussion markers
- **api.ts** – fetch wrappers for `/api` endpoints.
- **types.ts** – full TypeScript types matching backend schemas (anatomy, statement_type, position_score, visibility, tags, labels).
- Vite proxies `/api` → `http://localhost:8000`.

## Data flow
1. Server starts → `lifespan` creates tables and seeds if empty.
2. Client fetches `GET /api/topics/{id}/zigzag` → flat chronological list with zigzag fields (`conflict_zone`, `edge_type`, `is_edge_attack`, `opens_conflict`, `sibling_ids`).
3. Client fetches `GET /api/topics/{id}/tree` → nested JSON with vote scores (used by commented-out tree view).
4. Write operations pass `user_id` as query parameter (no auth yet).

## Data Model (`models.py`)

All models live in a single `models.py` file (SQLAlchemy ORM, in-memory SQLite).

### Entity-Relationship Overview

```
User ─────────┬──< Topic
              │      ├── transcript_yaml          (Stage 0 raw data)
              │      ├──< ArgumentNode             (core entity)
              │      ├──< ArgumentGroup
              │      └──< MultiNodePattern
              │
              ├──< ArgumentNode
              │      ├── parent_id ──► ArgumentNode (self-ref: tree structure)
              │      ├── split_from_id ──► ArgumentNode (self-ref: Stage-2 split origin)
              │      ├── argument_group_id ──► ArgumentGroup
              │      ├──< Vote
              │      ├──< Comment
              │      ├──< Evidence
              │      ├──< NodeLabel
              │      ├──< DefinitionFork
              │      ├──<> Tag               (via ArgumentNodeTag, with origin)
              │      └──<> MultiNodePattern   (via multi_node_pattern_members)
              │
              ├──< Vote
              ├──< Comment
              └──< Evidence
```

### Entities

| Entity | Table | Key columns | Purpose |
|--------|-------|-------------|---------|
| **User** | `users` | `username`, `email`, `password_hash` | Author of topics, arguments, votes, comments |
| **Topic** | `topics` | `title`, `description`, `transcript_yaml` | Root discussion. `transcript_yaml` holds Stage-0 raw YAML |
| **ArgumentNode** | `argument_nodes` | `title`, `position`, `parent_id`, `stage_added`, `split_from_id` | Central entity — each argument in the tree/zigzag |
| **ArgumentGroup** | `argument_groups` | `canonical_title`, `topic_id` | Groups related arguments under one canonical title (Stage 4) |
| **Vote** | `votes` | `user_id`, `argument_node_id`, `value` (+1/−1) | Up/down vote on arguments. Unique per user+node |
| **Tag** | `tags` | `name`, `category`, `moral_foundation` | Reusable labels with taxonomy category |
| **ArgumentNodeTag** | `argument_node_tags` | `argument_node_id`, `tag_id`, `origin` | Association model (not bare table) — tracks who applied the tag (USER/MODERATOR/AI) |
| **TagVote** | `tag_votes` | `user_id`, `tag_id`, `argument_node_id`, `value` | Vote on tag relevance. Unique per user+tag+node |
| **Comment** | `comments` | `argument_node_id`, `user_id`, `text` | Free-text comments on arguments |
| **Evidence** | `evidence` | `argument_node_id`, `evidence_type`, `url`, `quality_score` | Sources/proof attached to arguments |
| **NodeLabel** | `node_labels` | `argument_node_id`, `label_type`, `justification` | Quality labels (FALLACY, SPAM, …) with mandatory justification |
| **MultiNodePattern** | `multi_node_patterns` | `topic_id`, `pattern_type`, `name` | Cross-node patterns (e.g. Gish Gallop). M:N with ArgumentNode |
| **DefinitionFork** | `definition_forks` | `argument_node_id`, `term`, `definition_variant` | Tracks when a term has competing definitions |

### ArgumentNode Detail

The central model carries fields for multiple concerns:

| Field group | Columns | Used from Stage |
|-------------|---------|----------------|
| **Identity** | `id`, `topic_id`, `parent_id`, `created_by`, `created_at` | 1 |
| **Content** | `title`, `description` | 1 |
| **Position** | `position` (PRO/CONTRA/NEUTRAL), `position_score` (0.0–1.0) | 1 |
| **Anatomy** | `claim`, `reason`, `example`, `implication` | 3 (TODO) |
| **Classification** | `statement_type`, `visibility`, `hidden_reason` | 3 (TODO) |
| **Zigzag view** | `conflict_zone`, `edge_type`, `is_edge_attack`, `opens_conflict` | 1 |
| **Refinement** | `stage_added` (1=base, 2=split), `split_from_id` | 1–2 |
| **Grouping** | `argument_group_id` | 4 (TODO) |

### Enums

| Enum | Values | Used by |
|------|--------|---------|
| `Position` | PRO, CONTRA, NEUTRAL | ArgumentNode.position |
| `Visibility` | VISIBLE, VOTED_DOWN, MOD_HIDDEN, MOVED, MERGED, SUPERSEDED, PENDING_REVIEW | ArgumentNode.visibility |
| `StatementType` | POSITIVE, NORMATIVE, MIXED, UNCLASSIFIED | ArgumentNode.statement_type |
| `ConflictZone` | FACT, CAUSAL, VALUE | ArgumentNode.conflict_zone |
| `EdgeType` | COMMUNITY_NOTE, CONSEQUENCES, WEAKENING, REFRAME, CONCESSION | ArgumentNode.edge_type |
| `EvidenceType` | PROOF, META_ANALYSIS, STUDY, STATISTIC, LAW, EXPERT_OPINION, JOURNALISM, SURVEY, HISTORICAL, ANECDOTE, THOUGHT_EXPERIMENT, HEARSAY, UNFALSIFIABLE, FABRICATION | Evidence.evidence_type |
| `LabelType` | FALLACY, DOUBLE_STANDARD, CIRCULAR, MISSING_EVIDENCE, OFF_TOPIC, SPAM, ANECDOTE, DUPLICATE, CONTENTLESS, SCOPE_VIOLATION, MANIPULATION, INVALID | NodeLabel.label_type |
| `PatternType` | GISH_GALLOP, CREEPING_RELATIVIZATION, OTHER | MultiNodePattern.pattern_type |
| `TagCategory` | DOMAIN, MORAL_FOUNDATION, SOCIETAL_GOAL, EVIDENCE_QUALITY, FALLACY, RELEVANCE, COMPLETENESS, MANIPULATION, META_ARGUMENTATION, COMMUNITY, OTHER | Tag.category |
| `TagOrigin` | USER, MODERATOR, AI | ArgumentNodeTag.origin |
| `MoralFoundation` | CARE, FAIRNESS, LOYALTY, AUTHORITY, SANCTITY | Tag.moral_foundation |

## Key design decisions
- **Single-file models/schemas**: small project, avoids circular imports.
- **In-memory SQLite + StaticPool**: zero-friction dev, no files to manage, auto-resets.
- **Tests use a separate engine**: own `StaticPool` in-memory DB, `TESTING=1` env var skips auto-seed.
- **ArgumentNodeTag association model**: the Tag ↔ ArgumentNode link is a full ORM model (not a bare association table) to support `origin` tracking (USER / MODERATOR / AI). Tags also carry a `category` (TagCategory enum) for meta-grouping.
- **Explicit `foreign_keys` on self-referencing relationships**: `ArgumentNode` has two FKs to itself (`parent_id`, `split_from_id`). All self-referencing relationships must specify `foreign_keys=[…]` to avoid `AmbiguousForeignKeysError`.

## 6-Stufen-Verfeinerungsmodell (Zigzag)

Diskussionen durchlaufen sieben Analyse-Stufen (0–6). Dieselbe `ArgumentNode`-Struktur wird additiv reicher:

| Stufe | Neue Felder / Konzepte |
|-------|----------------------|
| 0 | `Topic.transcript_yaml` — roher YAML-Text der Diskussion |
| 1 | `ArgumentNode.stage_added=1` — ein Node pro Turn, **rohe Zuordnung** (nur Gesagtes, keine Analyse, transkript-artiger Stil) |
| 2 | **Split-Prozess** (Arbeitsschritt) — Originale + Splits gleichzeitig sichtbar. Originale bleiben im Rohformat und offen; Split-Karten zeigen zunächst nur ihren Titel. Unterhalb des Canvas beschreibt ein kleines Legenden-/Control-Panel die vier Verbindungsarten; der blaue Chronologiefluss kann dort ein-/ausgeblendet werden. Vier Verbindungsarten: Roh-Kette, Ursprungs-Argument, chronologischer Fluss, logische Split-Referenzen |
| 3 | **Verfeinerung** — Gesplittete Originale verschwinden, nur Splits bleiben. Hier werden die Inhalte/Beschreibungen der Split-Karten erstmals sichtbar; Karten starten eingeklappt und werden je Seite in einer gemeinsamen Spalte gestapelt. Das Legenden-/Control-Panel bleibt verfügbar und kann die blaue Chronologie ausblenden. Zwei Verbindungsarten: Chronologie (gestrichelt) + logische Referenz (durchgezogen) |
| 4 | ⚙️ TODO: post-dev — Bewertungen, argumentative Verfeinerungen |
| 5 | ⚙️ TODO: post-dev — Meta-Einordnung, Argumentgruppen, Grundannahmen |
| 6 | 🔭 Geplant — Diskussionsnetz, Cross-Topic-Links, AbstractArgument-Modell |

- **Kein `is_thread_primary`**: Der rote Faden ist implizit über die `parent_id`-Kette bestimmbar, wird nicht gespeichert.
- **Kein Edge-Kommentieren** (vorerst): Nur Argumente sind kommentierbar. Verbindungen später.
- **Stufe 1 = Rohdaten**: Kein analytischer Inhalt, farbloser Notepad-Stil. Nummerierung (R1, A₁ etc.) nur für Entwicklungsreferenz.
- **Stufe 2 = Split-Prozess**: Arbeitsschritt — zeigt beides gleichzeitig (Ausnahme). Originale bleiben offen im Rohstil; Split-Karten zeigen nur ihre Titel. Unterhalb des Canvas beschreibt ein kleines Legenden-/Control-Panel die vier Verbindungsarten; die blaue Chronologie ist dort schaltbar.
- **Stufe 3 = Verfeinerung**: Ergebnis — Originale verschwinden, nur Splits bleiben. Die Inhalte der Split-Karten werden hier erstmals sichtbar; Karten starten eingeklappt und stehen pro Seite untereinander in einer gemeinsamen Spalte. Das Legenden-/Control-Panel bleibt aktiv.
- Detail: `docs/implementation-plan.md` § Phase Z

