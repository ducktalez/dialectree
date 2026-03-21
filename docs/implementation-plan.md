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

| Step | Feature | Status |
|------|---------|--------|
| 0.1 | Argument Anatomy | ✅ Done |
| 0.2 | Visibility & Soft-Delete | ✅ Done |
| 0.3 | Extended Evidence Types | ✅ Done |
| 0.4 | Extended Label Types | ✅ Done |
| 0.5 | Tag Origin & Meta-Categories | ✅ Done |
| 0.6 | Statement Type | ✅ Done |
| 0.7 | Continuous Position Score | ✅ Done |
| 0.8 | Migration Seed Topic | ⬜ Next |
| 0.9 | Frontend Rich Tree View | ⬜ Pending |
| 0.10 | ArgumentGroup Workflow | ⬜ Pending |

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

### Edge Challenge System (prototyped, interactive)

Users can click an edge marker to open a **challenge popup** that lets them mark the
transition as problematic:

| Challenge | Emoji | Meaning |
|-----------|-------|---------|
| Invalides Argument / Fehlschluss | ❌ | Logical fallacy |
| Fehlender Beleg | ⚠️ | Missing evidence |
| Themaverfehlung / falscher Scope | 🎯 | Off-topic for this thread |
| Zirkelschluss / bereits diskutiert | 🔄 | Circular reasoning |
| Totschlagargument | 💣 | Conversation-stopper |
| Nur ein Label, kein Argument | 🏷️ | Name-calling, not reasoning |
| Schwaches Argument | 🤷 | Weak / unsubstantiated |

**Distinction from edge types:** Edge *types* describe the nature of the argument
transition (set by the author). Edge *challenges* are reactions by other participants
who dispute the legitimacy of that transition.

**Future:** Challenges could feed into a voting/moderation system that collapses or
highlights disputed edges. This connects to the existing `Label` system (e.g.,
`FALLACY`, `SCOPE_VIOLATION`).

### Drag-and-Drop (deferred)

Card dragging is implemented but disabled (`DRAG_ENABLED = false`). The infrastructure
(updateLines, drag handlers) is preserved for future use. Re-enable when:
- The UX for "what does dragging mean semantically" is clarified
- Positions can be persisted (requires backend support)

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

