"""
Seed script: Creates two example topics for the Zigzag view:
  1. "Sind Quotenregelungen rassistisch?" (Quotenrassismus – full zigzag discussion)
  2. "Blueprint: Optimale Diskussionsführung" (ideal discussion pattern with branching)

Usage:  python -m app.seed
"""
from pathlib import Path

from .database import engine, SessionLocal, Base
from .models import (
    User, Topic, ArgumentNode, ArgumentGroup, Vote, Tag, Comment,
    Evidence, NodeLabel, Position, EvidenceType, LabelType, MoralFoundation,
    StatementType, Visibility, TagCategory, TagOrigin, ArgumentNodeTag,
    ConflictZone, EdgeType,
)

_DATA_DIR = Path(__file__).parent / "data"


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # ── Users ──────────────────────────────────────────────────────
    alice = User(username="alice", email="alice@example.com", password_hash="TODO")
    bob = User(username="bob", email="bob@example.com", password_hash="TODO")
    charlie = User(username="charlie", email="charlie@example.com", password_hash="TODO")
    db.add_all([alice, bob, charlie])
    db.flush()

    # ══════════════════════════════════════════════════════════════════
    #  TOPIC 1: Quotenrassismus – Zigzag-Dialog aus Transkript
    #
    #  Struktur folgt direkt aus quoten_diskussion.md:
    #    Stage 1: R1 → L2 → R3 → L4  (ein Node pro Turn)
    #    Stage 2: Splits der Turns (2.1/2.2, 3.1/3.2, L4×3)
    #
    #  R = Rechts / NEIN zu Quoten (CONTRA)
    #  L = Links  / JA  zu Quoten (PRO)
    # ══════════════════════════════════════════════════════════════════

    # Load Stage-0 transcript (Markdown) for Topic 1
    _md_path = _DATA_DIR / "quoten_diskussion.md"
    _topic1_transcript = _md_path.read_text(encoding="utf-8") if _md_path.exists() else None

    topic1 = Topic(
        title="Sollte es Quoten für Minderheiten geben?",
        description="Quotenregelungen sollen historische Benachteiligung ausgleichen — "
                    "doch sind sie selbst eine Form von Rassismus?",
        transcript_yaml=_topic1_transcript,
        created_by=alice.id,
    )
    db.add(topic1)
    db.flush()

    # ── Stage 1: Basis-Argumente (stage_added=1) ──────────────────
    # Raw transcript only — one node per turn, no analytical labels.
    # R1 eröffnet, L2 antwortet, R3 widerspricht, L4 erwidert.

    r1 = ArgumentNode(
        topic_id=topic1.id,
        title="R1",
        description="Quotenregelungen sind rassistisch gegenüber Weißen und schlecht.",
        position=Position.CONTRA, created_by=bob.id,
        conflict_zone=ConflictZone.VALUE,
        stage_added=1,
    )
    db.add(r1)
    db.flush()

    l2 = ArgumentNode(
        topic_id=topic1.id, parent_id=r1.id,
        title="L2",
        description="Rassismus gegen Weiße gibt es nicht. "
                    "Quoten sollen die Unterrepräsentation durch strukturelle "
                    "Diskriminierung von Gruppen ausgleichen.",
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.VALUE,
        stage_added=1,
    )
    db.add(l2)
    db.flush()

    r3 = ArgumentNode(
        topic_id=topic1.id, parent_id=l2.id,
        title="R3",
        description="Doch, Rassismus gegen Weiße gibt es. "
                    "Die Unterschiede sind erklärbar durch Kultur- und IQ-Unterschiede.",
        position=Position.CONTRA, created_by=bob.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=1,
    )
    db.add(r3)
    db.flush()

    l4 = ArgumentNode(
        topic_id=topic1.id, parent_id=r3.id,
        title="L4",
        description="Das ist Rassismus. "
                    "IQ hat keine Bedeutung für den Erfolg. "
                    "IQ ist nicht angeboren — Unterschiede folgen aus struktureller Diskriminierung.",
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.FACT,
        opens_conflict="Relevance of IQ",
        stage_added=1,
    )
    db.add(l4)
    db.flush()

    # ── Stage 2: Splits (stage_added=2) ───────────────────────────
    # L2 → (2.1) und (2.2): parent=r1 (gleicher Gegner wie L2)
    l2_1 = ArgumentNode(
        topic_id=topic1.id, parent_id=r1.id, split_from_id=l2.id,
        title="(2.1) Rassismus gegen Weiße gibt es nicht",
        description=None,
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    l2_2 = ArgumentNode(
        topic_id=topic1.id, parent_id=r1.id, split_from_id=l2.id,
        title="(2.2) Quoten korrigieren Unterrepräsentation durch strukturelle Diskriminierung",
        description="Minderheiten sind historisch benachteiligt. "
                    "Quoten sind Korrekturmechanismus, kein Angriff auf andere Gruppen.",
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.VALUE,
        stage_added=2,
    )
    db.add_all([l2_1, l2_2])
    db.flush()

    # R3 → (3.1) und (3.2): parent zeigt auf spezifischen L2-Split
    #   (3.1) ↩ 2.1 — antwortet auf L2.1
    #   (3.2) ↩ 2.2 — antwortet auf L2.2
    r3_1 = ArgumentNode(
        topic_id=topic1.id, parent_id=l2_1.id, split_from_id=r3.id,
        title="(3.1) ↩ 2.1: Doch, Rassismus gegen Weiße gibt es",
        description="Jede Ungleichbehandlung aufgrund von Ethnie ist Rassismus — "
                    "unabhängig von Machtstrukturen.",
        position=Position.CONTRA, created_by=bob.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    r3_2 = ArgumentNode(
        topic_id=topic1.id, parent_id=l2_2.id, split_from_id=r3.id,
        title="(3.2) ↩ 2.2: Unterschiede erklärbar durch Kultur- und IQ-Unterschiede",
        description="Gruppenunterschiede haben kulturelle und biologische Ursachen — "
                    "nicht allein strukturelle Diskriminierung.",
        position=Position.CONTRA, created_by=bob.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    db.add_all([r3_1, r3_2])
    db.flush()

    # L4 → drei Sub-Argumente: parent=r3_2 (alle L4-Splits antworten auf 3.2)
    # (3.1 ist ein dead-end — kein L4-Argument antwortet darauf)
    l4_1 = ArgumentNode(
        topic_id=topic1.id, parent_id=r3_2.id, split_from_id=l4.id,
        title="(4.1) ↩ 3.2: Das ist Rassismus",
        description="Gruppenunterschiede mit IQ zu erklären reproduziert rassistische Denkmuster.",
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.VALUE,
        stage_added=2,
    )
    l4_2 = ArgumentNode(
        topic_id=topic1.id, parent_id=r3_2.id, split_from_id=l4.id,
        title="(4.2) ↩ 3.2: IQ hat keine Bedeutung für den Erfolg",
        description="Beruflicher Erfolg wird durch soziale Netzwerke, Kapital und Chancen bestimmt — nicht durch IQ.",
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    l4_3 = ArgumentNode(
        topic_id=topic1.id, parent_id=r3_2.id, split_from_id=l4.id,
        title="(4.3) ↩ 3.2: IQ ist nicht angeboren — Unterschiede folgen aus struktureller Diskriminierung",
        description="IQ-Gruppenunterschiede verschwinden bei gleichen Bildungs- und Lebensbedingungen.",
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    db.add_all([l4_1, l4_2, l4_3])
    db.flush()

    # ── Tags ──────────────────────────────────────────────────────
    tag_justice = Tag(name="Gerechtigkeit & Teilhabe", category=TagCategory.SOCIETAL_GOAL)
    tag_freedom = Tag(name="Freiheit & Selbstbestimmung", category=TagCategory.SOCIETAL_GOAL)
    tag_equality = Tag(name="Gleichberechtigung", category=TagCategory.DOMAIN)
    tag_sociology = Tag(name="Soziologie", category=TagCategory.DOMAIN)
    tag_fairness = Tag(name="Fairness", moral_foundation=MoralFoundation.FAIRNESS,
                       category=TagCategory.MORAL_FOUNDATION)
    tag_care = Tag(name="Fürsorge", moral_foundation=MoralFoundation.CARE,
                   category=TagCategory.MORAL_FOUNDATION)
    db.add_all([tag_justice, tag_freedom, tag_equality, tag_sociology, tag_fairness, tag_care])
    db.flush()

    db.add_all([
        ArgumentNodeTag(argument_node_id=r1.id, tag_id=tag_freedom.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=l2.id, tag_id=tag_justice.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=l2.id, tag_id=tag_equality.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=r3_2.id, tag_id=tag_sociology.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=l4.id, tag_id=tag_fairness.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=l4_3.id, tag_id=tag_care.id, origin=TagOrigin.AI),
    ])

    # ── Votes ─────────────────────────────────────────────────────
    db.add_all([
        Vote(user_id=alice.id, argument_node_id=r1.id, value=-1),
        Vote(user_id=bob.id, argument_node_id=r1.id, value=1),
        Vote(user_id=alice.id, argument_node_id=l2.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=l2.id, value=1),
        Vote(user_id=bob.id, argument_node_id=r3_2.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=r3_2.id, value=-1),
        Vote(user_id=alice.id, argument_node_id=l4.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=l4_3.id, value=1),
    ])

    # ── Comments ──────────────────────────────────────────────────
    db.add_all([
        Comment(argument_node_id=r1.id, user_id=alice.id,
                text="Eröffnungsthese ohne Belege — typischer Gesprächseinstieg."),
        Comment(argument_node_id=l2.id, user_id=bob.id,
                text="(2.1) setzt die akademische Definition als gegeben voraus. Das ist umstritten."),
        Comment(argument_node_id=r3_2.id, user_id=charlie.id,
                text="Das IQ-Argument öffnet einen klassischen Sub-Streitpunkt "
                     "— und verschiebt die Beweislast auf L."),
        Comment(argument_node_id=l4.id, user_id=bob.id,
                text="L4 antwortet als Block auf den Sub-Streitpunkt aus R3.2."),
    ])

    # ── Labels ────────────────────────────────────────────────────
    db.add(NodeLabel(
        argument_node_id=l2_1.id,
        label_type=LabelType.FALLACY,
        justification="No-True-Scotsman: Die akademische Rassismus-Definition wird so gewählt, "
                      "dass Weiße per Definition keine Opfer sein können.",
        created_by=bob.id,
    ))

    # ══════════════════════════════════════════════════════════════════
    #  TOPIC 2: Blueprint – Quotenrassismus als 5-Stufen-Beispiel
    #
    #  Kanonisches Beispiel mit Argumentbezeichnungen immer am Anfang.
    #  stage_added=1: Basis-Argumente (ein Node pro Turn)
    #  stage_added=2: Split-Derivate (Aufspaltung eines Turns)
    #  split_from_id: Referenz auf das Basis-Argument aus Stufe 1
    # ══════════════════════════════════════════════════════════════════

    # Load transcript YAML from file for Stage 0
    _yaml_path = _DATA_DIR / "quoten_blueprint.yaml"
    transcript_yaml_content = _yaml_path.read_text(encoding="utf-8") if _yaml_path.exists() else None

    topic2 = Topic(
        title="🔧 Blueprint: Quotenrassismus-Diskussion",
        description="Idealtypisches Diskussionsmuster am Beispiel der Quoten-Debatte — "
                    "demonstriert alle 5 Verfeinerungsstufen des Zickzack-Modells.",
        transcript_yaml=transcript_yaml_content,
        created_by=charlie.id,
    )
    db.add(topic2)
    db.flush()

    # ── STUFE 1: Basis-Argumente (stage_added=1) ──────────────────
    # Raw transcript only — one argument per turn, no analytical labels.
    # The red thread is implicit via parent_id chain: b1 → a1 → a2 → a3 → a4 → a5

    b1 = ArgumentNode(
        topic_id=topic2.id,
        title="B₁: Quotenregelungen sind Diskriminierung",
        description="Ungleichbehandlung nach Ethnie ist per Definition Diskriminierung.",
        position=Position.PRO, created_by=bob.id,
        statement_type=StatementType.NORMATIVE,
        conflict_zone=ConflictZone.VALUE,
        claim="Quotenregelungen diskriminieren nach Herkunft.",
        reason="Art. 3 GG verbietet Ungleichbehandlung aufgrund von Abstammung.",
        example="Bei Harvard brauchen asiatische Bewerber höhere Scores.",
        implication="Quoten müssen abgeschafft werden.",
        stage_added=1,
    )
    db.add(b1)
    db.flush()

    a1 = ArgumentNode(
        topic_id=topic2.id, parent_id=b1.id,
        title="A₁: Strukturelle Benachteiligung erfordert aktive Korrektur",
        description="Formale Gleichheit reicht nicht, wenn Startbedingungen ungleich sind.",
        position=Position.CONTRA, created_by=alice.id,
        statement_type=StatementType.NORMATIVE,
        conflict_zone=ConflictZone.VALUE,
        claim="Ohne aktive Maßnahmen perpetuiert sich strukturelle Ungleichheit.",
        reason="Jahrhundertelange Diskriminierung hat Ungleichheiten geschaffen.",
        implication="Temporäre Korrekturmaßnahmen sind ethisch geboten.",
        stage_added=1,
    )
    db.add(a1)
    db.flush()

    a2 = ArgumentNode(
        topic_id=topic2.id, parent_id=a1.id,
        title="A₂: Konsens — Diskriminierung ist schlecht, Methode ist umstritten",
        description="Beide Seiten stimmen überein: Diskriminierung ist abzulehnen. "
                    "Der Dissens liegt bei der Methode, nicht beim Ziel.",
        position=Position.NEUTRAL, created_by=charlie.id,
        statement_type=StatementType.MIXED,
        conflict_zone=ConflictZone.VALUE,
        edge_type=EdgeType.CONCESSION,
        claim="Konsens-Felder explizit benennen.",
        stage_added=1,
    )
    db.add(a2)
    db.flush()

    a3 = ArgumentNode(
        topic_id=topic2.id, parent_id=a2.id,
        title="A₃: Was IST überhaupt Rassismus? — Definitionsebene klären",
        description="Die Verbindung zwischen 'Korrektur' und 'kein Rassismus' setzt "
                    "eine umstrittene Definition voraus.",
        position=Position.PRO, created_by=bob.id,
        conflict_zone=ConflictZone.FACT, edge_type=EdgeType.COMMUNITY_NOTE,
        is_edge_attack=True,
        opens_conflict="Was ist die korrekte Definition von Rassismus?",
        stage_added=1,
    )
    db.add(a3)
    db.flush()

    # A₄: Basis-Node für den Definitionskonflikt (stage 1)
    # In Stufe 2 wird dieser Node in A₄a, A₄b, A₄c aufgespalten.
    a4 = ArgumentNode(
        topic_id=topic2.id, parent_id=a3.id,
        title="A₄: Definitionskonflikt — mehrere Positionen zur Rassismus-Definition",
        description="Verschiedene Positionen existieren nebeneinander: "
                    "akademisch vs. alltagssprachlich vs. kontextuell.",
        position=Position.NEUTRAL, created_by=charlie.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=1,
    )
    db.add(a4)
    db.flush()

    a5 = ArgumentNode(
        topic_id=topic2.id, parent_id=a4.id,
        title="A₅: Bad Faith — Definitionsverschiebung als Totschlagargument",
        description="Wenn die Definition so gewählt wird, dass das Gegenüber per Definition "
                    "nicht Recht haben KANN, ist das kein faires Argument.",
        position=Position.PRO, created_by=bob.id,
        statement_type=StatementType.NORMATIVE,
        conflict_zone=ConflictZone.VALUE,
        edge_type=EdgeType.CONSEQUENCES,
        is_edge_attack=True,
        stage_added=1,
    )
    db.add(a5)
    db.flush()

    # ── STUFE 2: Split-Derivate (stage_added=2) ───────────────────
    # Jeder Turn wird aufgedröselt. Split-Nodes referenzieren:
    #   - parent_id: denselben Parent wie ihr Basis-Node (der Gegner)
    #   - split_from_id: das Basis-Argument aus Stufe 1

    # Splits von B₁ (parent=None, gleicher parent wie B₁)
    b1_alt1 = ArgumentNode(
        topic_id=topic2.id, parent_id=None,
        split_from_id=b1.id,
        title="B₁a: Leistungsprinzip über alles",
        description="Fokus auf Meritokratie statt auf Rassismus-Begriff.",
        position=Position.PRO, created_by=bob.id,
        conflict_zone=ConflictZone.CAUSAL,
        stage_added=2,
    )
    b1_alt2 = ArgumentNode(
        topic_id=topic2.id, parent_id=None,
        split_from_id=b1.id,
        title="B₁b: Individuelle Rechte vs. Gruppenidentität",
        description="Philosophischer Rahmen: Liberalismus vs. Identitätspolitik.",
        position=Position.PRO, created_by=bob.id,
        conflict_zone=ConflictZone.VALUE,
        stage_added=2,
    )
    db.add_all([b1_alt1, b1_alt2])
    db.flush()

    # Split von A₁ (parent=B₁, gleicher parent wie A₁)
    a1_alt1 = ArgumentNode(
        topic_id=topic2.id, parent_id=b1.id,
        split_from_id=a1.id,
        title="A₁a: Diverse Teams liefern bessere Ergebnisse",
        description="Pragmatisch-ökonomisches Argument: McKinsey-Studien zeigen Innovationsvorteile.",
        position=Position.CONTRA, created_by=alice.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    db.add(a1_alt1)
    db.flush()

    # Splits von A₄ (parent=A₃, gleicher parent wie A₄)
    a4a = ArgumentNode(
        topic_id=topic2.id, parent_id=a3.id,
        split_from_id=a4.id,
        title="A₄a: Akademische Definition: Rassismus = Vorurteil + Macht",
        description="Institutionelle Macht ist konstitutiv für Rassismus. "
                    "Ohne Machtstrukturen ist es 'nur' Diskriminierung.",
        position=Position.CONTRA, created_by=alice.id,
        conflict_zone=ConflictZone.FACT, edge_type=EdgeType.REFRAME,
        stage_added=2,
    )
    a4b = ArgumentNode(
        topic_id=topic2.id, parent_id=a3.id,
        split_from_id=a4.id,
        title="A₄b: Alltagsdefinition: Jede Ungleichbehandlung nach Ethnie = Rassismus",
        description="Die meisten Menschen verstehen unter Rassismus jede "
                    "ethnisch motivierte Ungleichbehandlung, unabhängig von Macht.",
        position=Position.PRO, created_by=bob.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    a4c = ArgumentNode(
        topic_id=topic2.id, parent_id=a3.id,
        split_from_id=a4.id,
        title="A₄c: Beide Definitionen haben Berechtigung — kontextabhängig",
        description="Die Definition hängt vom Kontext ab: Im Recht die enge, "
                    "in der Soziologie die weite Definition.",
        position=Position.NEUTRAL, created_by=charlie.id,
        conflict_zone=ConflictZone.FACT, edge_type=EdgeType.CONCESSION,
        stage_added=2,
    )
    db.add_all([a4a, a4b, a4c])
    db.flush()

    # ── Votes for Blueprint ───────────────────────────────────────
    db.add_all([
        Vote(user_id=bob.id, argument_node_id=b1.id, value=1),
        Vote(user_id=alice.id, argument_node_id=b1.id, value=-1),
        Vote(user_id=alice.id, argument_node_id=a1.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=a1.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=a2.id, value=1),
        Vote(user_id=bob.id, argument_node_id=a3.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=a4.id, value=1),
        Vote(user_id=alice.id, argument_node_id=a4a.id, value=1),
        Vote(user_id=bob.id, argument_node_id=a4b.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=a4c.id, value=1),
        Vote(user_id=bob.id, argument_node_id=a5.id, value=1),
    ])

    # ── Comments for Blueprint ────────────────────────────────────
    db.add_all([
        Comment(argument_node_id=b1.id, user_id=charlie.id,
                text="Starke Eröffnung — direkt auf den Punkt."),
        Comment(argument_node_id=a1.id, user_id=bob.id,
                text="Fairer Gegenangriff. Steelmanning zeigt Respekt."),
        Comment(argument_node_id=a3.id, user_id=alice.id,
                text="Hier wird die Verbindung angegriffen, nicht der Inhalt — "
                     "das ist ein Edge Attack (undercutting defeater)."),
        Comment(argument_node_id=a5.id, user_id=charlie.id,
                text="Wichtig: Bad Faith muss benannt werden, sonst dreht man sich im Kreis."),
    ])

    # ── Labels for Blueprint ──────────────────────────────────────
    db.add(NodeLabel(
        argument_node_id=a4a.id,
        label_type=LabelType.FALLACY,
        justification="No-True-Scotsman: Die Definition wird so gewählt, "
                       "dass Gegenbeispiele per Definition ausgeschlossen werden.",
        created_by=bob.id,
    ))

    # ── Evidence for Blueprint ────────────────────────────────────
    db.add(Evidence(
        argument_node_id=a1_alt1.id,
        evidence_type=EvidenceType.STUDY,
        title="McKinsey: Diversity Wins (2020)",
        url="https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/diversity-wins-how-inclusion-matters",
        quality_score=0.85,
        created_by=alice.id,
    ))

    # ══════════════════════════════════════════════════════════════════
    #  TOPIC 3: Migration – "Deutschland sollte mehr Migranten aufnehmen"
    #
    #  Demonstriert das volle Phase-0-Feature-Set:
    #   - Argument-Anatomie (claim/reason/example/implication) auf allen Nodes
    #   - statement_type (POSITIVE / NORMATIVE) auf jedem Argument
    #   - Tags mit verschiedenen Kategorien und Ursprüngen (USER/AI/MODERATOR)
    #   - Evidence: STUDY, LAW, ANECDOTE, EXPERT_OPINION
    #   - Labels: FALLACY, MISSING_EVIDENCE, OFF_TOPIC
    #   - Ein Argument versteckt (visibility=VOTED_DOWN)
    #   - Ein ArgumentGroup (wirtschaftliche Argumente gebündelt)
    # ══════════════════════════════════════════════════════════════════

    topic3 = Topic(
        title="Deutschland sollte mehr Migranten aufnehmen",
        description="Soll Deutschland die Zuwanderung erhöhen? "
                    "Wirtschaftliche, humanitäre und gesellschaftliche Argumente im Vergleich.",
        created_by=alice.id,
    )
    db.add(topic3)
    db.flush()

    # ArgumentGroup: wirtschaftliche Argumente gebündelt
    eco_group = ArgumentGroup(
        topic_id=topic3.id,
        canonical_title="Wirtschaftliche Argumente",
        description="Argumente rund um den wirtschaftlichen Effekt von Migration "
                    "(Fachkräftemangel, Lohndruck, Sozialleistungen, BIP).",
    )
    db.add(eco_group)
    db.flush()

    # ── PRO 1: Fachkräftemangel ───────────────────────────────────
    m_pro1 = ArgumentNode(
        topic_id=topic3.id,
        title="Fachkräftemangel – Deutschland braucht qualifizierte Zuwanderung",
        description="Ohne Zuwanderung schrumpft die Erwerbsbevölkerung. "
                    "Der Fachkräftemangel kostet Wachstum und gefährdet die Sozialsysteme.",
        position=Position.PRO,
        statement_type=StatementType.POSITIVE,
        claim="Deutschland hat einen strukturellen Fachkräftemangel, der ohne Zuwanderung nicht lösbar ist.",
        reason="Die Bevölkerung altert; bis 2035 fehlen laut Bundesagentur für Arbeit über 7 Millionen Arbeitskräfte.",
        example="Pflegebranche, IT-Sektor und Handwerk sind bereits heute kaum besetzbar.",
        implication="Gezielte Zuwanderung von Fachkräften ist wirtschaftlich notwendig.",
        argument_group_id=eco_group.id,
        created_by=alice.id,
    )
    db.add(m_pro1)
    db.flush()

    # ── PRO 2: Humanitäre Pflicht / Asylrecht ────────────────────
    m_pro2 = ArgumentNode(
        topic_id=topic3.id, parent_id=m_pro1.id,
        title="Asylrecht – Deutschland hat eine humanitäre Aufnahmepflicht",
        description="Art. 16a GG garantiert das Recht auf Asyl. "
                    "Flucht vor Krieg und Verfolgung begründet eine Aufnahmepflicht.",
        position=Position.PRO,
        statement_type=StatementType.NORMATIVE,
        claim="Deutschland hat eine rechtliche und moralische Pflicht, schutzbedürftige Menschen aufzunehmen.",
        reason="Art. 16a GG und die Genfer Flüchtlingskonvention begründen diese Pflicht völkerrechtlich.",
        example="2015/16 wurden über 1 Mio. Schutzsuchende aufgenommen — die Gesellschaft hat funktioniert.",
        implication="Abschottungspolitik verstößt gegen Völkerrecht und Grundgesetz.",
        created_by=alice.id,
    )
    db.add(m_pro2)
    db.flush()

    # ── CONTRA 1: Lohndruck im Niedriglohnsektor ──────────────────
    m_con1 = ArgumentNode(
        topic_id=topic3.id, parent_id=m_pro1.id,
        title="Zuwanderung erhöht Konkurrenz und Lohndruck im Niedriglohnsektor",
        description="Mehr Arbeitskräfte drücken Löhne im Niedriglohnbereich "
                    "und verdrängen einheimische Geringverdiener.",
        position=Position.CONTRA,
        statement_type=StatementType.POSITIVE,
        claim="Massenhafte Zuwanderung schadet Geringverdienern durch sinkende Löhne.",
        reason="Angebot und Nachfrage: Mehr Arbeitskräfte → niedrigere Löhne im Wettbewerbssegment.",
        example="Im Baugewerbe sind Reallöhne seit den 1990ern gesunken, parallel zur Zuwanderung aus Osteuropa.",
        implication="Zuwanderung sollte auf nachgewiesenen Qualifikationsbedarf beschränkt werden.",
        argument_group_id=eco_group.id,
        created_by=bob.id,
    )
    db.add(m_con1)
    db.flush()

    # ── CONTRA 2: Sozialleistungsbelastung ────────────────────────
    m_con2 = ArgumentNode(
        topic_id=topic3.id, parent_id=m_pro2.id,
        title="Zuwanderung belastet das Sozialleistungssystem überproportional",
        description="Viele Zuwanderer beziehen Transferleistungen über Jahre, "
                    "was die Sozialkassen strukturell überfordert.",
        position=Position.CONTRA,
        statement_type=StatementType.POSITIVE,
        claim="Mehr Zuwanderer bedeuten dauerhaft mehr Ausgaben für Sozialleistungen.",
        reason="Ein Großteil der Asylbewerber hat keinen sofortigen Zugang zum Arbeitsmarkt.",
        example="Laut IAB-Studie 2023 sind 5 Jahre nach Einreise noch ca. 40 % der Geflüchteten nicht erwerbstätig.",
        implication="Unkontrollierte Zuwanderung ist fiskalisch nicht nachhaltig.",
        argument_group_id=eco_group.id,
        created_by=bob.id,
    )
    db.add(m_con2)
    db.flush()

    # ── NEUTRAL: Metadiskussion – Integration als eigentliche Frage
    m_neu = ArgumentNode(
        topic_id=topic3.id, parent_id=m_con2.id,
        title="Die eigentliche Frage ist Integration, nicht Zuwanderungsmenge",
        description="Die quantitative Zuwanderungsdebatte lenkt vom eigentlichen Problem ab: "
                    "fehlende Integrationspolitik.",
        position=Position.NEUTRAL,
        statement_type=StatementType.NORMATIVE,
        claim="Die Debatte über Zuwanderungszahlen verfehlt das Kernproblem.",
        reason="Selbst geringe Zuwanderung ist problematisch ohne Sprach- und Bildungsprogramme.",
        implication="Vor einem Mehr oder Weniger müssen Integrationsinstitutionen gestärkt werden.",
        edge_type=EdgeType.REFRAME,
        created_by=charlie.id,
    )
    db.add(m_neu)
    db.flush()

    # ── HIDDEN: Xenophober Slogan (community downvoted) ───────────
    # Demonstriert visibility=VOTED_DOWN: Argument ist vorhanden aber ausgeblendet.
    m_hidden = ArgumentNode(
        topic_id=topic3.id, parent_id=m_con1.id,
        title="Ausländer raus!",
        description="Alle Ausländer sollen Deutschland verlassen.",
        position=Position.CONTRA,
        statement_type=StatementType.NORMATIVE,
        visibility=Visibility.VOTED_DOWN,
        hidden_reason="Community downvoted: kein sachlicher Beitrag, xenophober Slogan ohne Argumentation.",
        created_by=bob.id,
    )
    db.add(m_hidden)
    db.flush()

    # ── Evidence ──────────────────────────────────────────────────
    db.add_all([
        Evidence(
            argument_node_id=m_pro1.id,
            evidence_type=EvidenceType.STUDY,
            title="Bundesagentur für Arbeit: Engpassanalyse Fachkräftemangel 2023",
            url="https://www.arbeitsagentur.de/datei/engpassanalyse_ba014195.pdf",
            quality_score=0.9,
            created_by=alice.id,
        ),
        Evidence(
            argument_node_id=m_pro2.id,
            evidence_type=EvidenceType.LAW,
            title="Artikel 16a Grundgesetz – Recht auf politisches Asyl",
            url="https://www.gesetze-im-internet.de/gg/art_16a.html",
            quality_score=0.95,
            created_by=alice.id,
        ),
        Evidence(
            argument_node_id=m_con2.id,
            evidence_type=EvidenceType.STUDY,
            title="IAB-Kurzbericht: Geflüchtete auf dem Arbeitsmarkt 2023",
            url="https://www.iab.de/",
            quality_score=0.88,
            created_by=bob.id,
        ),
        Evidence(
            argument_node_id=m_con1.id,
            evidence_type=EvidenceType.EXPERT_OPINION,
            title="Hans-Werner Sinn: Zuwanderung und Lohneffekte im Niedriglohnsektor",
            description="Ökonom Sinn argumentiert, dass niedrig-qualifizierte Zuwanderung "
                        "Reallöhne im Wettbewerbssegment drückt.",
            quality_score=0.65,
            created_by=bob.id,
        ),
        Evidence(
            argument_node_id=m_neu.id,
            evidence_type=EvidenceType.ANECDOTE,
            title="Erfahrungsbericht: Integrationskurs-Wartelisten 2022",
            description="Viele Kommunen berichten von monatelangen Wartelisten für Deutschkurse — "
                        "selbst bei voller Integrationsbereitschaft.",
            quality_score=0.3,
            created_by=charlie.id,
        ),
    ])

    # ── Tags ──────────────────────────────────────────────────────
    tag_economy = Tag(name="Wirtschaft", category=TagCategory.DOMAIN)
    tag_human_rights = Tag(name="Menschenrechte", category=TagCategory.MORAL_FOUNDATION,
                           moral_foundation=MoralFoundation.CARE)
    tag_integration = Tag(name="Integration", category=TagCategory.DOMAIN)
    tag_labor_market = Tag(name="Arbeitsmarkt", category=TagCategory.DOMAIN)
    tag_law = Tag(name="Recht & Gesetz", category=TagCategory.MORAL_FOUNDATION,
                  moral_foundation=MoralFoundation.AUTHORITY)
    db.add_all([tag_economy, tag_human_rights, tag_integration, tag_labor_market, tag_law])
    db.flush()

    db.add_all([
        ArgumentNodeTag(argument_node_id=m_pro1.id, tag_id=tag_economy.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=m_pro1.id, tag_id=tag_labor_market.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=m_pro2.id, tag_id=tag_human_rights.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=m_pro2.id, tag_id=tag_law.id, origin=TagOrigin.MODERATOR),
        ArgumentNodeTag(argument_node_id=m_con1.id, tag_id=tag_labor_market.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=m_con1.id, tag_id=tag_economy.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=m_con2.id, tag_id=tag_economy.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=m_neu.id, tag_id=tag_integration.id, origin=TagOrigin.USER),
    ])

    # ── Labels ────────────────────────────────────────────────────
    db.add_all([
        # FALLACY: Korrelation ≠ Kausalität auf m_con2
        NodeLabel(
            argument_node_id=m_con2.id,
            label_type=LabelType.FALLACY,
            justification="Korrelation ist keine Kausalität: Nicht-Erwerbstätigkeit kann viele "
                          "Ursachen haben (Sprachbarriere, Anerkennung, bürokratische Hürden).",
            created_by=alice.id,
        ),
        # MISSING_EVIDENCE: Kausaler Beleg für Lohndruck fehlt bei m_con1
        NodeLabel(
            argument_node_id=m_con1.id,
            label_type=LabelType.MISSING_EVIDENCE,
            justification="Kausaler Zusammenhang zwischen Zuwanderung und Lohndrückung "
                          "im deutschen Baugewerbe nicht direkt belegt.",
            created_by=charlie.id,
        ),
        # OFF_TOPIC: Xenophober Slogan trägt nichts zur Diskussion bei
        NodeLabel(
            argument_node_id=m_hidden.id,
            label_type=LabelType.OFF_TOPIC,
            justification="Kein sachlicher Beitrag zur Diskussionsfrage.",
            created_by=alice.id,
        ),
    ])

    # ── Votes ─────────────────────────────────────────────────────
    db.add_all([
        Vote(user_id=alice.id, argument_node_id=m_pro1.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=m_pro1.id, value=1),
        Vote(user_id=alice.id, argument_node_id=m_pro2.id, value=1),
        Vote(user_id=bob.id, argument_node_id=m_con1.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=m_con1.id, value=-1),
        Vote(user_id=bob.id, argument_node_id=m_con2.id, value=1),
        Vote(user_id=alice.id, argument_node_id=m_con2.id, value=-1),
        Vote(user_id=charlie.id, argument_node_id=m_neu.id, value=1),
        Vote(user_id=alice.id, argument_node_id=m_hidden.id, value=-1),
        Vote(user_id=charlie.id, argument_node_id=m_hidden.id, value=-1),
    ])

    # ── Comments ──────────────────────────────────────────────────
    db.add_all([
        Comment(argument_node_id=m_pro1.id, user_id=bob.id,
                text="Gilt primär für hochqualifizierte Zuwanderung. Asylmigration folgt anderen Regeln."),
        Comment(argument_node_id=m_pro2.id, user_id=bob.id,
                text="Art. 16a GG ist durch den sicherer-Drittstaaten-Passus (§ 26a AsylG) stark eingeschränkt."),
        Comment(argument_node_id=m_neu.id, user_id=alice.id,
                text="Reframing-Argument: Verschiebt die Debatte auf die Meta-Ebene. Berechtigt, "
                     "aber vermeidet die eigentliche Frage nicht."),
    ])

    db.commit()
    t1_title = topic1.title
    t2_title = topic2.title
    t3_title = topic3.title
    q_count = db.query(ArgumentNode).filter(ArgumentNode.topic_id == topic1.id).count()
    b_count = db.query(ArgumentNode).filter(ArgumentNode.topic_id == topic2.id).count()
    m_count = db.query(ArgumentNode).filter(ArgumentNode.topic_id == topic3.id).count()
    b1_count = db.query(ArgumentNode).filter(
        ArgumentNode.topic_id == topic2.id, ArgumentNode.stage_added == 1
    ).count()
    b2_count = db.query(ArgumentNode).filter(
        ArgumentNode.topic_id == topic2.id, ArgumentNode.stage_added == 2
    ).count()
    db.close()
    print("✅ Seed data created successfully!")
    print(f"   Topic 1: '{t1_title}' with {q_count} argument nodes")
    print(f"   Topic 2: '{t2_title}' with {b_count} argument nodes "
          f"({b1_count} stage-1 basis, {b2_count} stage-2 splits)")
    print(f"   Topic 3: '{t3_title}' with {m_count} argument nodes "
          f"(Phase-0 full-feature demo: anatomy, visibility, labels, evidence, group)")


if __name__ == "__main__":
    seed()

