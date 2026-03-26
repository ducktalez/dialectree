# Dialectree – Implementation Plan

> **Implementation red thread:** see [`docs/discussion-flow.md`](discussion-flow.md) for the guiding example
> that defines the order in which features should be built.
>
> **Taxonomy:** see [`docs/taxonomy.md`](taxonomy.md) for the canonical list of all argument types,
> fallacies, evidence tiers, tag categories, and categorisation dimensions.
>
> **Visualization:** see [`docs/visualization-strategy.md`](visualization-strategy.md) for the
> three-function model (Raw Data → Retrospective Evaluation → Overview) and edge annotations.

---

## Open Technology Decisions

Decisions that **must be made** before the system can reach its final form, but are
not yet locked in. Each is listed with the current default and the trade-off.

| Decision | Current Default | Final Candidate | Trade-off |
|----------|----------------|-----------------|-----------|
| **Database** | In-memory SQLite (StaticPool) | PostgreSQL | SQLite is zero-friction but can't do full-text search, concurrent writes, or JSONB for flexible tag metadata |
| **Search** | None | PostgreSQL `tsvector` or Meilisearch | Needed for tag-similarity suggestions, duplicate detection, argument search |
| **Auth** | `user_id` query param | JWT + OAuth2 (FastAPI `Security`) | Currently no auth at all; must happen before any multi-user deployment |
| **Real-time Updates** | Polling (frontend refetches) | WebSockets or SSE | Needed once multiple users discuss the same topic concurrently |
| **KI / Embeddings** | None | OpenAI API / local sentence-transformers | Required for automatic tag suggestions, duplicate detection, argument anatomy extraction |
| **Task Queue** | None | Celery + Redis or ARQ | Needed for async KI calls, n8n webhook processing |
| **Frontend State** | Local `useState` | Zustand or React Query | Current approach doesn't scale past 3–4 interacting components |
| **CSS / Design System** | Inline styles | Tailwind CSS or Radix UI | Current inline styles are unmaintainable |
| **Migrations** | None (in-memory recreate) | Alembic | Required as soon as data must survive restarts |
| **Deployment** | `uvicorn` local | Docker Compose (FastAPI + PostgreSQL + Redis) | Not needed during dev, required for any shared instance |

---

## Phase 0 – Core Feature Completion

### Completion Status

> **Phase 0 is complete.** All core features are implemented, tested, and documented.
> Next steps: Phase 1 (security/infrastructure) or Phase 2 (advanced features).

| Step | Feature | Status |
|------|---------|--------|
| 0.1 | Argument Anatomy | ✅ Done |
| 0.2 | Visibility & Soft-Delete | ✅ Done |
| 0.3 | Extended Evidence Types | ✅ Done |
| 0.4 | Extended Label Types | ✅ Done |
| 0.5 | Tag Origin & Meta-Categories | ✅ Done |
| 0.6 | Statement Type | ✅ Done |
| 0.7 | Continuous Position Score | ✅ Done |
| 0.8 | Migration Seed Topic | ✅ Done |
| 0.9 | Frontend Rich Tree View | ✅ Done |
| 0.10 | ArgumentGroup Workflow | ✅ Done |

The features below are ordered so each step **builds on the previous one**. Each step
follows a two-stage approach:

1. **Debug Stage** — Backend model + API + tests + raw JSON visible at `/docs`.
   The feature must be fully inspectable before moving on.
2. **Integration Stage** — Frontend visualisation, integrated into the existing tree view
   so the user experiences it naturally.

> **Guiding principle:** Add complexity to the data model only when there is a visible way
> to inspect and verify it. Never add a column that has no endpoint and no UI.

---

### 0.1 — Argument Anatomy (Claim / Reason / Example / Implication)

**Why now:** Every later feature (labels, evidence, KI extraction) targets a specific
*part* of an argument. Without anatomy, all quality assessments apply to an undifferentiated
blob of text.

**Gap:** Currently `ArgumentNode` has only `title` + `description`. The taxonomy (§3)
defines four structural components: Claim, Reason, Example, Implication.

| Task | Type | Detail |
|------|------|--------|
| Add `claim`, `reason`, `example`, `implication` fields to `ArgumentNode` | Model | All `Text`, nullable. `title` remains as display summary. |
| Expose new fields in `ArgumentNodeOut` and `ArgumentNodeCreate` schemas | Schema | Optional fields — backward compatible. |
| Show anatomy in `GET /api/topics/{id}/tree` response | API | New fields in `ArgumentTreeNode`. |
| Update seed data to demonstrate anatomy on 2–3 existing nodes | Seed | Fill the new fields for the Rauchen-Topic. |
| **Tests:** create argument with anatomy, verify in tree response | Test | `test_arguments.py` |
| *Debug:* Verify via Swagger `/docs` that anatomy fields are returned | — | — |
| *Integrate:* Expand node card in frontend to show anatomy (collapsible) | Frontend | Accordion or tooltip per component. |

---

### 0.2 — Visibility & Irrelevance Types (Soft-Delete)

**Why now:** Tagging, labelling, and moderation all need the ability to *hide* an argument
without deleting it. This is the prerequisite for every quality-control feature.

**Gap:** No visibility status on `ArgumentNode`. Hard delete only (`CASCADE`).
Taxonomy §13 defines 6 irrelevance types.

| Task | Type | Detail |
|------|------|--------|
| Add `IrrelevanceType` enum: `VOTED_DOWN`, `MOD_HIDDEN`, `MOVED`, `MERGED`, `SUPERSEDED`, `PENDING_REVIEW` | Model | New `Enum`. |
| Add `visibility` field to `ArgumentNode`: `VISIBLE` (default) or one of the irrelevance types | Model | `String` or `Enum`, default `"VISIBLE"`. |
| Add `hidden_reason` field (`Text`, nullable) | Model | Free-text justification. |
| `PATCH /api/arguments/{id}` accepts `visibility` + `hidden_reason` | API | Only mods should change this later; for now any `user_id`. |
| `GET /api/topics/{id}/tree` excludes hidden nodes by default; `?show_hidden=true` includes them | API | Query param toggle. |
| **Tests:** hide argument, verify tree excludes it; show_hidden includes it | Test | |
| Seed: hide one argument in Rauchen-Topic (e.g. spam example) | Seed | |
| *Debug:* Swagger — verify hidden nodes absent from tree, present with `?show_hidden=true` | — | |
| *Integrate:* Frontend shows hidden nodes as greyed-out / collapsed with reason badge | Frontend | |

---

### 0.3 — Extended Evidence Types & Quality Tiers

**Why now:** Evidence is already modelled but with only 4 types. Taxonomy §7 defines 15 tiers
with quality scores. Aligning the code to the taxonomy enables meaningful evidence display.

**Gap:** `EvidenceType` has 4 values; taxonomy has 15 with implied quality defaults.

| Task | Type | Detail |
|------|------|--------|
| Extend `EvidenceType` enum to match taxonomy §7 tiers: `PROOF`, `META_ANALYSIS`, `STUDY`, `STATISTIC`, `LAW`, `EXPERT_OPINION`, `JOURNALISM`, `SURVEY`, `HISTORICAL`, `ANECDOTE`, `THOUGHT_EXPERIMENT`, `HEARSAY`, `UNFALSIFIABLE`, `FABRICATION` | Model | Replace existing 4-value enum. |
| Add `default_quality` mapping: each type → default score from taxonomy | Logic | Used when `quality_score` is not explicitly set. |
| Maintain backward compatibility: old seed data uses `STUDY`, `STATISTIC`, `ARTICLE` → map `ARTICLE` → `JOURNALISM` | Seed | Migration of seed values. |
| **Tests:** create evidence with each new type; verify default quality score | Test | |
| *Debug:* Swagger — create evidence, inspect quality defaults | — | |
| *Integrate:* Frontend shows evidence badge with quality tier colour (green/yellow/red) | Frontend | |

---

### 0.4 — Extended Label Types & Justification Effects

**Why now:** Labels are the quality-control mechanism. Current 3 types (FALLACY,
DOUBLE_STANDARD, CIRCULAR) cover almost nothing from taxonomy §13 (10 types).

**Gap:** Missing label types. No effect enforcement (labels don't hide arguments yet).

| Task | Type | Detail |
|------|------|--------|
| Extend `LabelType` enum: `FALLACY`, `DOUBLE_STANDARD`, `CIRCULAR`, `MISSING_EVIDENCE`, `OFF_TOPIC`, `SPAM`, `ANECDOTE`, `DUPLICATE`, `CONTENTLESS`, `SCOPE_VIOLATION`, `MANIPULATION`, `INVALID` | Model | |
| Define label → visibility effect mapping (e.g. `SPAM` → `MOD_HIDDEN`, `MISSING_EVIDENCE` → warning only) | Logic | Configurable threshold: e.g. 3 confirmed labels → auto-hide. |
| Add `confirmed` boolean + `confirmed_at` to `NodeLabel` | Model | For community-confirmed labels. |
| **Tests:** create label, confirm label, verify visibility change | Test | |
| *Debug:* Swagger — label an argument as SPAM, verify it becomes hidden | — | |
| *Integrate:* Frontend shows label badges on nodes (⚠️ icon + type) | Frontend | |

---

### 0.5 — Tag Origin & Meta-Categories

**Why now:** Tags exist but are flat strings. Taxonomy §12 requires origin tracking
(User/Mod/KI) and meta-categories (substantive, quality, community, meta-argumentation).

**Gap:** `Tag` has only `name` + `moral_foundation`. No origin, no category.

| Task | Type | Detail |
|------|------|--------|
| Add `TagCategory` enum: `DOMAIN`, `MORAL_FOUNDATION`, `EVIDENCE_QUALITY`, `FALLACY`, `RELEVANCE`, `COMPLETENESS`, `MANIPULATION`, `META_ARGUMENTATION`, `COMMUNITY`, `OTHER` | Model | |
| Add `category` field to `Tag` (nullable, defaults to `OTHER`) | Model | |
| Add `TagOrigin` enum: `USER`, `MODERATOR`, `AI` | Model | |
| Add `origin` field to `argument_node_tags` association (or promote to full model) | Model | Needs a proper `ArgumentNodeTag` model instead of bare association table. |
| **Tests:** create tag with category and origin, verify in response | Test | |
| *Debug:* Swagger — inspect tag metadata | — | |
| *Integrate:* Frontend groups tags by category, shows origin icon (👤/🛡️/🤖) | Frontend | |

---

### 0.6 — Positive vs. Normative Statement Type

**Why now:** The most fundamental categorisation dimension (taxonomy §15). Without it,
factual disputes and value disputes are indistinguishable — which is the root cause of
most unresolvable discussions.

**Gap:** No field on `ArgumentNode`. No way to mark a claim as factual or normative.

| Task | Type | Detail |
|------|------|--------|
| Add `StatementType` enum: `POSITIVE`, `NORMATIVE`, `MIXED`, `UNCLASSIFIED` | Model | |
| Add `statement_type` field to `ArgumentNode` (default `UNCLASSIFIED`) | Model | |
| Expose in tree response | Schema | |
| Seed: classify existing Rauchen-Topic nodes | Seed | |
| **Tests:** create argument with statement_type, verify in tree | Test | |
| *Debug:* Swagger — filter tree by statement_type | — | |
| *Integrate:* Frontend shows Ⓕ (factual) / Ⓥ (value) badge on each node | Frontend | |

---

### 0.7 — Continuous Position Score

**Why now:** PRO/CONTRA/NEUTRAL is a coarse 3-value enum. The taxonomy (§1) envisions a
continuous 0.0–1.0 scale alongside the discrete category.

**Gap:** No `position_score` field.

| Task | Type | Detail |
|------|------|--------|
| Add `position_score` field to `ArgumentNode` (`Float`, nullable, 0.0–1.0) | Model | 0.0 = full CONTRA, 0.5 = NEUTRAL, 1.0 = full PRO. |
| Auto-derive discrete `position` from score if score is provided: <0.33 → CONTRA, 0.33–0.66 → NEUTRAL, >0.66 → PRO | Logic | In create/update endpoint. |
| Expose in tree response | Schema | |
| **Tests:** create argument with position_score, verify derived position | Test | |
| *Debug:* Swagger — verify score ↔ enum derivation | — | |
| *Integrate:* Frontend uses score for gradient node colouring (red ↔ grey ↔ green) | Frontend | |

---

### 0.8 — Migration Seed Topic

**Why now:** The Rauchen-Topic is a good first example but doesn't exercise the new features
(anatomy, statement types, evidence tiers, labels). A second seed topic based on the
migration Leitbeispiel from `discussion-flow.md` demonstrates the full system.

**Gap:** Only one seed topic. Discussion-flow.md defines a rich migration example.

| Task | Type | Detail |
|------|------|--------|
| Add second seed topic: "Deutschland sollte mehr Migranten aufnehmen" | Seed | |
| Populate with 5–8 arguments covering: PRO (Wirtschaft), PRO (Asylrecht), CONTRA (Arbeitsplätze), NEUTRAL (Metadiskussion) | Seed | |
| Use argument anatomy fields on all migration arguments | Seed | |
| Assign statement_type (POSITIVE/NORMATIVE) on each | Seed | |
| Assign tags with different categories and origins | Seed | |
| Add evidence with new extended types (STUDY, LAW, ANECDOTE, EXPERT_OPINION) | Seed | |
| Add labels (FALLACY, MISSING_EVIDENCE, OFF_TOPIC) on selected arguments | Seed | |
| Hide one argument (e.g. "Ausländer raus!" → visibility = VOTED_DOWN) | Seed | |
| Create one ArgumentGroup (economic arguments bundled) | Seed | |
| *Debug:* Start server, verify at `/docs` that all new fields are populated | — | |
| *Integrate:* Frontend already shows the new topic — verify all new badges/colours appear | Frontend | |

---

### 0.9 — Frontend: Rich Tree View

**Why now:** Steps 0.1–0.8 added a lot of backend data. The frontend still shows only
title, position, vote_score, tag names, label names, evidence_count, comment_count.
This step brings all new dimensions into the visual tree.

**Gap:** Frontend has no awareness of anatomy, statement_type, position_score, visibility,
tag categories, evidence quality, label effects.

| Task | Type | Detail |
|------|------|--------|
| Update `types.ts`: add anatomy fields, statement_type, position_score, visibility, hidden_reason | Types | |
| Node card: show anatomy as collapsible sub-sections (Claim → Reason → Example → Implication) | Component | |
| Node card: gradient border colour from position_score (not just 3 fixed colours) | Component | |
| Node card: Ⓕ/Ⓥ badge for statement_type | Component | |
| Node card: tag chips grouped by category, origin icon | Component | |
| Node card: evidence quality bar (green/yellow/red based on avg quality_score) | Component | |
| Node card: label badges with severity colour | Component | |
| Hidden nodes: greyed-out, collapsed, with irrelevance reason tooltip | Component | |
| Toggle: "Show hidden arguments" checkbox | Component | |
| **No new API calls** — all data comes from the existing `/tree` endpoint | — | |

---

### 0.10 — Argument-Group Workflow (Merge / Unmerge)

**Why now:** ArgumentGroup exists as a model but has no real workflow: you can't merge
arguments into a group from the UI, and grouped arguments aren't visually collapsed.

**Gap:** No merge/unmerge API. Frontend doesn't distinguish grouped arguments.

| Task | Type | Detail |
|------|------|--------|
| `POST /api/argument-groups/{id}/merge` — accepts list of `argument_node_ids`, sets their `argument_group_id` | API | |
| `POST /api/argument-groups/{id}/unmerge/{node_id}` — removes a node from the group | API | |
| Tree endpoint: grouped arguments appear as a single collapsed node with expand-to-see-examples | API + Frontend | |
| **Tests:** merge two arguments, verify tree shows single node; unmerge, verify two nodes | Test | |
| *Debug:* Swagger — merge/unmerge calls | — | |
| *Integrate:* Frontend: grouped node shows "3 similar arguments" badge, click to expand | Frontend | |

---

### Summary: Phase 0 Dependency Graph

```
0.1 Anatomy
  └──► 0.6 Statement Type (needs structured fields to classify)
         └──► 0.7 Continuous Position (extends classification further)

0.2 Visibility / Soft-Delete
  └──► 0.4 Label Effects (labels change visibility)
         └──► 0.5 Tag Origin (tags feed into labels)

0.3 Evidence Tiers
  └──► (independent, but enriches 0.8 seed)

0.8 Migration Seed (depends on 0.1–0.7, uses all new fields)
  └──► 0.9 Frontend Rich View (visualises everything from 0.1–0.8)
         └──► 0.10 ArgumentGroup Workflow (final interactive feature)
```

---

## Phase 1 – Post-Development (after core API is stable)

### Security & Auth
- [ ] Password hashing (bcrypt/passlib)
- [ ] Token-based authentication (JWT)
- [ ] User registration / login endpoints
- [ ] Email verification, password reset
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] Restrict CORS origins

### Database & Infrastructure
- [ ] Alembic migrations
- [ ] PostgreSQL setup for production
- [ ] Caching layer (Redis or similar)
- [ ] Monitoring / logging

### Frontend
- [ ] Layout and CSS design (Tailwind CSS or Radix UI)
- [ ] Component library or design system
- [ ] Client-side form validation
- [ ] Error handling UI
- [ ] Responsive design, accessibility
- [ ] Routing (React Router or similar)
- [ ] State management (Zustand or React Query)

## Phase 2 – Advanced Features

### Twitter/X Import
- [ ] N8N workflow for importing Twitter threads (see `n8n/` for sketch)
- [ ] Twitter API v2 integration (Bearer Token)
- [ ] NLP/Embedding-based position detection (PRO/CONTRA/NEUTRAL)
- [ ] Duplicate detection (similar tweets → same ArgumentGroup)

### AI & Embeddings
- [ ] Embedding-based similarity detection for argument grouping
- [ ] Simulation: rational vs. derailing discussant on a topic
- [ ] GROK-style fact-check: AI-assisted verification of claims (similar to Twitter/X community notes)
- [ ] Gamification: reward users for quality contributions (good discussion questions, accurate tags), penalise spam/low-quality input
- [ ] KI-based argument anatomy extraction from free-text input
- [ ] Automatic tag suggestion based on tag-similarity to existing arguments

### Multi-Node Patterns
- [ ] UI for marking and naming patterns across multiple nodes (e.g. Gish gallop, creeping relativization)
- [ ] Pattern detection heuristics

### Definition Forks
- [ ] UI for splitting argument strands by term interpretation (e.g. "racism" has multiple definitions with different moral implications)

### Conflict & Sub-Discussion System
- [ ] Conflict detection (contradicting arguments on same node)
- [ ] Automatic sub-topic creation from conflicts
- [ ] Normative vs. positive conflict separation
- [ ] Conflict resolution workflow with validity score feedback

### User Reputation
- [ ] Domain-specific reputation tracking
- [ ] Weighted voting based on track record
- [ ] Reputation effects from label confirmations / overturns

### Meme Representation (see `docs/meme-catalog.md`)
- [ ] **Phase 2a — Meme Tagging:** Users can tag argument chains with a meme template name (new tag category `MEME` in §12)
- [ ] **Phase 2b — Meme Preview:** Select a meme template + argument chain → static image preview (server-side generation with Pillow or similar)
- [ ] **Phase 2c — KI Suggestion:** System detects argumentative pattern and suggests matching meme template from catalog
- [ ] **Phase 2d — Auto-Generation:** Full meme generation: KI condenses argument text to fit panel constraints + image composition
- [ ] **Phase 2e — Sharability:** Generated memes downloadable as PNG, shareable via link / social media embed

---

## Design Principles (guiding future implementation)

These are not features but **architectural decisions** that should inform all implementation:

### Complexity vs. Simplicity
> The data model should be **extremely complex**. The presentation should be reduced to the
> **simplest and most intuitive view possible**.

- Tags are the primary UI surface — the lightweight entry point for all categorisation.
- Behind the scenes, tags carry meta-categories, origin tracking, moral foundation weights,
  and uncertainty factors (see `taxonomy.md` §12).
- A neural network should eventually learn from tag patterns to improve automatic categorisation
  (e.g. `Gutmensch` → probable moral-values argument, Care foundation).

### Nothing Is Deleted
- Every node, edge, tag, or vote is preserved. Hidden content gets an **irrelevance type**
  (see `taxonomy.md` §13) — never a hard delete.
- Any hidden argument can become the seed for a new discussion.

### Three Tagging Origins
All assessments (tags, labels, scores) can come from three sources:
1. **User-generated** — votable, pr0gramm-style
2. **Moderator-assigned** — with justification, higher authority
3. **KI-generated** — suggested, needs confirmation

Each origin has different authority and disputability rules (see `taxonomy.md` §12.5).

### Continuous Position Slider
- PRO/CONTRA/NEUTRAL is the canonical enum, but the UI should allow **continuous input**:
  click far right = 100% PRO, middle = NEUTRAL, far left = 100% CONTRA.
- The continuous value is stored alongside the discrete enum.

### Contradicting Sources
- When two evidence items on the same node contradict each other, the system should surface
  the semantic difference as prominently as possible (not average it away).
- Conflicting studies → open a sub-discussion to resolve the contradiction.

### Goal Hierarchy Tracking
- Argument strands should track whether a claim is a **terminal goal** (end in itself) or
  an **intermediate goal** (means to an end). See `taxonomy.md` §19.3.
- Intermediate goals must not be promoted to terminal goals without explicit justification.

### Tag Disputability
- If a user considers a tag incorrect, they can **open a meta-discussion** about the tag
  itself. The result affects both the tag and the participants' reputation.

### Debug-First, Integrate-Later
- Every new data dimension must first be **inspectable via Swagger** (`/docs`) and **verified
  by tests** before any frontend work begins.
- Only after the backend is stable and tested should the feature be visually integrated
  into the tree view — keeping the UI simple and progressive.

---

## Deferred: Edge Semantics & Edge Attacks (Zickzack View)

> **Status:** Prototyped in `zickzack.html` (static demo). Not yet backed by API models.
> 
> **Context:** The Zickzack view visualizes dialogues as alternating argument chains.
> Edges (connections between argument cards) carry semantic meaning beyond just
> "this responds to that".

### Edge Types (implemented in static demo)

Edges are annotated with a semantic label that describes *how* the argument responds:

| `edgeType`       | Emoji | Label     | Meaning |
|------------------|-------|-----------|---------|
| `community_note` | 📢    | Unwahr!   | Fact-check / Community-Notes style correction |
| `consequences`   | ⚠️    | Folgen    | Highlights unintended consequences or side-effects |
| `weakening`      | 🤷    | Schwach   | Argues the point is weaker than claimed |
| `reframe`        | 💡    | Reframing | Introduces a new perspective / redefines the debate |
| `concession`     | 🤝    | Konsens   | Partial agreement, finding common ground |

**Future candidates:**
- `steelmanning` (🛡️) — strengthening the opponent's argument before countering
- `question` (❓) — probing / Socratic questioning
- `analogy` (🔗) — arguing by analogy
- `scope_shift` (🎯) — redirecting to a different scope

### Edge Attacks (prototyped)

An **edge attack** targets the *connection* between two arguments, not the content
of either argument. It challenges whether the response is a legitimate continuation
of the discussion at all.

**Example:** In the Rassismus dialogue, R2 ("DOCH! Was ist überhaupt Rassismus?")
doesn't counter L1's *content* — it attacks the *inference* from R1 to L1. L1 claims
"Rassismus gegen Weiße gibt es nicht" as a response to "Quotenregelungen sind
rassistisch." R2 says: the connection itself is flawed because the definition of
Rassismus is disputed.

**Visualized as:** A card with dashed red border (`.edge-attack`) positioned at the
midpoint of the sibling's connection line, connected by a dashed red line with ❌.

**Argumentation-theoretic parallel:** This is an *undercutting defeater* — it doesn't
deny the conclusion but undermines the inferential link between premise and conclusion.

**Open questions for backend modeling:**
1. Should edge attacks be a separate model (`EdgeAttack`) or a special `ArgumentNode`
   with `target_type = 'EDGE'`?
2. How to represent the "target edge" in the DB? Options:
   - `parent_id` + `target_parent_id` (the two nodes forming the edge)
   - A dedicated `edge_id` referencing a first-class `Edge` model
3. Edge attacks often open a **new conflict space** (e.g., "What IS racism?").
   Should this auto-create a new `Topic` or a sub-discussion?

### Edge Challenge System (removed)

The interactive challenge popup (7-button popup on edge click) was **removed** from
`zickzack.html`. Rationale: every challenge category is already covered by existing
mechanisms:

| Former Challenge | Covered by |
|------------------|------------|
| Invalides Argument / Fehlschluss | `Label.FALLACY` on the argument node |
| Fehlender Beleg | Follow-up argument ("missing evidence") |
| Themaverfehlung / falscher Scope | `Label.SCOPE_VIOLATION` |
| Zirkelschluss | `Label.FALLACY` (sub-type circular) |
| Totschlagargument | `Label.KILLER_ARGUMENT` |
| Nur ein Label | `Label.LABEL_ARGUMENT` |
| Schwaches Argument | Downvote |

**What remains:** Edge *types* (author-set semantic labels like `reframe`, `concession`)
and Edge *attacks* (undercutting defeaters — cards that target a connection, not content)
are still present. These represent genuinely distinct concepts that cannot be modelled
as regular follow-up arguments.

### Drag-and-Drop (enabled)

Card dragging is implemented and enabled (`DRAG_ENABLED = true`). All connection types
(main lines, sibling/origin connections, blue chronological flow, split-to-split) update
live during drag. Positions are not persisted — they reset on reload.

**Shared GUI core:** The zigzag view now uses one common geometric core for all early stages:
- shared anchor resolution helpers (topic anchor, card-center anchor, logical edge anchor)
- shared SVG update helpers for curved flow paths and straight logical connections
- stage-specific rendering only decides **which** connection types are drawn, not how anchor math works

This keeps drag behaviour stable across Stage 1–3 and avoids stage-specific geometry bugs.

---

## Phase Z – Dynamic Zigzag View (6-Stufen-Verfeinerungsmodell)

> **Status:** Stufen 0–3 implementiert. Stufen 4–5 deferred. Stufe 6 geplant, separate Spezifikation erforderlich.
> **Depends on:** Phase 0 (core models).
> **Specification:** Die Detail-Spezifikation ist unten direkt in diese Phase integriert.
>
> **Architekturentscheidungen:**
> - Kein `is_thread_primary`: roter Faden implizit über `parent_id`, nicht gespeichert.
> - Kein Edge-Kommentieren (vorerst): Kommentare/Labels nur auf Argumente, nicht auf Verbindungen.
> - Stufe 2 (Split-Prozess) ist ein **Arbeitsschritt** — zeigt Originale + Splits gleichzeitig.
> - Stufe 3 (Verfeinerung) zeigt nur Splits — gesplittete Originale verschwinden.
> - Stufe 6 (Diskussionsnetz) erfordert `AbstractArgument`-Modell + Cross-Topic-Links — vor Implementierung separat spezifizieren.

### Z.0 — Rohdaten / Transkript / YAML ✅

| Task | Type |
|------|------|
| Add `transcript_yaml` (Text, nullable) to `Topic` | Model |
| Expose in `TopicOut` and `TopicCreate` schemas | Schema |
| New endpoint `GET /api/topics/{id}/transcript` returns YAML | API |
| Create `backend/app/data/quoten_blueprint.yaml` with all stages | Data |
| Seed: set `transcript_yaml` on Blueprint topic | Seed |

### Z.1 — Zickzack-Basiszuordnung ✅

| Task | Type |
|------|------|
| Add `stage_added` (Integer, default 1) to `ArgumentNode` | Model |
| Expose in schemas | Schema |
| `GET /api/topics/{id}/zigzag?stage=N` filters `stage_added <= N` (default 2) | API |
| Seed: set `stage_added=1` on all Blueprint base arguments (B₁, A₁…A₅) | Seed |
| UI: stage tab `1️⃣ Basis` shows canvas with `?stage=1` | Frontend |

### Z.2 — Split-Prozess (Arbeitsschritt) ✅

| Task | Type |
|------|------|
| Add `split_from_id` (FK→argument_nodes, nullable) to `ArgumentNode` | Model |
| Expose in schemas | Schema |
| Seed: add new A₄ base node (stage 1); set `stage_added=2` + `split_from_id` on B₁a, B₁b, A₁a, A₄a, A₄b, A₄c | Seed |
| UI: stage tab `2️⃣ Split-Prozess` shows canvas with `?stage=2` — both originals and splits visible | Frontend |
| Basis-Argumente (stage_added=1) keep raw/notepad style in this view and are shown expanded by default | Frontend |
| Stage-2 split cards are shown expanded, but display only their title (no description/body yet) | Frontend |
| Roh-Kette between originals: thick, dimmed (proportional to consolidated info) | Frontend |
| Ursprungs-Argument connections (grey dashed): split → origin via `split_from_id` | Frontend |
| Blue chronological flow: curvy topic-blue line through card centers (Topic→R1→L2.1→…) | Frontend |
| Legend/control panel below the canvas inside the visualization frame describes the four connection types | Frontend |
| Clicking the dashed blue legend entry toggles the blue chronology line on/off | Frontend |
| Split-to-split connections: bright green/red straight lines, `parent_id` → specific opponent split | Frontend |
| L4 splits named (4.1)/(4.2)/(4.3) style with ↩ 3.2 back-references in seed + transcript | Seed |
| Split `parent_id` points to specific opponent split (not original parent) | Seed |
| All connections follow cards during drag | Frontend |

### Z.2a — Stufe-3 Verbindungsarten ✅

Two distinct connection types in Stage 3 Verfeinerung are implemented in `zickzack.html`:

| Task | Type |
|------|------|
| **Chronological flow** connections: dashed topic-blue curves through card centers | Frontend |
| **Logical reference** connections: solid green (PRO) / red (CONTRA), straight, side-docked | Frontend |
| Distinguish both types visually so the discussion flow and logical structure are independently readable | Frontend |

### Z.2b — Split-Toggle-Visualisierung ⬜ Deferred

Button on each split argument to temporarily switch the view to the original argument. Hides sibling splits to maintain the "never show original + splits simultaneously" rule.

| Task | Type |
|------|------|
| Toggle button on split cards: click → show original, hide other splits of same set | Frontend |
| Reverse toggle: click again → restore split view | Frontend |
| Ensure no information is shown twice at any point | Frontend |

### Z.2c — GUI-Editing für Splits ⬜ Deferred

Interactive split creation and connection editing in Stage 2 (Split-Prozess):

| Task | Type |
|------|------|
| Create a new split-set from an existing argument (select argument → "✂ Aufteilen" → enter split titles) | Frontend |
| Draw logical reference connections between split arguments and their targets | Frontend |
| API: `POST /api/arguments/{id}/split` — create split-set from a base argument | API |
| Visual feedback: highlight which original is being split, show split-set grouping | Frontend |

### Z.3 — Verfeinerung (Ergebnis-Ansicht) ✅

| Task | Type |
|------|------|
| UI: stage tab `3️⃣ Verfeinerung` shows canvas with `?stage=2` data, but **hides** originals that have splits | Frontend |
| Filter logic: if any node has `split_from_id` pointing to an original, that original is hidden | Frontend |
| Unsplit originals remain visible in normal card style (not raw style) | Frontend |
| Stage 3 is the first step that adds description/body content to split cards | Frontend |
| Stage-3 cards are collapsible and start collapsed by default | Frontend |
| In chronological layout, split cards of the same side stack directly under each other in the same column | Frontend |
| Two connection types: chronological (dashed blue center-flow) + logical reference (solid, colored) | Frontend |
| API contract remains `?stage=2` data for the frontend; backend accepts `stage=3..6` and currently returns the same node set as stage 2 | API + Frontend |

### Z.4 — Zickzack Einordnung ⚙️ TODO: post-dev

Bewertungen und argumentative Verfeinerungen hinzufügen. Nur auf **Argumente**, nicht auf Verbindungen (Edge-Kommentieren bleibt deferred — zu einem späteren Zeitpunkt diskutieren).

### Z.5 — Meta-Einordnung ⚙️ TODO: post-dev

Argumentgruppen als zu klärende Unterpunkte markieren. Weitere Aufdröslung von Argumenten (Quelle, Grundannahme etc.). Gehört konzeptuell zu Z.4, wird als eigener Schritt implementiert.

### Z.6 — Diskussionsnetz 🔭 Geplant

Konkrete Diskussion in allgemeines Argumentationsnetz einordnen. Erfordert:
- `AbstractArgument`-Modell (Topic-übergreifend)
- Cross-Topic-Links
- Auswählbare Versionen (Steelman / neutral / radikal / häufigste / erste Version)
- Meta-Streit über korrekte Zuordnung

**Vor Implementierung: separate Spezifikation erforderlich.**

### Z.UI — Frontend Stufen-Navigation ✅

| Task | Type |
|------|------|
| Stufen-Tabs 0–6 im Header des Canvas | Frontend |
| Stufe 0: YAML-Viewer (kein Canvas), Daten via `/transcript` | Frontend |
| Stufen 1–3: Zigzag Canvas, gefiltert nach `?stage=N` | Frontend |
| Stufen 4–5: Placeholder `⚙️ Noch nicht implementiert` | Frontend |
| Stufe 6: Placeholder `🔭 Diskussionsnetz — separate Spezifikation erforderlich` | Frontend |

### Phase Z — Detailed Specification

#### 0–6 refinement model

The zigzag view uses one additive data model (`ArgumentNode`) across seven stages:

| Stage | Name | What changes in the UI | Current status |
|------|------|-------------------------|----------------|
| 0 | Transcript | Editable raw transcript textarea, no canvas | ✅ |
| 1 | Basis | Raw transcript-like zigzag, one node per turn, no analysis | ✅ |
| 2 | Split-Prozess | Work step: originals + splits visible simultaneously | ✅ |
| 3 | Verfeinerung | Split origins disappear, refined split view only | ✅ |
| 4 | Einordnung | Votes, comments, conflict-zone markers, edge semantics | ⚙️ TODO: post-dev |
| 5 | Meta | Argument groups, premises, source/meta classification | ⚙️ TODO: post-dev |
| 6 | Netz | Cross-topic argument network | 🔭 Planned |

#### Stage-specific rules

**Stage 0 — Transcript**
- Editable textarea backed by `GET/PUT /api/topics/{id}/transcript`
- No placeholder-only mode: empty transcript is still editable

**Stage 1 — Basis**
- Raw content only: no extra analysis, no back-references like `3.1` or `2.2`
- Transcript/notepad visual style, no votes/comments/labels
- Pure chronological chain: each card links to the previous one

  **Stage 2 — Split-Prozess**
  - Exception to the minimal-information rule: originals and splits are shown together
  - Stage-1 cards stay in raw/notepad style
  - Stage-1/original cards stay expanded by default
  - Split cards also stay expanded by default, but they show only their title at this stage; the body/description is intentionally deferred
  - A small legend/control panel sits below the canvas inside the visualization frame and explains the four connection types
  - The dashed blue chronology line can be toggled on/off directly from that panel
  - Four connection types:
    1. raw chain between originals (thick, dimmed)
    2. origin connection `split_from_id` → original (grey dashed)
    3. blue chronological flow through unfolded sequence (curved, card-center docked)
    4. bright green/red logical references via `parent_id`
  - Cards are draggable; all connection types follow during drag
  - **Planned GUI:** Interactive splitting UI ("split"-set erstellen / Verbindungen per Drag-and-Drop ziehen).
  - **Planned UI Feature:** Advanced Split-Visualization: A button on a split-argument to temporarily switch the visual to the main/original argument. This hides other split-arguments from the same set to adhere to the rule of not showing duplicate information.

**Stage 3 — Verfeinerung**
- Any original referenced by `split_from_id` is hidden
- Unsplit originals remain visible in normal card style
- Split cards receive their body/description for the first time in this stage
- Stage-3 cards are collapsible and start collapsed by default; expanding reveals the full content
- In chronological view, split cards on the same side stack in one shared column instead of being laterally offset
- The legend/control panel below the canvas remains available; the dashed blue chronology line can still be toggled on/off
- Exactly two connection types remain:
  1. chronological flow (topic-blue, dashed, flowing through card centers)
  2. logical reference (green/red, straight, side-docked), including the root argument's connection to the topic
- Backend currently reuses stage-2 node data; Stage-3 semantics are applied in the frontend

#### Split model

- `split_from_id` points from a split node to its stage-1 origin
- `parent_id` points to the specific opponent node or opponent split the split answers
- Visual grouping in Stage 2 is done by `split_from_id`, not by `parent_id`

#### Data model fields used by Phase Z

| Field | Model | Meaning |
|------|-------|---------|
| `transcript_yaml` | `Topic` | Raw transcript for stage 0 |
| `stage_added` | `ArgumentNode` | The stage in which the node first appears |
| `split_from_id` | `ArgumentNode` | Stage-1 base node this split was extracted from |
| `conflict_zone` | `ArgumentNode` | FACT / CAUSAL / VALUE |
| `edge_type` | `ArgumentNode` | Semantic reaction type |
| `is_edge_attack` | `ArgumentNode` | Undercutting/edge attack |
| `opens_conflict` | `ArgumentNode` | Name of newly opened sub-conflict |

#### API semantics

`GET /api/topics/{id}/zigzag?stage=N`
- Returns a flat chronologically sorted list
- Filters by `stage_added <= N`
- `stage=1` = base nodes only
- `stage=2` = base + split nodes
- `stage=3..6` currently return the same backend node set as stage 2; later-stage visibility/line semantics are currently handled in the frontend

`GET /api/topics/{id}/transcript`
- Returns `Topic.transcript_yaml`

`PUT /api/topics/{id}/transcript`
- Replaces the full transcript content

#### Source transcript files

| File | Format | Purpose |
|------|--------|---------|
| `backend/app/data/quoten_diskussion.md` | Markdown | Human-readable quota discussion transcript |
| `backend/app/data/quoten_blueprint.yaml` | YAML | Machine-readable blueprint topic |

#### Still deferred

- Split/original toggle per split card
- GUI editing for split-set creation and connection drawing
- Stage 4–6 interaction model
- Edge-commenting on connections

### Implementation Order

```
Z.0 transcript_yaml ──► Z.1 stage_added ──► Z.2 split_from_id (Split-Prozess)
                                               │
                                           Z.UI Stage tabs (0–6)
                                               │
                                           Z.3 Verfeinerung ✅
                                               │
                                      Z.4 (deferred) ──► Z.5 (deferred)
                                                              │
                                                         Z.6 (planned)
```

---

## UI Collaboration Workflow

> *How to communicate UI/layout ideas efficiently between developer and Copilot.*

### Problem
Describing visual changes in text is imprecise. Screenshots help but can't be edited
collaboratively. Code diffs show implementation, not intent.

### Recommended Approaches

**1. Edit-and-point (empfohlen für dieses Projekt):**
Edit `zickzack.html` directly in the browser dev tools or PyCharm, take a screenshot
or describe the change, and reference the **blueprint dialogue** (`🔧 Blueprint`)
as the shared test case. Example:
> "Im Blueprint: A₄a–A₄c sollen im Fächer-Modus nebeneinander stehen, nicht untereinander.
> A₃ (Meta-Einordnung) soll über den dreien zentriert sein."

**2. ASCII-Mockups im Chat:**
Quick sketches using box-drawing characters. Works well for layout:
```
      [Topic]
    ┌────┼────┐
   A₁   A₂   B₁
         │
    ┌────┼────┐
   A₄a  A₄b  A₄c
```

**3. Annotierte Screenshots:**
Screenshot machen → in Paint/Preview Pfeile und Beschriftungen hinzufügen →
als Bild in den Chat ziehen. Copilot kann Bilder analysieren.

**4. HTML als Whiteboard:**
Den Blueprint-Dialog in `zickzack.html` als interaktives Whiteboard nutzen:
Karten per Drag verschieben (ist aktiviert), dann beschreiben was sich ändern soll.
Der Blueprint existiert genau dafür.

### Convention
When describing UI changes, reference the **blueprint step names** (B₁, A₁, A₂, etc.)
and specify the **view mode** (chronological or fan). This creates an unambiguous shared
vocabulary.

---

## Phase 3 – Extended Test Coverage

Tests that are **not needed during early development** but must be added before go-live:

### Security Tests
- [ ] Authentication & authorisation on all write endpoints
- [ ] Input sanitization (XSS, SQL injection)
- [ ] Rate limiting behaviour
- [ ] CORS restriction enforcement

### Data Integrity Tests
- [ ] Cascade delete consistency across all relationships
- [ ] Concurrent vote/tag operations (race conditions)
- [ ] Large tree performance (1000+ nodes per topic)
- [ ] Soft-delete / irrelevance type transitions

### Business Logic Tests
- [ ] Argument visibility rules (hidden by votes, labels, mod action)
- [ ] Tag origin authority hierarchy (user < KI < moderator)
- [ ] Moral foundation soft-assignment summing to 1.0
- [ ] Uncertainty factor propagation
- [ ] Meta-discussion → tag verdict → reputation effects
- [ ] Scope violation → argument relocation + link integrity
- [ ] ArgumentGroup merging and unmerging
- [ ] Exhaustive case enumeration (MECE) — adding a new case triggers branching

### Frontend Tests
- [ ] Tree rendering with deeply nested nodes
- [ ] Continuous position slider → discrete enum mapping
- [ ] Tag input, voting, and disputability flow

