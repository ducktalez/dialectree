# Dialectree – Implementation Plan

Roadmap of deferred features, ordered by priority. Items here are **not in scope** during the current development phase.

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

### Multi-Node Patterns
- [ ] UI for marking and naming patterns across multiple nodes (e.g. Gish gallop, creeping relativization)
- [ ] Pattern detection heuristics

### Definition Forks
- [ ] UI for splitting argument strands by term interpretation (e.g. "racism" has multiple definitions with different moral implications)

