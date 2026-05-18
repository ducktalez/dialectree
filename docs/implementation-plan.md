# Dialectree – Implementation Plan

> **Implementation red thread:** see [`docs/discussion-flow.md`](discussion-flow.md) for the guiding example
> that defines the order in which features should be built.
>
> **Taxonomy:** see [`docs/taxonomy.md`](taxonomy.md) for the canonical list of all argument types,
> fallacies, evidence tiers, tag categories, and categorisation dimensions.
>
> **Visualization:** see [`docs/visualization-strategy.md`](visualization-strategy.md) for the
> three-function model (Raw Data → Retrospective Evaluation → Overview) and edge annotations.

This document is organized as a **stack**: the most sensible *next* items sit at the top.
Below the stack come open phases (1–3) and the detailed Zigzag specification.
The **Changelog** and **Design Discussions** are at the very bottom.

---

## 🥞 Next Up (Stack)

The next handful of tasks, ordered by what makes sense to tackle next given current
state (no auth, no AI stack, in-memory DB). Pick from the top.

1. **Definition Forks — edit existing entries from the UI** *(frontend, small)*
   Backend `PATCH /api/definition-forks/{id}` exists; current Stage-3 panel only
   supports add + delete. Add inline edit.
2. **Per-user vote tracking on sources** *(blocked by auth — Phase 1)*
   Replace localStorage trust with server-side per-user vote records.
3. **Automatic multi-node pattern detection** *(KI, post-dev)*
   Manual UI exists (see Changelog). Heuristics / KI for auto-suggesting
   Gish-gallop / creeping-relativization patterns require an embedding stack.
4. **Twitter/X import via n8n** *(integration, deprioritized — better methods under consideration)*
   n8n sketch exists in `n8n/`. Parked until a clearer ingestion approach is
   chosen (e.g. direct API, browser extension, manual paste flow).

Everything below this stack is either a larger phase (security/infra, advanced
features) or detail spec for items already on the stack.

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
| **KI / Embeddings** | None (Jaccard stand-in for sources) | OpenAI API / local sentence-transformers | Required for automatic tag suggestions, real duplicate detection, argument anatomy extraction |
| **Task Queue** | None | Celery + Redis or ARQ | Needed for async KI calls, n8n webhook processing |
| **Frontend State** | Local `useState` | Zustand or React Query | Current approach doesn't scale past 3–4 interacting components |
| **CSS / Design System** | Inline styles | Tailwind CSS or Radix UI | Current inline styles are unmaintainable |
| **Migrations** | None (in-memory recreate) | Alembic | Required as soon as data must survive restarts |
| **Deployment** | `uvicorn` local | Docker Compose (FastAPI + PostgreSQL + Redis) | Not needed during dev, required for any shared instance |
| **SRT Parsing** | `srt` library (3.5.x) | — | Lightweight (~200 LOC, zero dependencies); locked in |

---

## Phase 1 – Post-Development (Security & Infrastructure)

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
- [ ] Routing (React Router or similar — if the static HTML approach is dropped)
- [ ] State management (Zustand or React Query)

---

## Phase 2 – Advanced Features

### Quellensammlung — Remaining
The MVP (JSON store, CRUD, voting, inline media, Jaccard similarity, 47 tests) is
done — see Changelog. Still open:

- [ ] **Per-user vote tracking on the server** (requires auth) — currently uses
      client-side localStorage and trusts the `previous` value sent by the client.
- [ ] **Replace Jaccard stand-in with embedding-based similarity** once an embedding
      stack (OpenAI / sentence-transformers) is available.

### Twitter/X Import
- [ ] N8N workflow for importing Twitter threads (see `n8n/` for sketch)
- [ ] Twitter API v2 integration (Bearer Token)
- [ ] NLP/Embedding-based position detection (PRO/CONTRA/NEUTRAL)
- [ ] Duplicate detection (similar tweets → same ArgumentGroup)

### SRT Import — Speaker Diarization (Schritt 2)
Assigning spoken text to speakers. Three options evaluated:

| Option | Approach | Accuracy | Complexity | When |
|--------|----------|----------|------------|------|
| **A — LLM Prompt** (recommended) | Send flowing text to Claude/GPT: *"Identify speakers, output YAML with speaker labels"* | ~95% for clear speaker changes | Low (manual copy-paste or API call) | Now (manual), later as endpoint |
| **B — Audio Diarization** | `pyannote.audio` or `WhisperX` on downloaded audio (`yt-dlp`) | High (uses audio features) | High (audio download, GPU optional) | Phase 2+ |
| **C — Heuristic** | Regex patterns (name prefixes like `R:`, `L:`) | Low (only pre-formatted transcripts) | Minimal | Only if input is already semi-structured |

**Current workflow:** User runs SRT import → gets flowing text in Stage 0 → manually
copies to LLM for speaker segmentation → pastes result back via `PUT /api/topics/{id}/transcript`.

**Future:** `POST /api/topics/{id}/diarize` endpoint with LLM API integration
(requires API key management).

### AI & Embeddings
- [ ] Embedding-based similarity detection for argument grouping
- [ ] Simulation: rational vs. derailing discussant on a topic
- [ ] GROK-style fact-check: AI-assisted verification of claims (similar to Twitter/X community notes)
- [ ] Gamification: reward users for quality contributions (good discussion questions, accurate tags), penalise spam/low-quality input
- [ ] KI-based argument anatomy extraction from free-text input
- [ ] Automatic tag suggestion based on tag-similarity to existing arguments

### Multi-Node Patterns
- [x] **Manuelle UI** in `zickzack.html`: Auswahlmodus, persistente Server-Muster (Stand: siehe Changelog 2026-Q2).
- [ ] Pattern detection heuristics (auto-suggest Gish-gallop / creeping
      relativization based on graph topology + embeddings — requires KI stack).

### Definition Forks
- [x] Backend CRUD + `PATCH` + topic-wide listing (`/api/definition-forks/?topic_id=…`).
- [x] Stage-3 UI: ⑂-Badge mit Inline-Panel zum Hinzufügen/Löschen von Begriffslesarten.
- [ ] Inline-Editing für bestehende Forks (PATCH-Endpunkt ist da, UI noch nicht).
- [ ] Dispute/Voting auf konkurrierende Definitionen (eigene Mini-Diskussion pro Term).

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

---

## Phase Z – Dynamic Zigzag View (open stages)

> **Status:** Stufen 0–3 implementiert (siehe Changelog). Hier nur **offene** Stufen.
> **Depends on:** Phase 0 (core models).
>
> **Architekturentscheidungen:**
> - Kein `is_thread_primary`: roter Faden implizit über `parent_id`.
> - Kein Edge-Kommentieren (vorerst): Kommentare/Labels nur auf Argumente, nicht auf Verbindungen.
> - Stufe 6 (Diskussionsnetz) erfordert `AbstractArgument`-Modell + Cross-Topic-Links — vor Implementierung separat spezifizieren.

### Z.2b — Split-Toggle-Visualisierung ✅

Erledigt — siehe Changelog. Button auf jeder Split-Karte in Stage 3 zeigt
temporär das Original an und blendet die Geschwister-Splits aus.

### Z.2c — GUI-Editing für Splits ✅

Erledigt — siehe Changelog. Inline-Forms in Stage 2: `✂ Aufteilen` auf jeder
Rohkarte erzeugt N Splits (`POST /api/arguments/{id}/split`); `🔗 …` auf
jeder Split-Karte setzt die logische Referenz (`PATCH /api/arguments/{id}/connect`).

### Z.4 — Zickzack Einordnung ⚙️ TODO: post-dev

Bewertungen und argumentative Verfeinerungen hinzufügen. Nur auf **Argumente**,
nicht auf Verbindungen (Edge-Kommentieren bleibt deferred).

### Z.5 — Meta-Einordnung ⚙️ TODO: post-dev

Argumentgruppen als zu klärende Unterpunkte markieren. Weitere Aufdröslung von
Argumenten (Quelle, Grundannahme etc.). Gehört konzeptuell zu Z.4, wird als
eigener Schritt implementiert.

### Z.6 — Diskussionsnetz 🔭 Geplant

Konkrete Diskussion in allgemeines Argumentationsnetz einordnen. Erfordert:
- `AbstractArgument`-Modell (Topic-übergreifend)
- Cross-Topic-Links
- Auswählbare Versionen (Steelman / neutral / radikal / häufigste / erste Version)
- Meta-Streit über korrekte Zuordnung

**Vor Implementierung: separate Spezifikation erforderlich.**

### Phase Z — Detailed Specification (reference)

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

`GET /api/topics/{id}/transcript` — Returns `Topic.transcript_yaml`
`PUT /api/topics/{id}/transcript` — Replaces the full transcript content

#### Source transcript files

| File | Format | Purpose |
|------|--------|---------|
| `backend/app/data/quoten_diskussion.md` | Markdown | Human-readable quota discussion transcript |
| `backend/app/data/quoten_blueprint.yaml` | YAML | Machine-readable blueprint topic |

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

## UI Collaboration Workflow

> *How to communicate UI/layout ideas efficiently between developer and Copilot.*

When describing UI changes, reference the **blueprint step names** (B₁, A₁, A₂, etc.)
and specify the **view mode** (chronological or fan). This creates an unambiguous shared
vocabulary. Preferred channels:

1. **Edit-and-point:** edit `zickzack.html` directly in PyCharm or dev tools, screenshot
   the result and reference the blueprint dialogue (`🔧 Blueprint`) as the shared test case.
2. **ASCII mockups** in chat for layout sketches.
3. **Annotated screenshots** — drop into chat, Copilot can analyse images.
4. **HTML as whiteboard** — use the draggable blueprint cards in `zickzack.html` to
   demonstrate the desired arrangement, then describe the change.

---

## 💬 Design Discussions & Deferred Concepts

Open architectural questions and conceptual sketches that are not yet ready to
become tasks. Captured here so the reasoning isn't lost in chat history.

### Edge Semantics & Edge Attacks (Zickzack View)

> **Status:** Prototyped in `zickzack.html` (static demo). Not yet backed by API models.
>
> **Context:** The Zickzack view visualizes dialogues as alternating argument chains.
> Edges (connections between argument cards) carry semantic meaning beyond just
> "this responds to that".

#### Edge Types (implemented in static demo)

Edges are annotated with a semantic label that describes *how* the argument responds:

| `edgeType`       | Emoji | Label     | Meaning |
|------------------|-------|-----------|---------|
| `community_note` | 📢    | Unwahr!   | Fact-check / Community-Notes style correction |
| `consequences`   | ⚠️    | Folgen    | Highlights unintended consequences or side-effects |
| `weakening`      | 🤷    | Schwach   | Argues the point is weaker than claimed |
| `reframe`        | 💡    | Reframing | Introduces a new perspective / redefines the debate |
| `concession`     | 🤝    | Konsens   | Partial agreement, finding common ground |

**Future candidates:** `steelmanning` (🛡️), `question` (❓), `analogy` (🔗), `scope_shift` (🎯).

#### Edge Attacks (prototyped)

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

#### Edge Challenge System (removed — rationale preserved)

The interactive challenge popup (7-button popup on edge click) was **removed** from
`zickzack.html`. Rationale: every challenge category is already covered by existing
mechanisms (`Label.FALLACY`, follow-up arguments, `Label.SCOPE_VIOLATION`,
`Label.KILLER_ARGUMENT`, `Label.LABEL_ARGUMENT`, downvote).

**What remains:** Edge *types* (author-set semantic labels like `reframe`, `concession`)
and Edge *attacks* (undercutting defeaters — cards that target a connection, not content).

### Drag-and-Drop (enabled — reference)

Card dragging is implemented and enabled (`DRAG_ENABLED = true`). All connection types
update live during drag. Positions are not persisted — they reset on reload. The zigzag
view uses one common geometric core for all early stages (shared anchor resolution, shared
SVG update helpers); stage-specific rendering only decides *which* connection types are
drawn, not how anchor math works.

---

## 📜 Changelog (completed work)

Consolidated record of finished features so the upper sections can stay focused on
what's next. Newest at the top.

### 2026-Q2 — Seed cleanup: removed "Migration" demo topic
Third seed topic "Deutschland sollte mehr Migranten aufnehmen" entirely removed
from `app/seed.py` (it had served as a Phase-0 full-feature demo). Reasoning:
the topic added clutter to the seed/landing experience without contributing
anything that isn't already exercised by the Quotenrassismus topics or by
`tests/`. Topics 1 ("Sollte es Quoten für Minderheiten geben?") and 2
("🔧 Blueprint: Quotenrassismus-Diskussion") remain. Print-summary trimmed
accordingly. Tests still 216/216 green (no test depended on topic 3).

### 2026-Q2 — Definition Forks UI (Stage 3) + backend polish
The Stage-3 Verfeinerung view now lets users attach competing term
interpretations directly to argument cards.

- **Backend** (`routers/definition_forks.py`):
  - `POST` now validates `argument_node_id` → 404 instead of 500 on dangling FK.
  - New `PATCH /api/definition-forks/{id}` to edit term / variant / description.
  - `GET /api/definition-forks/?topic_id=…` joins on `ArgumentNode.topic_id` so
    the frontend can fetch every fork for a topic in one request (badge counts).
- **Frontend** (`zickzack.html`):
  - New per-topic state `currentDefinitionForks`, loaded alongside patterns.
  - Stage-3+ cards carry a `⑂ <n>` badge (or `⑂ +` when empty). Click opens an
    inline panel with the existing forks (term + variant + optional description)
    + an add-row. Delete via 🗑. Mutations reload the topic-wide list and
    re-open the panel so the user sees the new state immediately.
  - Reuses the existing `.inline-form` styling and `postJSON`/`deleteJSON`
    helpers — no new CSS.
- **Tests**: +5 tests in `test_definition_forks.py` (FK 404, topic filter, PATCH
  happy path, PATCH 400 on empty term, PATCH 404). Total 216/216 green.
- **Deferred**: editing existing forks from the UI (currently only add+delete);
  scoring / dispute mechanics on competing definitions.

### 2026-Q2 — Sources JSON → SQLAlchemy (Quellensammlung promoted)
The Quellensammlung is now backed by proper SQL models instead of `sources.json`.

- **Models** (`models.py`): `Source`, `SourceTag` (n:m via `source_tag_link`),
  `SourceComment`, `SourceUsage`. `SourceUsage.argument_id` is a real FK with
  `ON DELETE SET NULL` so curation history survives argument deletion.
- **Router** (`routers/sources.py`): full surface preserved (`GET/POST/PATCH/DELETE
  /api/sources/…`, `/tags`, `/similar`, `/{id}/comments`, `/{id}/usages`,
  `/{id}/vote`) so the frontend keeps working without changes. Tag deduplication
  is now enforced at the schema level (`SourceTag.name UNIQUE`).
- **Seed** (`seed.py`): `_seed_sources_from_json` idempotently imports legacy
  `data/sources.json` on first start; JSON file kept as authoring source for now.
- **Tests** (`tests/test_sources.py`): 47 tests still green (total 211/211).
- **Deferred** (still in Phase 2): per-user vote tracking (needs auth);
  embedding-based similarity (Jaccard stand-in remains).

### 2026-Q2 — Multi-Node-Muster (manuelle UI, Zickzack)
Manuelle Markierung von Mehrknoten-Mustern (z.B. Gish Gallop, schleichende
Relativierung) im Zickzack-View. Backend (Router + 12 Tests) war bereits
vorhanden; jetzt vollständig vom UI bedient.

- **Frontend** (`zickzack.html`):
  - Neuer Auswahlmodus parallel zu Polygon-Bereichen: „🧩 Muster markieren"-Button
    im Legend-Panel, fixe Toolbar unten mit Name-Input + `PatternType`-Select +
    Erstellen/Abbrechen.
  - Persistente Muster werden bei Topic-Wechsel via `GET /api/patterns/?topic_id=…`
    geladen und in `currentPatterns` gehalten.
  - Rendering als **zweite Overlay-Ebene**: dashed convex-hull Outline, Farbe
    nach `pattern_type` (`GISH_GALLOP` rot, `CREEPING_RELATIVIZATION` orange,
    `OTHER` neutralgrau). Folgt Karten beim Draggen.
  - Eigene Legend-Sektion „Muster" mit Type-Badge, Mitgliederzahl, 🗑-Löschen
    pro Eintrag.
  - Sichtbar in Stages 1–3 (in Placeholder-Stages 4–6 nicht).
- **Backend**: keine Änderungen — bestehende Endpunkte (`POST/GET/DELETE
  /api/patterns/`) ausreichend. Pattern-Editing (PATCH) bleiben aufgeschoben;
  bei Bedarf erfolgt Löschen+Neuanlage.
- **Docs**: `architecture.md` (Static-UI-Eintrag), `taxonomy.md` §6 Status
  auf 🟡 (Modell + REST + manuelle UI; Auto-Detection post-dev),
  `implementation-plan.md` Multi-Node-Patterns-Phase 2 aktualisiert.
- Tests unverändert grün (205/205).

### 2026-Q2 — Z.2c GUI editing for splits (Stage 2)
Interactive split creation and connection editing in the Split-Prozess view.

- **Backend** (`routers/arguments.py`):
  - `POST /api/arguments/{id}/split?user_id=…` — body `{splits: [{title, position, description?, parent_id?}]}`.
    Creates N children with `stage_added=2` and `split_from_id=<base>`. If a
    split omits `parent_id`, it inherits the base node's `parent_id` (logical
    reference defaults to the original opponent). Rejects splitting an
    already-split node (Stage-1 only).
  - `PATCH /api/arguments/{id}/connect` — body `{parent_id: int | null}`.
    Convenience endpoint to (re)wire only a split node's logical reference;
    refuses non-split nodes and self-parenting.
- **Tests** (`tests/test_arguments.py`): +13 tests (205/205 total), covering
  inheritance of base parent, explicit parent override, cross-topic rejection,
  zigzag visibility of created splits, connect/unlink, self-parent rejection.
- **Frontend** (`zickzack.html`):
  - Stage-2 raw cards get a `✂ Aufteilen` button (hidden if the original is
    already split). Opens an inline form with addable rows: title, position,
    optional target opponent dropdown.
  - Stage-2 split cards get a `🔗 #<n>` / `🔗 kein Ziel` button. Opens a
    target picker (all Stage-1 raw nodes except own origin); choosing
    "— kein Ziel —" unlinks the parent.
  - Both forms reuse the existing `.inline-form` styling and call the new
    `patchJSON` helper.

### 2026-Q2 — Retired views: Baum, Waage, Konflikt
Removed three standalone static pages whose role is now covered by the
Zickzack data model:

- **`/baum` (index.html — Argumentbaum)** — superseded by Zickzack's layered
  refinement view; the layered tree concept added no power beyond what Zickzack
  already offers.
- **`/entscheidung` (entscheidung.html — Waage)** — never had a concrete use
  case beyond visual gimmickry; weighted aggregation is deferred until a real
  need surfaces.
- **`/konflikt` (konflikt.html — Konfliktanalyse)** — the three-level
  Facts/Causal/Values dimension is already first-class on
  `ArgumentNode.conflict_zone` and will be surfaced inline in Zickzack
  Stage 4 (Einordnung). The standalone explainer added no model power.

Removed: 4 HTML files, 4 routes in `main.py`, nav links across all remaining
pages (`zickzack.html`, `quellen.html`, `rauchen.html`),
references in `architecture.md`, `taxonomy.md` §23/§24, `visualization-strategy.md`.
The standalone `dialog.html` was redundant with the Zickzack Stage-1 view.
192/192 tests still pass — no backend logic depended on these views.

### 2026-Q2 — Z.2b Split-Toggle (Stage 3)
- Button `🔄 Original` on every split card in Stage 3 reveals the original
  argument and hides all sibling splits of the same set.
- Button `↩ Splits` on a revealed-origin card restores the split view.
- Preserves the "never show original + splits simultaneously" design rule.
- Revealed-origin cards start expanded (the user explicitly asked to see them).
- State (`revealedSplitOrigins`) resets on topic/stage change; not persisted.
- Pure frontend change in `zickzack.html`; no backend changes; 192/192 tests still pass.

### 2026-Q2 — Quellensammlung (MVP)
Central, deduplicated registry for evidence sources, served at `/quellen`.
pr0gramm-style fixed 8×128px grid with inline detail expansion.

- JSON-backed data store (`backend/app/data/sources.json`) — no DB table yet
- Backend router `routers/sources.py`:
  - `GET /api/sources/` with filters: `kind`, `tag` (repeatable, AND), `q` full-text,
    `argument_id`, `sort=neu|alt|titel|top|kontrovers|zufall`
  - `GET /api/sources/tags`, `GET /api/sources/{id}`, `GET /api/sources/similar`
    (token-set Jaccard on title + description — lightweight stand-in for embeddings)
  - `POST /api/sources/` with optional thumbnail upload (multipart) — auto-generates
    placeholder SVG if none given
  - `POST /api/sources/{id}/comments`, `POST /api/sources/{id}/usages`
  - `PATCH /api/sources/{id}`, `DELETE /api/sources/{id}` (cleans up managed thumbnail),
    `DELETE …/comments/{idx}`, `DELETE …/usages/{idx}`
  - `POST /api/sources/{id}/vote` — `{value, previous}` transition (per-user tracking deferred)
- Inline media player: YouTube/Vimeo embed for VIDEO sources, `<video>`/`<audio>` for
  uploaded media via `media_url`; tile shows ▶ play icon when a playable medium is detected
- Tests (`tests/test_sources.py`): 47 tests across CRUD, filters, comments, usages,
  patch/delete, voting, media, argument-id filter, random sort, similarity
- Frontend `quellen.html`: fixed 8×128px grid (responsive 6/4/3), click expands detail
  inline at end of row, filter chips (kinds / tags / topics) + search + sort, hash-based
  deep-linking (`#id=<n>&tag=…&q=…`), "Neue Quelle" modal with file upload and live
  duplicate-warning via `/similar`, inline comment + usage forms, keyboard navigation
  (← → ↑ ↓, Enter, Esc)
- Tag conventions: `QUELLE`, `GEGENSEITE`, `SOUNDBOARD`, `WISSENSCHAFT`, `MEME`, plus
  `TOPIC:<SLUG>` namespace for topic association
- Dependency: `python-multipart>=0.0.9` for `Form`/`File` support

### 2026-Q2 — SRT Import Pipeline (YouTube → Stage 0)
- `srt_parser.py`: Parse SRT files → clean flowing text (strips timestamps, HTML tags,
  deduplicates overlapping ASR fragments)
- `POST /api/topics/{id}/import-srt` endpoint stores parsed text as `transcript_yaml`
  in Stage-0 YAML format
- 14 unit + integration tests (`test_srt_parser.py`)
- Dependency: `srt>=3.5.0`

### 2026-Q1 — URL Routing & Unified Header
- Hash-based deep-linking on `zickzack.html` (`#topic=N&stage=M`) — reload preserves view
- Unified header across all static pages: title left, nav links inline, role selector
  far right; active state per page

### 2026-Q1 — Phase Z Stages 0–3
The dynamic zigzag refinement model, stages 0–3 fully implemented.

- **Z.0 — Transcript:** `transcript_yaml` (Text) on `Topic`, `GET/PUT /api/topics/{id}/transcript`,
  blueprint YAML in `backend/app/data/quoten_blueprint.yaml`
- **Z.1 — Basis:** `stage_added` (Integer, default 1) on `ArgumentNode`,
  `GET /api/topics/{id}/zigzag?stage=N` filters `stage_added <= N`,
  Stage-1 cards use raw/notepad style
- **Z.2 — Split-Prozess:** `split_from_id` (FK → `argument_nodes`, nullable) on
  `ArgumentNode`; UI shows originals + splits simultaneously with four connection
  types (raw chain, origin dashed, blue chronological flow, green/red logical
  references); legend/control panel below canvas with toggleable chronology line
- **Z.2a — Stufe-3 Verbindungsarten:** two distinct connection types in Verfeinerung
  view (chronological flow vs. logical reference), visually distinguishable
- **Z.3 — Verfeinerung:** filters out originals referenced by `split_from_id`,
  shows split bodies for the first time, cards collapsible (collapsed by default),
  chronological column-stacking for same-side splits
- **Z.3a — Polygon-Overlay:** subtle convex-hull polygons marking argumentative
  branches; auto-groups (Stage 2: by `split_from_id`; Stage 3: by `parent_id` branching);
  custom groups via card selection mode; individual group toggles in legend;
  polygons follow cards during drag
- **Z.UI — Stage tabs 0–6:** placeholder for stages 4–6, full canvas for 1–3,
  YAML viewer for stage 0

### 2025-Q4 — Phase 0 Core (complete)

> All core features below are implemented, tested, and documented against
> `architecture.md` and `taxonomy.md`.

| Step | Feature | What was added |
|------|---------|----------------|
| 0.1 | Argument Anatomy | `claim`/`reason`/`example`/`implication` fields on `ArgumentNode`; exposed in tree |
| 0.2 | Visibility & Soft-Delete | `IrrelevanceType` enum (6 values), `visibility` + `hidden_reason` fields, `?show_hidden=true` toggle |
| 0.3 | Extended Evidence Types | `EvidenceType` extended to 15 tiers per taxonomy §7 with `default_quality` mapping |
| 0.4 | Extended Label Types | `LabelType` extended (12+ types), `confirmed`/`confirmed_at` on `NodeLabel`, label → visibility effect mapping |
| 0.5 | Tag Origin & Meta-Categories | `TagCategory` (10 values), `TagOrigin` (USER/MOD/AI), proper `ArgumentNodeTag` model |
| 0.6 | Statement Type | `StatementType` enum (POSITIVE/NORMATIVE/MIXED/UNCLASSIFIED) |
| 0.7 | Continuous Position Score | `position_score` (Float 0.0–1.0) on `ArgumentNode`, auto-derives discrete position |
| 0.8 | Migration Seed Topic | (Removed 2026-Q2) A third seed topic "Deutschland sollte mehr Migranten aufnehmen" was added to exercise anatomy / visibility / labels / evidence / group end-to-end. Dropped from the seed to keep the demo focused on the Zickzack stages; the underlying features are still covered by tests. |
| 0.9 | Frontend Rich Tree View | Anatomy sub-sections, gradient borders, Ⓕ/Ⓥ badges, category-grouped tag chips, evidence quality bars, label severity, hidden-node greying |
| 0.10 | Argument-Group Workflow | `POST /api/argument-groups/{id}/merge` and `/unmerge/{node_id}`, grouped node display |




