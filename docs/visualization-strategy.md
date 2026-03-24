# Dialectree – Visualization Strategy

> **Key insight:** The Zickzack format is the core visualization. All other views
> (Mindmap, Waage, Konfliktanalyse) are derived aggregations built on top of
> recorded dialogues.

---

## Three Functions of the Zickzack

Every discussion visualization serves exactly **one of three functions**:

### Function 1 — Raw Data (Transkription)

A single, concrete discussion is recorded as a **Zickzack dialogue**.

- Each argument occupies one side (PRO left, CONTRA right).
- The **main strand** is the sequence of best arguments each side chose to pursue.
- **Alternative arguments** branch off but are greyed out — they were available
  but not pursued in this particular exchange.
- The dialogue ends at a **dead end**: consensus, dissent, loop, or unresolved
  factual/logical/value disagreement.

**Implementation:** `zickzack.html` — SVG-based, with needle-path showing
cumulative persuasion shift.

### Function 2 — Retrospective Evaluation (Persönliche Bewertung)

After a discussion is recorded, **other users** can:

- **Rate** how strongly each argument shifts the debate (drag arguments
  left/right on the needle spectrum).
- **Tag** arguments with quality labels (fallacy, missing evidence, off-topic, etc.).
- **Mark** which zone (facts / causality / values) each argument belongs to.
- **Flag** connections with emojis indicating the type of response:
  - ❌ Invalid argument / logical fallacy
  - ⚠️ Missing evidence
  - 🔗 Causal claim
  - 🎯 Scope violation / topic change
  - 💬 Opens new sub-discussion
  - 📄 Source/evidence provided (rendered differently from arguments)
  - 🔄 Circular reasoning detected

This creates a **crowd-annotated** version of the original dialogue.

### Function 3 — Overview (Gesamtübersicht)

Multiple recorded discussions on the **same topic** are overlaid:

- Common argument paths merge into thicker, more prominent strands.
- Unique or rare arguments appear as thin branches.
- **Cycles** become visible: where do discussions always loop?
- **Meta-discussions** can be marked at overlay points (e.g. "this is where
  the definition of 'racism' always becomes the real dispute").
- Dead ends cluster by type: which topics end in value disagreement vs.
  factual disagreement?

**Goal:** A map of all possible ways a discussion on topic X can unfold,
annotated with where each path typically stalls.

---

## Argument Network (from accumulated dialogues)

The sum of many recorded discussions forms a **directed graph** (not just a tree):

```
        ┌── Argument A ──► Argument B ──► Dead End (consensus)
Topic ──┤
        └── Argument A ──► Argument C ──► Argument D ──► Dead End (value dissent)
                                │
                                └──► Sub-Discussion: "What is X?"
```

### Connection Types (Edge Annotations)

Each edge in the network should carry metadata:

| Emoji | Meaning | Effect |
|-------|---------|--------|
| ❌ | Invalid / fallacy | Marks a logical error |
| ⚠️ | Missing evidence | Argument needs backing |
| 🎯 | Scope violation | Argument belongs in a different discussion |
| 💬 | Opens sub-discussion | Creates a new topic branch |
| 📄 | Evidence attached | Source provided (rendered differently) |
| 🔄 | Circular reference | Points back to earlier argument |
| 🔀 | Conflict field | Normative vs. positive disagreement |
| 🏷️ | Meta-argument | Categorization or framing move |
| 💣 | Killer argument | Ends the discussion strand ("Totschlagargument") |
| 🤷 | Weak argument | Low argumentative value |
| 🛡️ | Defense | Defensive response without new substance |
| 📢 | Opening claim | First assertion in a new strand |
| 🤝 | Consensus point | Both sides agree here |

### Edge Attack (Kanten-Angriff)

An **edge attack** targets the *connection* between two arguments — not the content
of either one. It challenges whether the response is a legitimate continuation of
the discussion at all (an *undercutting defeater* in argumentation theory).

**Example:** "DOCH! Was ist überhaupt Rassismus?" doesn't counter the argument's
content — it attacks the *inference* from the previous argument to the response.

**Visualized as:** A card with dashed red border positioned at the midpoint of the
connection line, connected by a dashed red line with ❌.

> **Removed:** The interactive challenge popup (7-button popup on edge click) was
> removed. All challenge categories (fallacy, missing evidence, scope violation, etc.)
> are already covered by the existing `Label` and `Vote` systems on argument nodes.
> See `implementation-plan.md § Edge Challenge System (removed)` for the mapping.

### Sources vs. Arguments

Sources (studies, laws, statistics) must be **visually distinct** from arguments:
- Arguments: solid border, colored by position (green/red/grey)
- Sources: dashed border, neutral color, quality-tier badge
- Sources can be disputed independently (opens evidence-quality sub-discussion)

### Meta-Discussion Overlay

When multiple discussions converge on the same sub-question (e.g. "Is X really
caused by Y?"), the overlay visualization highlights these as **meta-discussion
nodes** — shared conflict points that appear across many conversations.

Potential visualization: pulsing or highlighted nodes at convergence points,
with a count badge ("12 discussions hit this point").

---

## View Hierarchy

| View | Purpose | Data Source |
|------|---------|-------------|
| **Zickzack** | Single dialogue, raw recording | One discussion |
| **Mindmap / Präsentation** | Dialectical tree with pursued + alternative branches | One discussion, expanded |
| **Konfliktanalyse** | Where does the disagreement lie? (Facts/Causality/Values) | One topic, aggregated |
| **Waage / Entscheidung** | Neutral decision support — weigh all arguments | One topic, aggregated |
| **Dialog** | Chat-style back-and-forth | One discussion, sequential |
| **Network** *(future)* | Overlay of all discussions on a topic | Multiple discussions |

---

## Stage 3: Dual Connection Types

In Stage 3 (Verfeinerung), two distinct connection types coexist. They serve different purposes and must be visually distinguishable:

| Connection type | Purpose | Visual style | Dock position |
|-----------------|---------|--------------|---------------|
| **Chronological flow** | Traces the temporal sequence of the discussion — "who spoke when" | Dashed, flowing curve, colored by discussion topic | Center of card (top/bottom) |
| **Logical reference** | Shows which (sub-)argument addresses which other — "what responds to what" | Solid, straight line, green (PRO) / red (CONTRA) | Side of card (left/right) |

This separation allows the reader to independently follow:
1. The **discussion timeline** (how the conversation actually unfolded)
2. The **logical structure** (which argument refutes or supports which)

Central docking for chronological connections and side docking for logical references is the recommended approach to maximize visual distinction.

---

## Design Principles for Visualization

1. **Greyed-out alternatives** show what arguments were *available* but not
   *pursued*. This prevents the illusion that the chosen path was the only one.

2. **Emojis on connections** provide instant visual feedback about the type of
   response (refutation, evidence, scope shift, etc.).

3. **The main strand is always readable** — alternative branches never obscure
   the primary argument chain.

4. **Sources look different from arguments** — no confusion between "someone
   claims X" and "study Y shows X".

5. **Dead ends are always classified** — consensus 🤝, dissent 🔀, loop 🔄,
   or unresolved ❓ — so users can see at a glance where a discussion stopped
   and why.


