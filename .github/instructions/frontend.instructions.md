---
applyTo: "frontend/**,backend/app/static/**"
---
# Frontend & Static UI Instructions

These instructions supplement the global `.github/copilot-instructions.md` for files inside `frontend/` and `backend/app/static/`.

## What "only the necessary" means here
- **No complex state management.** Plain `useState`/`useEffect` is sufficient.
- **No routing library** unless strictly needed for a specific task.
- The backend is the priority. Frontend must not block backend development.

## Argument Tree Display Rules
The tree view is the core UI. Follow these rules for any tree rendering (static `index.html` **and** React frontend):

1. **Layered layout** — the view is organized as **horizontal rows stacked vertically** (`.layer-stack`), each representing a semantic level. From top to bottom: 🌍 Highest goal ("Erschaffen einer lebenswerten Welt") → 🎯 Societal goals (from `SOCIETAL_GOAL` tags: Sicherheit, Freiheit, Gerechtigkeit, Wohlstand, Nachhaltigkeit) → ❓ Topic question → 💬 Main arguments (depth 0) → 🔗 Sub-arguments (depth 1) → 📌 Premises (depth 2+). **Moral Foundations** (Care, Fairness, etc.) are NOT a separate layer — they stay as tag pills on argument cards, explaining WHY people prioritize certain goals. Domain tags also stay as pills. Each layer is a `.layer` with a `.layer-label` and a `.layer-row` (flex, centered, wrapping).
2. **No redundant text** — position type (PRO/CONTRA/NEUTRAL) is conveyed **only** by the coloured left border, never as a text badge.
3. **Tight-fit nodes** — each node uses `width: fit-content` with `max-width: 210px`. No stretching. Goal node has warm gold gradient, value nodes purple, domain nodes teal, topic node blue.
4. **Premises as subtle annotations** — depth-2+ nodes (examples, anecdotes, ground truths) use the `.premise-node` class: dashed border, italic title, smaller font (0.66rem), 70% opacity, max-width 180px. They are visually subordinate, appearing as background supporting material rather than main argument cards.
4. **SVG diagonal connectors between layers** — cubic bezier curves connect cards across layers. Meta-connections (value→domain→topic) are thin/light grey. Argument connections are thicker and coloured by child position (green=PRO, red=CONTRA, orange=NEUTRAL). **Connection endpoints are spread** along card edges (not converging at center).
5. **Emoji on argument connectors** — ✅ PRO, ❌ CONTRA, 💡 NEUTRAL, ⚠️ FALLACY. Only on argument-level connections, not on meta-connections.
6. **PRO left, CONTRA right** — within each layer row, arguments are sorted PRO → NEUTRAL → CONTRA, then by vote score descending.
7. **Score as coloured number** — `+3`, `-1`, `0`. Green/red/grey. No emoji.
8. **Tags/labels as pills** — tags blue, labels orange, compact inline.
9. **Full page width** — no `max-width` on `#app`. Layers use `flex-wrap: wrap` to prevent overlap.
10. **Data derivation** — moral values and societal domains are **derived from tags** on argument nodes (by `category`). No separate DB model needed. The tree is flattened and nodes grouped by depth to determine their layer.


