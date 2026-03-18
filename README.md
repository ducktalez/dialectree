# Dialectree 🌳

Structured argument trees for better discussions.

## What is Dialectree?

Discussions repeat endlessly (especially online). The same arguments get made, refuted, and forgotten — over and over. Dialectree breaks this cycle by mapping every debatable question into a **logical argument tree**: one root question, branching into PRO/CONTRA/NEUTRAL arguments, each of which can have sub-arguments, down to the underlying moral premises.

Similar arguments (same point, different wording) are grouped into a single bubble. Fallacies can be flagged. Circular reasoning becomes visible. The goal: every argument gets made **once**, clearly, in the right place.

## Documentation

| Document | Purpose |
|----------|---------|
| [`docs/taxonomy.md`](docs/taxonomy.md) | Canonical reference for all argument types, fallacies, evidence tiers, tag categories, and categorisation dimensions |
| [`docs/discussion-flow.md`](docs/discussion-flow.md) | Guiding example ("Deutschland sollte mehr Migranten aufnehmen") — defines the implementation red thread |
| [`docs/implementation-plan.md`](docs/implementation-plan.md) | Roadmap, deferred features, design principles, extended test coverage |
| [`docs/architecture.md`](docs/architecture.md) | Technical architecture overview |

## Concept Clusters

The following concepts are planned or partially implemented. This is not a final list.

### Core – Argument Structure
- **Topics**: the root question (e.g. "Should smoking be banned?")
- **ArgumentNodes**: individual arguments (PRO / CONTRA / NEUTRAL), forming a tree via parent references
- **ArgumentGroups**: bundle similarly worded arguments under one canonical title (shortest/strongest/most neutral version)
- **DefinitionForks**: when a term has multiple interpretations (e.g. "racism"), the argument strand splits — different definitions lead to different moral implications

### Quality & Credibility
- **Fallacy labels**: mark an argument as a fallacy (requires justification)
- **Double standards**: flag inconsistent application of a principle
- **Evidence**: attach sources (studies, statistics, articles, historical events) with a quality score (0.0–1.0)
- **Moral Foundations Theory tags**: Care, Fairness, Loyalty, Authority, Sanctity — fixed tag category for moral premises

### Patterns & Parallels
- **Multi-node patterns**: name and mark patterns that span multiple nodes (e.g. Gish gallop, creeping relativization)
- **Argumentative parallels**: link structurally similar arguments across different topics
- **Loop detection**: surface when a discussion circles back to an already-addressed point

### Social & Interaction
- **Users**: authors of arguments, votes, comments
- **Voting**: up/down on argument nodes (+1 / -1)
- **Tags**: user-generated, votable (pr0gramm-style)
- **Comments**: free-text discussion on individual nodes

### Import & AI (future)
- **Twitter/X import**: automatically parse threads into argument trees (N8N workflow sketch in `n8n/`)
- **Embedding-based grouping**: detect similar arguments for automatic ArgumentGroup suggestions
- **Discussion simulation**: model how a rational vs. derailing discussant would navigate a topic

## Quick Start

### PyCharm (recommended)
The project ships with ready-to-use Run Configurations (in `.idea/runConfigurations/`). After opening the project, use the **Run** dropdown:

| Configuration      | What it does                            |
|---------------------|-----------------------------------------|
| **Backend Server**  | `uvicorn app.main:app --reload`         |
| **Backend Tests**   | `pytest tests/ -v`                      |
| **Seed Data**       | `python -m app.seed`                    |
| **Frontend Dev**    | `npm run dev` (Vite dev server)         |

### Manual (terminal)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

### Seed data
```bash
cd backend
python -m app.seed
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # dev server on http://localhost:5173 (proxies /api → backend)
```
> **Note:** Node.js is only required during development (for Vite).
> In production, `npm run build` compiles the app to static files that FastAPI serves directly — no Node.js on the server.
> Install Node.js LTS once from [nodejs.org](https://nodejs.org), then `npm install && npm run dev` is all you need.

## Project Structure
```
dialectree/
├── .github/copilot-instructions.md   # agent instructions (auto-loaded)
├── docs/taxonomy.md                  # canonical reference: all argument types, fallacies, evidence tiers, tags
├── docs/discussion-flow.md           # guiding example & implementation red thread
├── docs/implementation-plan.md       # deferred features & roadmap
├── backend/
│   ├── app/                          # FastAPI app, models, schemas, routers
│   └── tests/                        # pytest
├── frontend/                         # React + React Flow (minimal during dev)
└── n8n/                              # Twitter import workflow (sketch)
```
