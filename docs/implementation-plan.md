# Dialectree – Implementation Plan

Roadmap of deferred features, ordered by priority. Items here are **not in scope** during the current development phase.

> **Implementation red thread:** see [`docs/discussion-flow.md`](discussion-flow.md) for the guiding example
> that defines the order in which features should be built.
>
> **Taxonomy:** see [`docs/taxonomy.md`](taxonomy.md) for the canonical list of all argument types,
> fallacies, evidence tiers, tag categories, and categorisation dimensions.

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
- [ ] Layout and CSS design
- [ ] Component library or design system
- [ ] Client-side form validation
- [ ] Error handling UI
- [ ] Responsive design, accessibility
- [ ] Routing (React Router or similar)

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

### Multi-Node Patterns
- [ ] UI for marking and naming patterns across multiple nodes (e.g. Gish gallop, creeping relativization)
- [ ] Pattern detection heuristics

### Definition Forks
- [ ] UI for splitting argument strands by term interpretation (e.g. "racism" has multiple definitions with different moral implications)

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
