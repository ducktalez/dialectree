# Dialectree – Taxonomy

Central reference for all argument types, categorisation dimensions, fallacies, evidence
tiers, tag systems, and meta-discussion patterns used in Dialectree.
Every enum, label, or tag category that appears in the system should trace back to an entry
in this document.

> **Maintainer note:** When a new category is implemented, mark it with ✅.
> Planned but not yet implemented categories are marked ❌.
> Partially implemented (model exists, logic incomplete) are marked ⚠️.

---

## Table of Contents

1. [Argument Position](#1-argument-position)
2. [Genuine Argument Types](#2-genuine-argument-types)
3. [Argument Anatomy](#3-argument-anatomy)
4. [Fallacies (Pseudo-Arguments)](#4-fallacies-pseudo-arguments)
5. [Non-Argumentative Exit Moves](#5-non-argumentative-exit-moves)
6. [Meta-Discussion Strategies](#6-meta-discussion-strategies)
7. [Evidence Hierarchy](#7-evidence-hierarchy)
8. [Rule Systems (Normative Frameworks)](#8-rule-systems-normative-frameworks)
9. [Consensus-Finding Mechanisms](#9-consensus-finding-mechanisms)
10. [Moral Foundations](#10-moral-foundations)
11. [Philosophical Razors](#11-philosophical-razors)
12. [Tag Categories](#12-tag-categories)
13. [Label Types (Quality / Moderation)](#13-label-types-quality--moderation)
14. [Rhetorical Devices & Question Types](#14-rhetorical-devices--question-types)
15. [Statement Types: Positive vs. Normative](#15-statement-types-positive-vs-normative)
16. [Authority Types](#16-authority-types)
17. [Scope & Branching](#17-scope--branching)
18. [Thought Experiments, Analogies & Transferability](#18-thought-experiments-analogies--transferability)
19. [Propaganda, Manufacturing Consent & Systemic Manipulation](#19-propaganda-manufacturing-consent--systemic-manipulation)
20. [Political Compass Mapping](#20-political-compass-mapping)
21. [Meme Representation](#21-meme-representation)
22. [Strategic Frameworks (Reference)](#22-strategic-frameworks-reference)

---

## 1. Argument Position

Every argument node has exactly one position relative to its parent thesis.

| Position    | Meaning                          | Status |
|-------------|----------------------------------|--------|
| `PRO`       | Supports the parent claim        | ✅     |
| `CONTRA`    | Opposes the parent claim         | ✅     |
| `NEUTRAL`   | Contextualises without taking sides | ✅  |

Future consideration: continuous scale (0.0 = full CONTRA … 0.5 = NEUTRAL … 1.0 = full PRO)
so users can express partial agreement. The discrete enum remains the canonical category.

---

## 2. Genuine Argument Types

These are logically valid forms of reasoning. Each argument in the system can be tagged with
one or more of these types to make the reasoning structure explicit.

### 2.1 Deductive Arguments (conclusion follows necessarily)

| Type | Description | Example |
|------|-------------|---------|
| **Modus Ponens** | If P then Q; P; therefore Q | "If all EU citizens have freedom of movement, and Poles are EU citizens, then Poles have freedom of movement." |
| **Modus Tollens** | If P then Q; not Q; therefore not P | "If migration causes unemployment, unemployment should rise. It didn't, so migration doesn't cause it." |
| **Disjunctive Syllogism** | P or Q; not P; therefore Q | "Either we increase migration or accept labour shortages. We won't accept shortages, so we must increase migration." |
| **Hypothetical Syllogism** | If P→Q and Q→R, then P→R | "If we need nurses, and migration provides nurses, then we need migration." |
| **Reductio ad Absurdum** | Assume P, derive contradiction, therefore not P | "If we deport all migrants, hospitals collapse — absurd, so we shouldn't." |
| **Categorical Syllogism** | All A are B; C is A; therefore C is B | "All asylum seekers have legal rights. This person is an asylum seeker. Therefore they have legal rights." |

### 2.2 Inductive Arguments (conclusion is probable, not certain)

| Type | Description | Example |
|------|-------------|---------|
| **Generalisation** | Sample → general rule | "In 15 studied countries, migration raised GDP. Migration probably raises GDP generally." |
| **Statistical Argument** | Data-driven probability claim | "78 % of economists agree that migration is net-positive." |
| **Causal Argument** | X causes Y (empirical) | "Countries with higher immigration have lower old-age dependency ratios." |
| **Argument by Analogy** | Similar case → similar outcome | "Canada's points-based system works; a similar system would work here." |
| **Predictive Argument** | Past pattern → future expectation | "Demographic projections show a 4M worker shortfall by 2035 without migration." |

### 2.3 Abductive Arguments (best explanation)

| Type | Description | Example |
|------|-------------|---------|
| **Inference to Best Explanation** | Among competing hypotheses, the one that best explains evidence | "The most likely explanation for the nursing shortage is demographic decline, not laziness." |
| **Inference from Elimination** | Rule out alternatives, what remains must be true | "We've tried automation, higher wages, longer hours — only migration closes the gap." |
| **Exhaustive Case Enumeration** (MECE Map) | List all possible cases; address or eliminate each; what remains must hold | See example below |

#### Exhaustive Case Enumeration — Detail

A powerful argumentative tool: enumerate **all** possible explanations or options (mutually
exclusive, collectively exhaustive — MECE), then address each one. What survives elimination
is the remaining conclusion. As long as no one identifies a missing case, the enumeration holds.

```
Example 1 — Reasons to have children:
  Cases: [Desire for children | Social pressure | Old-age provision | Side-effect of sex]
  → Three of four have been weakened by modernity.
  → Remaining dominant factor: intrinsic desire for children.
  → Valid until someone identifies a 5th case.

Example 2 — On-demand energy for an industrial nation:
  Cases: [Fossil fuels | Nuclear energy | Energy storage]
  → Renewables cannot generate on-demand → not in the case set.
  → Each case can now be argued independently.
  → Valid until a new on-demand source is identified.
```

> **System implication:** When a user creates an exhaustive enumeration, the system should
> track the case list and flag when a new case is proposed (branching trigger).

### 2.4 Practical / Normative Arguments

| Type | Description | Example |
|------|-------------|---------|
| **Means-End Argument** | To achieve X, we must do Y | "To maintain the pension system, we need more contributors → migration." |
| **Argument from Values** | X aligns with value V, V is important, therefore X | "Taking in refugees aligns with human dignity — a core value of our constitution." |
| **Argument from Consequences** | X leads to good/bad outcome → do/avoid X | "Restricting migration leads to economic decline." |
| **Argument from Fairness** | Equal treatment demands X | "If we accept Ukrainian refugees, consistency demands we accept Syrian ones too." |
| **Lesser Evil** | X is bad, but Y is worse | "Integration costs are high, but the alternative (ageing society) is worse." |
| **Precautionary Argument** | Uncertain risk → err on the side of caution | "We don't know the long-term effects; we should proceed carefully." |

### 2.5 Other Legitimate Forms

| Type | Description | Example |
|------|-------------|---------|
| **Argument from Authority** (legitimate) | Expert consensus supports X | "The UNHCR recommends expanding legal migration pathways." |
| **Thought Experiment** | Hypothetical scenario to test a principle | "Imagine you were born in a war zone — wouldn't you want asylum?" |
| **Definitional Argument** | X meets/doesn't meet definition of Y | "'Economic migrant' and 'refugee' are legally distinct categories." |
| **Burden-of-Proof Argument** | The claim-maker must provide evidence | "You claim migration causes crime — the burden of proof is on you." |

---

## 3. Argument Anatomy

Every argument can be decomposed into up to four structural components:

| Component | Role | Required? |
|-----------|------|-----------|
| **Claim** (Behauptung) | The core assertion | Yes |
| **Reason** (Begründung) | Why the claim is believed to be true | Yes |
| **Example** (Beispiel) | Concrete instance or illustration | No |
| **Implication** (Implikation) | What follows if the claim is accepted | No |

```
Claim:       "Our society depends on migration."
Reason:      "There aren't enough people willing to do certain jobs."
Example:     "Healthcare would collapse without migrant workers."
Implication: "Therefore migration is economically necessary."
```

Status: ❌ not yet implemented (currently a single `title` + `description` field)

---

## 4. Fallacies (Pseudo-Arguments)

Arguments that look valid but contain a logical or rhetorical flaw. Each can be assigned
as a **label** on an argument node, requiring a justification.

### 4.1 Formal Fallacies (structural errors)

| Fallacy | Description |
|---------|-------------|
| **Affirming the Consequent** | If P→Q; Q; therefore P (invalid) |
| **Denying the Antecedent** | If P→Q; not P; therefore not Q (invalid) |
| **Undistributed Middle** | All A are B; all C are B; therefore all C are A |
| **False Dilemma / False Dichotomy** | Presenting only two options when more exist |
| **Circular Reasoning** (Petitio Principii) | Conclusion is hidden in the premises |
| **Non Sequitur** | Conclusion doesn't follow from premises |

### 4.2 Informal Fallacies (content / context errors)

| Fallacy | Description |
|---------|-------------|
| **Ad Hominem** | Attacking the person instead of the argument |
| **Straw Man** | Distorting someone's argument to make it easier to attack |
| **Appeal to Authority** (illegitimate) | Citing a non-expert as authoritative evidence |
| **Appeal to Emotion** (Argumentum ad Passiones) | Substituting emotional reaction for evidence |
| **Appeal to Popularity** (Argumentum ad Populum) | "Most people believe X, so X is true" |
| **Appeal to Tradition** | "We've always done it this way" |
| **Appeal to Nature** | "It's natural, therefore good" |
| **Appeal to Ignorance** (Argumentum ad Ignorantiam) | "It hasn't been disproven, so it's true" |
| **Red Herring** | Introducing an irrelevant topic to divert attention |
| **Tu Quoque** (Whataboutism) | "You do it too, so my position is fine" |
| **Slippery Slope** | Assuming one step inevitably leads to extreme outcome |
| **False Equivalence** | Treating two fundamentally different things as equal |
| **False Cause** (Post Hoc / Cum Hoc) | Confusing correlation with causation |
| **Hasty Generalisation** | Drawing broad conclusions from insufficient data |
| **Cherry Picking** | Selecting only evidence that supports one's view |
| **Moving the Goalposts** | Changing the criteria after an argument has been met |
| **Equivocation** | Using a term with different meanings within the same argument |
| **Composition / Division** | What's true of parts must be true of the whole (or vice versa) |
| **Loaded Question** | Question that contains an unwarranted assumption |
| **Begging the Question** | Using the conclusion as a premise |
| **Genetic Fallacy** | Judging an argument by its origin, not its content |
| **Nirvana Fallacy** (Perfect Solution) | Rejecting a solution because it's not perfect |
| **Sunk Cost Fallacy** | Continuing because of past investment, not future value |
| **Bandwagon Fallacy** | "Everyone is doing it, so it must be right" |
| **Appeal to Pity** (Argumentum ad Misericordiam) | Using sympathy to win an argument |
| **Kafkatrap** | Denial of an accusation is used as proof of the accusation |
| **Motte-and-Bailey** | Retreating to a defensible claim when a bold one is challenged |
| **Thought-Terminating Cliché** | Using a phrase that shuts down critical thinking ("It is what it is") |

### 4.3 Argument Stoppers (Totschlag-Argumente)

Arguments so broad or emotional they shut down discussion rather than advance it:

| Type | Example |
|------|---------|
| **Moral Absolute** | "Human rights are non-negotiable" (true, but prevents nuance) |
| **Doomsday Claim** | "Society will collapse if we don't act now" |
| **Identity Shield** | "As a [group], I know better" (shuts out outside perspective) |
| **Legal Finality** | "It's the law" (ignores whether the law should change) |
| **Godwin's Law** | Comparing the opponent to Nazis |

---

## 5. Non-Argumentative Exit Moves

Not arguments at all — these are tactics to leave a losing discussion without conceding.

| Move | Description |
|------|-------------|
| **Rage Quit** | Leaving in anger, often with an insult |
| **Grammar Nazi** | Deflecting by criticising spelling / grammar instead of content |
| **Tone Policing** | "I won't engage until you calm down" (avoids the substance) |
| **Appeal to Boredom** | "This is getting boring / pointless" |
| **Sealioning** | Relentless, bad-faith demands for evidence to exhaust the opponent |
| **DARVO** | Deny, Attack, Reverse Victim and Offender |
| **Ghosting** | Simply disappearing from the discussion |
| **"Agree to Disagree"** (premature) | Ending debate before actual resolution when resolution is possible |
| **Virtue Signalling Exit** | Leaving with a moral declaration instead of addressing the point |
| **Concern Trolling** | Feigning sympathy to undermine ("I'm just worried about you…") |
| **Cope / Copium** | Rationalising a lost position to avoid admitting being wrong. A face-saving denial mechanism — the person constructs increasingly strained justifications rather than conceding. Passive variant of denial. |
| **Intimidation / Physical Coercion** | Raising voice, talking fast, invading personal space, or using threats of violence to suppress the opponent's argument through fear rather than logic |
| **Volume / Speed Dominance** | Talking louder or faster to prevent the opponent from responding. Not an argument — pure channel control. |

---

## 6. Meta-Discussion Strategies

Patterns that span multiple nodes or involve how a participant uses the discussion structure
itself (not the content). These are assignable as **multi-node patterns**.

| Strategy | Description |
|----------|-------------|
| **Gish Gallop** | Flooding with many weak arguments to overwhelm the opponent |
| **Creeping Relativisation** | Gradually softening a strong claim across multiple responses |
| **Motte-and-Bailey** | Bold claim (bailey) → retreat to safe claim (motte) when challenged |
| **Castle and Courtyard** (Burg und Vorhof) | Two linked arguments: one is the real position, the other is expendable |
| **Derailing** | Systematically steering the discussion away from the original topic |
| **Gaslighting** | Making the opponent doubt their own perception or memory |
| **Label Argumentation** | Applying a stigmatising label instead of engaging with content ("That's racist") |
| **Sea Lioning** | Politely but relentlessly demanding evidence in bad faith |
| **Steelmanning** | Strengthening the opponent's argument before responding (positive pattern!) |
| **Loop / Circular Discussion** | Discussion returns to a previously addressed point |
| **Scope Creep** | Gradually expanding the scope of the discussion to avoid the original question |
| **Whataboutism Chain** | Chaining Tu Quoque deflections across multiple exchanges |
| **Poisoning the Well** | Preemptively discrediting a source before it's even cited |
| **Double Standard** | Applying a principle to one side but not the other |
| **Taboo Derailing** | Deliberately or inadvertently touching a culturally taboo topic, triggering performative outrage that derails the discussion. The derailer may not intend to provoke — the topic itself acts as a proxy trigger with high statistical success rate. |
| **Performative Outrage** | Expressing exaggerated shock or offense to shut down a line of reasoning, especially near taboo topics. The outrage is strategic (conscious or unconscious) rather than genuine. |
| **Non-Rational Seduction** | Using charm, attractiveness, alcohol, flattery, or emotional manipulation to influence the opponent's position — bypassing rational argument entirely. |

Status: ⚠️ MultiNodePattern model exists, but detection / UI is not implemented.

---

## 7. Evidence Hierarchy

Evidence attached to an argument has a type and a quality tier. Higher tiers are harder
to dismiss; lower tiers require more supporting context.

| Tier | Quality | Type | Description |
|------|---------|------|-------------|
| **1.0** | Proof | `PROOF` | Mathematical / logical proof (undeniable within the axiomatic system) |
| **0.95** | Systematic Review | `META_ANALYSIS` | Meta-analysis or systematic review of multiple studies |
| **0.9** | Peer-Reviewed Study | `STUDY` | Peer-reviewed, published, reproducible |
| **0.85** | Official Statistic | `STATISTIC` | Government / institutional data (census, Eurostat, etc.) |
| **0.8** | Court Ruling / Legal Text | `LAW` | Legally binding precedent or statute |
| **0.7** | Expert Opinion | `EXPERT_OPINION` | Recognised expert in the relevant domain |
| **0.6** | Journalistic Investigation | `JOURNALISM` | Quality journalism with editorial standards |
| **0.5** | Survey / Poll | `SURVEY` | Self-reported data, susceptible to bias |
| **0.4** | Historical Precedent | `HISTORICAL` | Past event used as indicator (context-dependent) |
| **0.3** | Personal Experience | `ANECDOTE` | Individual case, not generalisable |
| **0.2** | Thought Experiment | `THOUGHT_EXPERIMENT` | Hypothetical scenario (no empirical data) |
| **0.1** | Hearsay / Rumour | `HEARSAY` | Unverifiable, second-hand information |
| **0.05** | Unfalsifiable Claim | `UNFALSIFIABLE` | Cannot be tested (treatable with philosophical razors, see §11) |
| **0.0** | Fabrication | `FABRICATION` | Known falsehood or deliberate disinformation |

### Source Credibility Factors (future — KI / community scored)

| Factor | Description |
|--------|-------------|
| Reputation | Scientific journal > blog > anonymous forum |
| Consistency | Does this source contradict itself elsewhere? |
| Track Record | Were previous claims by this source accurate? |
| Peer-Review Status | Has the work been independently reviewed? |
| Key Finding Reinterpretation | Does the communicator distort the study's actual findings? |
| Contradicting Studies | Are there reputable studies reaching opposite conclusions? |

---

## 8. Rule Systems (Normative Frameworks)

Arguments often implicitly appeal to one of these rule systems. Making the framework
explicit reveals why people talk past each other.

| Framework | Basis | Enforcement | Example |
|-----------|-------|-------------|---------|
| **Natural Law** (Naturgesetze) | Physics, biology, chemistry | Cannot be violated — only discovered | "Gravity exists regardless of legislation." |
| **Positive Law** (Festgeschriebene Gesetze) | Legislation, constitutions, treaties | State power (courts, police) | "Asylum is a legal right under GG Art. 16a." |
| **Social Norms** (Guter Geschmack) | Cultural consensus, etiquette | Social sanctions (shame, exclusion) | "It's considered rude to talk about salary." |
| **Moral Principles** | Ethical philosophy, religion | Conscience, community values | "It's wrong to let people drown at sea." |
| **Logical Axioms** | Mathematics, formal logic | Internal consistency | "A ∧ ¬A is a contradiction." |

---

## 9. Consensus-Finding Mechanisms

When a discussion must reach a resolution, different mechanisms are available.
The choice of mechanism is itself a meta-discussion.

| Mechanism | Basis | Strength | Weakness | Suitable when… |
|-----------|-------|----------|----------|----------------|
| **Popular Vote** (Populus) | Majority decides | Legitimacy through participation | Tyranny of majority; susceptible to manipulation | Large group, equal stakes |
| **Authority** (Meritocratic) | Expert knowledge / experience | Informed decision | Depends on trust in expert selection | Technical / specialised questions |
| **Trust-Based** (Vertrauen) | Personal credibility, reputation | Fast, low friction | Not scalable; in-group bias | Small groups, established relationships |
| **Legal / De Jure** | Statute, precedent | Predictable, enforceable | May be unjust; slow to change | Binding decisions, rights questions |
| **Factual / De Facto** | Empirical evidence | Objective (ideally) | Data can be incomplete or misinterpreted | Falsifiable factual claims |
| **Necessity / Random** | A decision must be made regardless | Breaks deadlocks | Not goal-directed | Urgency; truly indifferent options |
| **Individual Choice** | Each person decides for themselves | Respects autonomy | Not suitable for collective decisions | Personal matters without externalities |

### Embedding-Style Overview

```
                      ┌─────────────────────────────────────────────────┐
                      │           How do we resolve this?               │
                      └───────────┬─────────────────────┬───────────────┘
                 Collective       │                     │    Individual
            ┌─────────┼──────────┐│                     │
       Popular    Authority   Legal                  Personal
       Vote       (Expert)   (De Jure)               Choice
         │           │          │
      Majority   Expertise   Statute
      Polling    Consensus   Precedent
                 Trust
                                        Deadlock? → Necessity / Random
```

---

## 10. Moral Foundations

Based on Moral Foundations Theory (Haidt). Each argument can be tagged with one or more
foundations. Soft assignment: weights sum to 1.0 (e.g. 0.7 Care + 0.2 Fairness + 0.1 Authority).

| Foundation | Core Concern | Triggered by | Example in migration debate |
|------------|-------------|--------------|----------------------------|
| **Care / Harm** | Protecting the vulnerable | Suffering, cruelty | "Refugees are drowning in the Mediterranean" |
| **Fairness / Cheating** | Justice, reciprocity, proportionality | Free-riding, unequal treatment | "Migrants should contribute before receiving benefits" |
| **Loyalty / Betrayal** | In-group solidarity | Treason, disloyalty | "We should take care of our own people first" |
| **Authority / Subversion** | Respect for hierarchy and tradition | Lawlessness, disrespect | "We must follow immigration law" |
| **Sanctity / Degradation** | Purity, disgust, sacred values | Contamination, violation of the sacred | "Our culture is being eroded" |
| **Liberty / Oppression** | Autonomy, resistance to domination | Tyranny, coercion | "People should be free to live where they choose" |

### 10.1 Ethical Theories

Moral Foundations (above) describe **intuitions** — fast, gut-level moral reactions.
Ethical theories provide the **systematic frameworks** that justify or challenge those
intuitions. An argument's moral weight depends on which theory the arguer implicitly assumes.

| Theory | Core Principle | Decides by… | Example |
|--------|---------------|-------------|---------|
| **Utilitarianism** (Consequentialism) | Maximise overall well-being / happiness | Outcomes — the action that produces the most good for the most people | "Migration policy should be evaluated by net economic + social welfare impact" |
| **Deontology** (Kant) | Act only according to rules you could universalise | Rules — some actions are inherently right or wrong, regardless of outcome | "People have a right to asylum, period — consequences are irrelevant to the duty" |
| **Virtue Ethics** (Aristotle) | Cultivate virtuous character traits | Character — what would a virtuous person do? | "A compassionate society welcomes those in need" |
| **Contractualism** (Rawls) | Agree on principles behind a veil of ignorance | Fairness — what rules would you accept not knowing your position? | "If you didn't know whether you'd be born a refugee or a citizen, what policy would you want?" |
| **Care Ethics** (Gilligan) | Prioritise relationships and care for specific individuals | Responsibility — who is vulnerable and how do we respond? | "These are real people, not statistics — we have a personal responsibility" |
| **Pragmatism** | What works in practice? | Practical outcomes — avoid ideology, evaluate empirically | "Let's try a points-based system and measure the results after 5 years" |
| **Moral Relativism** | Morality is culturally constructed — no universal standard | Context — what is considered right in this culture/time? | "Western values shouldn't be imposed on other cultures" |
| **Natural Law Theory** | Morality is derived from nature / reason / divine order | Nature — some things are inherently right or wrong by nature | "Migration is natural — humans have always moved" |

> **System note:** Ethical theories can be tagged on moral-premise leaf nodes. When two
> arguers disagree at the leaf level, surfacing their differing ethical frameworks
> (e.g. utilitarian vs. deontological) makes the root cause of the disagreement visible.

### 10.2 Game Theory & Rational Choice

Some arguments implicitly assume rational actors making strategic decisions.
Game-theoretic concepts can be tagged as **logical axioms** — ground truths that
frame the argument's assumptions.

| Concept | Description | Relevance to argumentation |
|---------|-------------|---------------------------|
| **Nash Equilibrium** | A state where no player can improve their outcome by changing strategy unilaterally | "Both sides are locked in — neither will budge because any concession would be exploited" |
| **Pareto Efficiency** | A state where no one can be made better off without making someone else worse off | "This policy is Pareto-optimal — any change hurts someone" (can be used to block reform) |
| **Prisoner's Dilemma** | Individual rationality leads to collective irrationality | "If every country refuses refugees, everyone loses — but no single country wants to go first" |
| **Tragedy of the Commons** | Shared resources are overexploited when individuals act selfishly | "Without coordinated migration policy, every country free-rides on others' generosity" |
| **Zero-Sum Thinking** | Assuming one side's gain is the other's loss (often a fallacy) | "Migrants taking jobs" assumes a fixed number of jobs — which is empirically false |
| **Tit-for-Tat** | Cooperate first, then mirror the opponent's last move | Reciprocal trade agreements; "we'll accept your refugees if you accept ours" |
| **Dominant Strategy** | A strategy that is best regardless of what others do | "Investing in integration is a dominant strategy — it pays off whether migration increases or decreases" |
| **Rational Choice Theory** | Individuals maximise utility given constraints | Baseline assumption of most economic arguments — but humans are often irrational (see §10 Moral Foundations) |

> **System note:** Game-theoretic tags are useful when an argument assumes rational actors.
> When the assumption is violated (emotional decisions, bounded rationality), the tag
> `Zero-Sum Thinking` or `Bounded Rationality` can flag the mismatch.

---

## 11. Philosophical Razors

Heuristics for cutting through arguments. Can be applied by users or KI as labels
suggesting an argument should be simplified, dismissed, or reformulated.

| Razor | Principle | Application |
|-------|-----------|-------------|
| **Occam's Razor** | The simplest explanation is usually correct | Prefer simple arguments over convoluted ones |
| **Hanlon's Razor** | Don't attribute to malice what ignorance explains | De-escalation; default to incompetence over conspiracy |
| **Hitchens's Razor** | What is asserted without evidence can be dismissed without evidence | Shifts burden of proof to the claimant |
| **Sagan Standard** | Extraordinary claims require extraordinary evidence | Higher evidence bar for unusual claims |
| **Grice's Razor** | Don't interpret beyond what is explicitly said | Prevents over-reading implications |
| **Newton's Flaming Laser Sword** | What cannot be tested by experiment is not scientific | Separates empirical from metaphysical claims |
| **Alder's Razor** | If a claim cannot be settled by experiment, it's not worth debating (scientifically) | Related to above, more radical |
| **Popper's Falsifiability** | A theory is scientific only if falsifiable | Tests whether a claim can even be challenged |
| **Hume's Guillotine** | You cannot derive "ought" from "is" | Separates factual claims from moral demands |
| **Brandolini's Law** (Bullshit Asymmetry) | Refuting bullshit requires 10x the effort of producing it | Awareness tool; prioritise high-quality arguments |

---

## 12. Tag Categories

Tags are user-generated labels on argument nodes. They fall into several meta-categories:

### 12.1 Substantive Tags (inhaltlich)

| Category | Examples | Purpose |
|----------|----------|---------|
| **Domain / Topic Area** | `Wirtschaftlich`, `Juristisch`, `Moralisch`, `Ökologisch`, `Sozial` | Group arguments by subject |
| **Moral Foundation** | `Care`, `Fairness`, `Loyalty`, `Authority`, `Sanctity`, `Liberty` | Moral dimension (see §10) |
| **Normative vs. Positive** | `Feststellung`, `Wertvorstellung` | Statement type (see §15) |
| **Evidence Quality** | `fehlender Beleg`, `Studie vorhanden`, `Anekdote` | Quick evidence assessment |

### 12.2 Quality / Moderation Tags

| Category | Examples | Purpose |
|----------|----------|---------|
| **Fallacy** | `Ad Hominem`, `Strohmann`, `Slippery Slope` | Mark logical errors (see §4) |
| **Relevance** | `Off-Topic`, `Themaverfehlung`, `Scope-Verletzung`, `Spam` | Flag misplaced arguments |
| **Completeness** | `Inhaltslos`, `unvollständig`, `nur beschreibend` | Flag arguments without substance |
| **Manipulation** | `Gaslighting`, `Gish Gallop`, `Derailing` | Flag strategic deception (see §6) |

### 12.3 Meta-Argumentation Tags

| Category | Examples | Purpose |
|----------|----------|---------|
| **Argument Stopper** | `Totschlag-Argument`, `Killerphrase` | Marks discussion-ending moves |
| **Branching Trigger** | `Definitionsfrage`, `Scope-Verkleinerung`, `Metadiskussion` | Indicates a sub-discussion is needed |
| **Pattern** | `Burg und Vorhof`, `Creeping Relativisation` | Cross-node patterns (see §6) |

### 12.4 Community / Humour Tags (pr0gramm-style)

| Category | Examples | Purpose |
|----------|----------|---------|
| **Political Shorthand** | `Gutmensch`, `Bahnhofsklatscher`, `Wutbürger` | Community-assigned, votable |
| **Meme Tags** | `dies.`, `repost`, `old but gold` | Engagement, humour |
| **Sentiment** | `basiert`, `cringe`, `ehrenlos` | Quick crowd sentiment |

> **Design note:** Humour tags are expected to be the most actively used (pr0gramm insight).
> They serve as lightweight engagement signals and can feed into KI-based categorisation
> (e.g. `Gutmensch` → probable moral-values argument, Care foundation).

### 12.5 Tag Origins

Every tag has an origin that determines its authority and disputability:

| Origin | Authority | Votable? | Overridable by |
|--------|-----------|----------|----------------|
| **User-generated** | Low — crowd signal | Yes (pr0gramm-style) | Moderator, community consensus |
| **Moderator-assigned** | High — requires justification | No (but appealable) | Admin |
| **KI-generated** | Medium — suggested, needs confirmation | Yes | User correction, moderator override |

> **Design principle:** The data model is intentionally complex (three origin layers, soft
> scores, meta-categories). The **presentation** must reduce this to the simplest possible
> view. Tags are the primary UI surface — many are funny, some are meaningful, and the
> neural network should be able to learn from all of them.

### 12.6 Tag Disputability

If a user considers a tag incorrect or unfair, they can **open a discussion** about the
tag's appropriateness. This meta-discussion produces a verdict:
- Tag confirmed → stays, tagger gets positive reputation
- Tag overturned → removed, tagger gets neutral/negative reputation
- Tag refined → replaced with more accurate tag

### 12.7 Uncertainty Factor

Every score (acceptance, tag agreement, moral foundation weight) should carry an
**uncertainty factor** (0.0–1.0) reflecting how well-discussed the value is:
- 0.0 = no votes / discussion → score is unreliable
- 1.0 = extensively discussed → score is stable

This prevents weakly-voted scores from being treated as consensus.

---

## 13. Label Types (Quality / Moderation)

Labels differ from tags: they carry a **justification**, an **author role** (user vs. moderator),
and can trigger visibility changes (hiding arguments).

| Label Type | Trigger | Effect | Reversible? |
|------------|---------|--------|-------------|
| `FALLACY` | User/mod identifies logical error | Warning banner; votable | Yes (community vote) |
| `MISSING_EVIDENCE` | Claim without source | Marked "incomplete"; author notified | Yes (add source) |
| `OFF_TOPIC` | Argument outside topic scope | Hidden + suggested move to other topic | Yes (mod override) |
| `SPAM` | No argumentative content | Hidden; author reputation penalty | Yes (appeal) |
| `ANECDOTE` | Personal story as evidence | Quality warning; not hidden | No |
| `DUPLICATE` | Already covered by existing argument | Merged into ArgumentGroup | No (undo = ungroup) |
| `CONTENTLESS` | Descriptive without implication | Hidden; author notification | Yes (add implication) |
| `SCOPE_VIOLATION` | Correct content, wrong discussion | Moved; link remains | Yes |
| `MANIPULATION` | Strategic deception detected | Hidden pending review | Yes (community vote) |
| `INVALID` | Community consensus: argument is wrong | Hidden with reason | Yes (new evidence) |
| `MOVED` | Argument relocated to a different / new topic | Hidden in original; link to new location | No (structural) |

### Irrelevance Principle

Nothing is ever truly deleted. An argument that is hidden acquires an **irrelevance type**
explaining why it is no longer shown. The original data is preserved because any node could
become the basis for a new discussion.

| Irrelevance Type | Cause | Visible to |
|------------------|-------|------------|
| `VOTED_DOWN` | Community downvotes below threshold | Author, moderators |
| `MOD_HIDDEN` | Moderator action (spam, off-topic, etc.) | Moderators only |
| `MOVED` | Relocated to different topic | Everyone (as link) |
| `MERGED` | Absorbed into ArgumentGroup | Everyone (as sub-example) |
| `SUPERSEDED` | Replaced by stronger formulation | Author, moderators |
| `PENDING_REVIEW` | Flagged, awaiting community verdict | Author, moderators |

---

## 14. Rhetorical Devices & Question Types

Not all contributions are arguments. Some are rhetorical moves embedded in how a question
or statement is framed.

| Device | Description | Example |
|--------|-------------|---------|
| **Suggestive Question** | Question that implies its own answer | "Don't you think we've taken enough refugees?" |
| **Loaded Question** | Contains an unwarranted presupposition | "Why do migrants commit so much crime?" (presupposes they do) |
| **Rhetorical Question** | Not seeking an answer; making a point | "Are we really going to ignore human rights?" |
| **False Framing** | Presenting a situation in a misleading context | "Taxpayers are forced to fund migrants" (ignores that migrants also pay taxes) |
| **Euphemism** | Softening language to hide the reality | "Enhanced interrogation" instead of "torture" |
| **Dysphemism** | Harsh language to bias perception | "Flood of migrants" instead of "increase in migration" |
| **Dog Whistle** | Coded language understood by in-group | "Culturally incompatible" (coded xenophobia) |
| **Anchoring** | Setting an extreme reference point to make a moderate claim seem reasonable | "Some say deport everyone — I just want to reduce numbers a little" |
| **Weasel Words** | Vague attribution to unnamed authorities | "Studies say…", "Many people think…" |
| **Whataboutism** (as device) | Deflecting by pointing to another issue | "What about the homeless Germans?" |
| **Polemic** | Deliberately provocative, one-sided argumentation designed to attack rather than persuade. Uses sharp, emotionally charged language. | "Only an idiot would support open borders." |
| **Irony / Sarcasm** | Stating the opposite of what is meant, relying on context for the real message. Can be constructive (Socratic irony) or destructive (mockery). | "Oh sure, because banning things has always worked perfectly." |
| **Satire / Parody** | Exaggerating a position to absurdity to expose its flaws. Related to Reductio ad Absurdum but using humour rather than logic. | "Let's just ban everything that's unhealthy — starting with Mondays." |
| **Polarizing Vocabulary** | Using different emotionally charged words to describe the same concept, depending on political alignment. The word choice signals tribal affiliation and biases perception. | "Femizid" vs. "Ehrenmord"; "Freiheitskämpfer" vs. "Terrorist"; "Steuerlast" vs. "Solidarbeitrag" |

---

## 15. Statement Types: Positive vs. Normative

Every claim in a discussion is either a statement about what **is** (positive) or about
what **ought to be** (normative). Confusing the two is a common source of unresolvable conflict.

| Type | Definition | Testable? | Example |
|------|-----------|-----------|---------|
| **Positive** (Feststellung) | Factual claim about reality | Yes (empirically) | "Migration increased GDP by 1.2% last year." |
| **Normative** (Wertvorstellung) | Value judgement, moral claim | No (preference) | "We should accept more refugees." |

> **Hume's Guillotine:** You cannot derive an "ought" from an "is."
> The system should make the boundary between these layers visible.

Normative endpoints (moral premises) are **leaf nodes** in the argument tree — they cannot
be further justified, only accepted or rejected.

---

## 16. Authority Types

When someone cites "authority" to support a claim, the type of authority matters.

| Type | Basis | Legitimate when… | Illegitimate when… |
|------|-------|-------------------|---------------------|
| **Popular / Democratic** | Majority opinion, elections | Collective decisions with equal stakes | Used to determine factual truth |
| **Meritocratic / Expert** | Domain expertise, track record | Technical or scientific questions | Expert speaks outside their domain |
| **Trust-Based** | Personal relationship, reputation | Small-group coordination | Used to override evidence |
| **De Jure (Legal)** | Written law, precedent | Rights and obligations questions | Used as moral argument ("legal ≠ right") |
| **De Facto (Factual)** | Empirical evidence, measurements | Falsifiable empirical claims | Data is cherry-picked or fabricated |
| **Religious / Doctrinal** | Sacred text, religious tradition | Within a faith community | Applied to secular policy without consent |

---

## 17. Scope & Branching

Arguments can trigger structural changes to the discussion tree:

| Trigger | Action | Example |
|---------|--------|---------|
| **Scope too broad** | Split into sub-topics | "Migration" → "Labour migration" + "Asylum migration" |
| **Scope violation** | Move argument to different / new topic | "Universal morality" argument moved out of "Should Germany…" |
| **Definition Fork** | Same term, different meanings → split | "Racism" (systemic vs. individual) → two sub-branches |
| **Conflict detected** | Open sub-discussion | Factual vs. normative disagreement → separate both |
| **Meta-discussion needed** | Open meta-topic | "Is this even the right question?" |
| **Residual scope** | Enumerate unaddressed sub-topics | Splitting scope requires naming what's left |

### Branching Factor (Meta-Metric)

The **branching factor** of a question or argument measures whether it opens more conflicts
than it resolves. Tracking this reveals:
- Which topics are inherently divisive vs. convergent
- Which users tend to branch (open conflicts) vs. deduce (resolve them)
- Whether a discussion is making progress or spiralling

---

## 18. Thought Experiments, Analogies & Transferability

Thought experiments and analogies are powerful but fragile tools. They illustrate a moral
or logical principle, but always carry **side effects** — unintended implications that distort
the original point.

### The Clarity–Transferability Trade-off

| Dimension | Meaning |
|-----------|---------|
| **Clarity** | How clearly does the experiment isolate the concept? |
| **Transferability** | How well does the conclusion map back to the real-world situation? |

These two dimensions are in tension. The more extreme the thought experiment, the clearer the
concept — but the less transferable the conclusion.

```
Example: The Trolley Problem
  → Dozens of variants exist because small changes (fat man, surgeon, etc.)
    cause people to change their answer.
  → Each variant introduces different side effects (agency, proximity, intent).
  → The "best" variant minimises side effects while maximising the moral clarity
    of the concept under examination.
```

### Side Effects in Analogies

When someone draws an analogy ("Keeping animals is like slavery"), the system should support
marking:

| Assessment | Description |
|------------|-------------|
| **Valid parallel** | The structural similarity holds for the relevant dimension |
| **False equivalence** | The comparison equates fundamentally different things (→ §4.2) |
| **Side-effect distortion** | The analogy introduces moral/emotional baggage that doesn't exist in the original |
| **Scope mismatch** | The analogy applies at a different scale or context |

> **Open research question:** The transferability of moral reasoning across domains is
> under-explored. When is a moral principle from domain A applicable in domain B?
> Dialectree could contribute data here: if the same argument structure appears in
> multiple topics, the system can surface the structural parallel and let users evaluate
> whether the moral transfer holds.

---

## 19. Propaganda, Manufacturing Consent & Systemic Manipulation

Arguments at the level of **systemic power** rather than individual reasoning. These are not
necessarily fallacious — they may be factually correct — but they operate through mechanisms
that undermine free, informed decision-making.

### 19.1 Manipulation Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| **Manufacturing Consent** (Chomsky) | Systemic shaping of public opinion through media control | Selective coverage that makes one policy seem inevitable |
| **Overton Window Shifting** | Gradually normalising previously extreme positions | Extreme claim → public debate → moderate version becomes acceptable |
| **Astroturfing** | Fake grassroots support to simulate popular consensus | Paid social media campaigns posing as organic movements |
| **Firehose of Falsehood** | Flooding information space with contradictory claims to erode trust | State propaganda producing multiple conflicting narratives simultaneously |
| **Delayed Democracy** | Waiting until public opinion temporarily aligns before implementing a pre-decided policy | Polling until a favourable moment, then acting "democratically" |
| **Hypnotic / Emotional Conditioning** | Bypassing rational evaluation through repetition, fear, or group pressure | Repeated slogans, rally atmospheres, religious fervour |
| **Smear Campaign / Demonization** | Systematically destroying a person's or group's reputation to delegitimise their position, making the population consent to otherwise unacceptable actions | Bush administration's demonization of Saddam Hussein to build public consent for the Iraq War — shifting decision scope to the populace, then shaping their perception |
| **Scope Manipulation** | Redefining who gets to decide (or what they decide about) to engineer a favourable outcome | Reframing a geopolitical decision as a domestic security question to invoke popular fear |
| **Substance-Based Manipulation** | Using alcohol, drugs, or other substances to lower the opponent's rational defences in negotiation or discussion contexts | Business dinners with excessive alcohol to soften negotiation positions |

### 19.2 The Legitimacy Paradox

Accusing an institution of propaganda **itself** undermines trust — which can be either
a legitimate critique or a manipulation tactic:

| Scenario | Example | Assessment |
|----------|---------|------------|
| Legitimate media criticism | Exposing editorial bias with evidence | Valid argument |
| Delegitimisation tactic | "Lügenpresse" rhetoric to dismiss all unfavourable reporting | Propaganda itself |
| Structural critique | "Non-majority decisions passed under democratic label" | Valid if evidenced |

> **System challenge:** Dialectree assumes **free individuals making informed decisions**.
> Manufacturing Consent attacks this assumption at the meta-level. The system should allow
> marking arguments as potentially influenced by systemic manipulation — but this label
> must itself be disputable (see §12.6 Tag Disputability).

### 19.3 Intermediate Goals vs. Terminal Goals

A common manipulation pattern: an intermediate goal (means to an end) is gradually promoted
to a terminal goal (end in itself). The system should track the **goal hierarchy** of an
argument strand and flag when a means is being treated as an end.

```
Terminal goal:    "Citizens should be healthy."
Intermediate:    "We need a functioning healthcare system."
Means:           "We need migration to staff hospitals."

Manipulation:    "Migration" becomes the terminal goal,
                 detached from the original health argument.
```

---

## 20. Political Compass Mapping

Arguments can be mapped onto a two-dimensional political compass as a descriptive
(not prescriptive) tool. This is a **soft classification** — tags, not hard categories.

```
                   Authoritarian
                        │
                        │
            ┌───────────┼───────────┐
            │           │           │
   Left ────┼───────────┼───────────┼──── Right
            │           │           │
            └───────────┼───────────┘
                        │
                   Libertarian
```

| Axis | Left | Right |
|------|------|-------|
| **Economic** | State intervention, redistribution, public services | Free market, deregulation, private property |
| **Social** | Progressive, pluralist, cosmopolitan | Traditional, nationalist, culturally conservative |

| Axis | Authoritarian | Libertarian |
|------|---------------|-------------|
| **Governance** | Strong state, top-down control, regulation | Minimal state, individual autonomy, self-governance |

> **Design note:** Political compass mapping is inherently reductive. It is useful for
> visualisation and pattern detection (e.g. "this topic clusters in the auth-left quadrant")
> but should never replace the detailed moral foundation analysis (§10).
> Implementation: soft tag scores on two axes, each −1.0 to +1.0.

---

## 21. Meme Representation

Memes are visual shorthand for argumentative patterns. A single meme template can encode
a fallacy, a discussion dynamic, or an entire argument chain — often more effectively than
a paragraph of text. This makes them both an **engagement driver** (fun, shareable) and a
**classification tool** (instantly communicates a pattern).

### Why Memes Matter for Dialectree

| Insight | Explanation |
|---------|-------------|
| **pr0gramm effect** | Tags are one of pr0gramm's main assets because they're fun and creative. Memes have the same viral quality — users *want* to use them. |
| **Pattern compression** | A meme like "Patrick Star's Wallet" instantly encodes: airtight proof chain + opponent denial + cognitive dissonance. No label or tag captures that as efficiently. |
| **Cross-cultural recognition** | Meme templates are globally understood. A Spanish user and a German user both recognise "Expanding Brain" — no translation needed. |
| **KI training signal** | Meme assignments by users are high-quality labeled data for pattern detection models. |

### Concept Mapping (Overview)

Every meme template maps to one or more argumentative concepts from this taxonomy.
Selected examples:

| Meme | Argumentative Pattern | Reference |
|------|----------------------|-----------|
| **Patrick Star's Wallet** | Denial despite complete proof chain | §4.2 Argument from Incredulity |
| **Expanding Brain** | Reductio ad Absurdum (ironic escalation) | §2.1 Reductio |
| **Spider-Man Pointing** | Tu Quoque / Hypocrisy | §4.2 Tu Quoque |
| **Uno Reverse Card** | Counter-argument using opponent's own logic | §2.1 Modus Tollens |
| **Change My Mind** | Burden of Proof challenge | §2.5, §11 Hitchens's Razor |
| **Trolley Problem** | Ethical dilemma visualisation | §18 Thought Experiments |
| **NPC Meme** | Thought-terminating cliché | §4.2, §5 Exit Moves |
| **Clown Applying Makeup** | Self-defeating argument chain | §4.1 Circular Reasoning |
| **Anakin & Padmé ("Right?")** | Hidden implication revealed | §3 Anatomy (missing implication) |
| **It's a Trap!** | Loaded Question / Kafkatrap detected | §4.2, §14 |

> **Full catalog:** see [`docs/meme-catalog.md`](meme-catalog.md) for the complete
> meme-to-concept mapping with descriptions, all taxonomy references, and the
> implementation plan for meme sequence generation.

### Meme as Argument Visualisation

An argument chain can be rendered as a meme sequence:

```
Argument:  Claim → Reason → Example → Implication → Opponent denies conclusion
Meme:      Patrick Star's Wallet (4 panels)

Panel 1:  "Is this your labour shortage?"    — "Yes"
Panel 2:  "And healthcare needs workers?"    — "Yes"
Panel 3:  "And migrants fill those jobs?"    — "Yes"
Panel 4:  "So migration is important?"       — "No"
```

This is a future KI feature (see implementation plan, Phase 2).

---

## 22. Strategic Frameworks (Reference)

Entire bodies of strategic thought that inform how arguments are deployed. These are not
individual fallacies or tactics — they are **frameworks** that generate tactics. Dialectree
can reference them as context when a user's behaviour matches a known pattern.

| Framework | Origin | Core Idea | Relevance |
|-----------|--------|-----------|-----------|
| **36 Stratagems** | Chinese military/political tradition | 36 named strategies for conflict, deception, and negotiation | Many stratagems map directly to discussion tactics (e.g. "Kill with a borrowed knife" ≈ Label Argumentation; "Loot a burning house" ≈ exploiting a weakened opponent) |
| **Sun Tzu: Art of War** | Chinese military philosophy | "The supreme art of war is to subdue the enemy without fighting" | Framing, positioning, and information asymmetry as weapons — directly applicable to propaganda (§19) and meta-strategies (§6) |
| **Schopenhauer: The Art of Being Right** (Eristische Dialektik) | 19th century philosophy | 38 stratagems for winning arguments regardless of truth | The canonical reference for dishonest argumentation — many fallacies in §4 correspond to Schopenhauer's stratagems |
| **Machiavelli: The Prince** | Renaissance political philosophy | Power maintenance through pragmatism over morality | "The end justifies the means" — framework for evaluating whether manipulation (§19) is legitimate |
| **Robert Greene: 48 Laws of Power** | Modern popular strategy | Distilled power dynamics from historical examples | Maps to social manipulation patterns, reputation management, and strategic concession |

> **System note:** These frameworks are listed as references, not as tag categories.
> Individual tactics derived from them are tagged using existing taxonomy categories
> (§4 Fallacies, §5 Exit Moves, §6 Meta-Strategies, §19 Propaganda).
> A future feature could link tagged tactics back to their framework of origin.

---

## Appendix: Implementation Status

| Section | Enum / Model | Status |
|---------|-------------|--------|
| §1 Position | `PositionEnum` | ✅ |
| §2 Argument Types | — | ❌ (tag-based, no enum yet) |
| §3 Argument Anatomy | `ArgumentNode.claim/reason/example/implication` | ✅ |
| §4 Fallacies | `LabelTypeEnum.FALLACY` | ⚠️ (label exists, no fallacy sub-types) |
| §5 Exit Moves | — | ❌ (tag-based when needed) |
| §6 Meta-Discussion Strategies | `MultiNodePattern` | ⚠️ (model exists, no detection) |
| §7 Evidence Hierarchy | `EvidenceTypeEnum` (14 types) + `EVIDENCE_DEFAULT_QUALITY` | ✅ |
| §8 Rule Systems | — | ❌ (tag-based when needed) |
| §9 Consensus Mechanisms | — | ❌ |
| §10 Moral Foundations | `Tag.moral_foundation` | ⚠️ (field exists, soft assignment missing) |
| §10.1 Ethical Theories | — | ❌ (tag-based when needed) |
| §10.2 Game Theory & Rational Choice | — | ❌ (tag-based when needed) |
| §11 Philosophical Razors | — | ❌ (label-based when needed) |
| §12 Tag Categories | `Tag`, `ArgumentNodeTag` | ⚠️ (flat tags exist, no meta-categories) |
| §12.5 Tag Origins | — | ❌ (no origin tracking yet) |
| §12.6 Tag Disputability | — | ❌ |
| §12.7 Uncertainty Factor | — | ❌ |
| §13 Label Types | `LabelTypeEnum` (12 types) + `confirmed` field | ✅ |
| §13 Irrelevance Types | `Visibility` enum (6 types) + `hidden_reason` | ✅ |
| §14 Rhetorical Devices | — | ❌ (tag-based when needed) |
| §15 Positive vs. Normative | `StatementType` enum + `statement_type` field | ✅ |
| §16 Authority Types | — | ❌ |
| §17 Scope & Branching | `DefinitionFork` | ⚠️ (model exists, scope logic missing) |
| §18 Thought Experiments & Transferability | — | ❌ |
| §19 Propaganda & Systemic Manipulation | — | ❌ |
| §20 Political Compass Mapping | — | ❌ |
| §21 Meme Representation | — | ❌ (catalog in `docs/meme-catalog.md`) |
| §22 Strategic Frameworks | — | ❌ (reference only, no model needed) |







