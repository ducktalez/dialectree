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
    #  TOPIC 1: Quotenrassismus – Vollständiger Zigzag-Dialog
    #
    #  Basiert auf der Diskussionsstruktur aus implementation-plan.md:
    #  L1 → R1 → L2 → R2 (edge attack) → L3 → R3 → L4 (Konsens)
    #  mit Alternativen / Geschwistern auf jeder Ebene.
    # ══════════════════════════════════════════════════════════════════

    topic1 = Topic(
        title="Sind Quotenregelungen rassistisch?",
        description="Quotenregelungen sollen historische Benachteiligung ausgleichen — "
                    "doch sind sie selbst eine Form von Rassismus?",
        created_by=alice.id,
    )
    db.add(topic1)
    db.flush()

    # ── L1: Eröffnung (PRO Quoten = rassistisch) ─────────────────
    l1 = ArgumentNode(
        topic_id=topic1.id,
        title="Quotenregelungen sind rassistisch — sie bewerten nach Hautfarbe",
        description="Wenn eine Person wegen ihrer Herkunft bevorzugt wird, ist das per Definition Diskriminierung.",
        position=Position.PRO, created_by=bob.id,
        statement_type=StatementType.NORMATIVE,
        conflict_zone=ConflictZone.VALUE,
        claim="Quotenregelungen diskriminieren nach Herkunft.",
        reason="Jede Ungleichbehandlung aufgrund von Ethnie ist Rassismus, egal in welche Richtung.",
        example="Asiatische Bewerber brauchen bei Harvard höhere Scores als andere Gruppen.",
        implication="Quoten müssen abgeschafft werden, um echte Gleichberechtigung zu erreichen.",
    )
    db.add(l1)
    db.flush()

    # Alternativen zu L1 (gleicher parent_id = null → Geschwister)
    l1_alt1 = ArgumentNode(
        topic_id=topic1.id,
        title="Leistungsprinzip muss gelten — die beste Person soll den Job bekommen",
        description="Quoten untergraben Meritokratie und können zu weniger qualifizierten Besetzungen führen.",
        position=Position.PRO, created_by=bob.id,
        statement_type=StatementType.MIXED,
        conflict_zone=ConflictZone.CAUSAL,
    )
    l1_alt2 = ArgumentNode(
        topic_id=topic1.id,
        title="Individuelle Rechte übertrumpfen Gruppenstatistiken",
        description="Niemand sollte für die Taten seiner Vorfahren bestraft oder belohnt werden.",
        position=Position.PRO, created_by=bob.id,
        statement_type=StatementType.NORMATIVE,
        conflict_zone=ConflictZone.VALUE,
    )
    db.add_all([l1_alt1, l1_alt2])
    db.flush()

    # ── R1: Gegenargument (CONTRA – historische Korrektur) ────────
    r1 = ArgumentNode(
        topic_id=topic1.id, parent_id=l1.id,
        title="Historische Ungerechtigkeit erfordert aktive Korrektur",
        description="Ohne Quoten bleiben strukturelle Barrieren bestehen. Formale Gleichheit reicht nicht.",
        position=Position.CONTRA, created_by=alice.id,
        statement_type=StatementType.NORMATIVE,
        conflict_zone=ConflictZone.VALUE,
        claim="Positive Diskriminierung korrigiert strukturelle Benachteiligung.",
        reason="Jahrhundertelange Diskriminierung hat Ungleichheiten geschaffen, die sich nicht von selbst auflösen.",
        example="Frauenquoten in Aufsichtsräten haben den Frauenanteil von 10% auf 35% erhöht.",
        implication="Temporäre Ungleichbehandlung ist nötig, um echte Chancengleichheit herzustellen.",
    )
    # Alternative zu R1
    r1_alt1 = ArgumentNode(
        topic_id=topic1.id, parent_id=l1.id,
        title="Diversity in Teams führt nachweislich zu besseren Ergebnissen",
        description="McKinsey-Studien zeigen: Diverse Teams sind innovativer und profitabler.",
        position=Position.CONTRA, created_by=alice.id,
        conflict_zone=ConflictZone.FACT,
    )
    db.add_all([r1, r1_alt1])
    db.flush()

    # ── L2: Antwort auf R1 (PRO – Gegenangriff) ──────────────────
    l2 = ArgumentNode(
        topic_id=topic1.id, parent_id=r1.id,
        title="Rassismus gegen Weiße gibt es nicht — Rassismus erfordert Machtstrukturen",
        description="Akademische Definition: Rassismus = Vorurteil + institutionelle Macht. "
                    "Daher kann positive Diskriminierung per Definition kein Rassismus sein.",
        position=Position.CONTRA, created_by=alice.id,
        conflict_zone=ConflictZone.FACT, edge_type=EdgeType.REFRAME,
        opens_conflict="Welche Definition von Rassismus ist korrekt?",
    )
    db.add(l2)
    db.flush()

    # ── R2: Edge Attack auf die Verbindung L2→R1 ─────────────────
    # "DOCH! Was ist überhaupt Rassismus?" — greift nicht den Inhalt
    # von L2 an, sondern die Inferenz (undercutting defeater).
    r2 = ArgumentNode(
        topic_id=topic1.id, parent_id=l2.id,
        title="DOCH! Was ist überhaupt Rassismus? — Definitionsstreit",
        description="Die Verbindung zwischen 'historische Korrektur' und 'kein Rassismus' "
                    "setzt eine umstrittene Definition voraus. Das muss erst geklärt werden.",
        position=Position.PRO, created_by=bob.id,
        conflict_zone=ConflictZone.FACT, edge_type=EdgeType.COMMUNITY_NOTE,
        is_edge_attack=True,
        opens_conflict="Was ist die korrekte Definition von Rassismus?",
    )
    # Alternative zu R2
    r2_alt1 = ArgumentNode(
        topic_id=topic1.id, parent_id=l2.id,
        title="Asiatische Amerikaner werden durch Quoten systematisch benachteiligt",
        description="Harvard-Zulassungsdaten zeigen: Asiaten brauchen höhere Scores. "
                    "Das widerlegt die These, dass nur Weiße betroffen sind.",
        position=Position.PRO, created_by=bob.id,
        conflict_zone=ConflictZone.FACT, edge_type=EdgeType.WEAKENING,
    )
    db.add_all([r2, r2_alt1])
    db.flush()

    # ── L3: Meta-Einordnung (NEUTRAL) ─────────────────────────────
    l3 = ArgumentNode(
        topic_id=topic1.id, parent_id=r2.id,
        title="Der Begriff 'Rassismus' muss erst definiert werden",
        description="Ohne gemeinsame Definition redet man aneinander vorbei. "
                    "Ist Rassismus = Vorurteil + Macht, oder = jede Ungleichbehandlung nach Ethnie?",
        position=Position.NEUTRAL, created_by=charlie.id,
        statement_type=StatementType.MIXED,
        conflict_zone=ConflictZone.FACT,
        edge_type=EdgeType.REFRAME,
        opens_conflict="Was ist die korrekte Definition von Rassismus?",
    )
    db.add(l3)
    db.flush()

    # ── R3: Quoten schaffen Stigmatisierung ───────────────────────
    r3 = ArgumentNode(
        topic_id=topic1.id, parent_id=l3.id,
        title="Quoten schaffen Stigmatisierung — Quotenperson statt anerkannte Fachkraft",
        description="Betroffene leiden unter dem Verdacht, nur wegen der Quote eingestellt "
                    "worden zu sein. Das schadet den Menschen, die sie schützen sollen.",
        position=Position.PRO, created_by=bob.id,
        conflict_zone=ConflictZone.CAUSAL, edge_type=EdgeType.CONSEQUENCES,
    )
    db.add(r3)
    db.flush()

    # ── L4: Kompromissvorschlag ───────────────────────────────────
    l4 = ArgumentNode(
        topic_id=topic1.id, parent_id=r3.id,
        title="Anonymisierte Bewerbungsverfahren statt starrer Quoten",
        description="Wenn man Herkunft und Geschlecht im Bewerbungsprozess entfernt, "
                    "behebt man strukturelle Diskriminierung ohne neue zu schaffen.",
        position=Position.NEUTRAL, created_by=charlie.id,
        statement_type=StatementType.MIXED,
        conflict_zone=ConflictZone.CAUSAL,
        edge_type=EdgeType.CONCESSION,
    )
    # Alternative zu L4
    l4_alt1 = ArgumentNode(
        topic_id=topic1.id, parent_id=r3.id,
        title="Das Leistungsprinzip funktioniert nur bei gleichen Startbedingungen",
        description="Wer aus einem benachteiligten Umfeld kommt, hatte nie die gleichen Chancen.",
        position=Position.CONTRA, created_by=charlie.id,
        conflict_zone=ConflictZone.CAUSAL, edge_type=EdgeType.WEAKENING,
        is_edge_attack=True,
    )
    db.add_all([l4, l4_alt1])
    db.flush()

    # ── Tags ──────────────────────────────────────────────────────
    tag_justice = Tag(name="Gerechtigkeit & Teilhabe", category=TagCategory.SOCIETAL_GOAL)
    tag_freedom = Tag(name="Freiheit & Selbstbestimmung", category=TagCategory.SOCIETAL_GOAL)
    tag_equality = Tag(name="Gleichberechtigung", category=TagCategory.DOMAIN)
    tag_law = Tag(name="Recht", category=TagCategory.DOMAIN)
    tag_sociology = Tag(name="Soziologie", category=TagCategory.DOMAIN)
    tag_fairness = Tag(name="Fairness", moral_foundation=MoralFoundation.FAIRNESS,
                       category=TagCategory.MORAL_FOUNDATION)
    tag_care = Tag(name="Fürsorge", moral_foundation=MoralFoundation.CARE,
                   category=TagCategory.MORAL_FOUNDATION)
    db.add_all([tag_justice, tag_freedom, tag_equality, tag_law, tag_sociology,
                tag_fairness, tag_care])
    db.flush()

    db.add_all([
        ArgumentNodeTag(argument_node_id=l1.id, tag_id=tag_freedom.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=l1.id, tag_id=tag_equality.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=r1.id, tag_id=tag_justice.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=r1.id, tag_id=tag_equality.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=l1_alt1.id, tag_id=tag_fairness.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=l3.id, tag_id=tag_sociology.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=r1_alt1.id, tag_id=tag_care.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=l4.id, tag_id=tag_fairness.id, origin=TagOrigin.MODERATOR),
    ])

    # ── Votes ─────────────────────────────────────────────────────
    db.add_all([
        Vote(user_id=bob.id, argument_node_id=l1.id, value=1),
        Vote(user_id=alice.id, argument_node_id=r1.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=r1.id, value=1),
        Vote(user_id=bob.id, argument_node_id=l1_alt1.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=l3.id, value=1),
        Vote(user_id=alice.id, argument_node_id=l3.id, value=1),
        Vote(user_id=bob.id, argument_node_id=r2.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=l4.id, value=1),
    ])

    # ── Comments ──────────────────────────────────────────────────
    db.add_all([
        Comment(argument_node_id=l1.id, user_id=alice.id,
                text="Das Argument ignoriert den historischen Kontext komplett."),
        Comment(argument_node_id=r1.id, user_id=bob.id,
                text="Historische Korrektur ist berechtigt, aber warum ausgerechnet über Quoten?"),
        Comment(argument_node_id=l3.id, user_id=bob.id,
                text="Guter Punkt — ohne Definitionsklärung dreht man sich im Kreis."),
        Comment(argument_node_id=r2.id, user_id=charlie.id,
                text="Klassischer Definitionsstreit. Die akademische und die alltagssprachliche "
                     "Definition von Rassismus klaffen auseinander."),
        Comment(argument_node_id=l4.id, user_id=alice.id,
                text="Pragmatischer Ansatz, der beide Seiten berücksichtigt."),
    ])

    # ── Evidence ──────────────────────────────────────────────────
    db.add(Evidence(
        argument_node_id=r1_alt1.id,
        evidence_type=EvidenceType.STUDY,
        title="McKinsey: Diversity Wins (2020)",
        url="https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/diversity-wins-how-inclusion-matters",
        quality_score=0.85,
        created_by=alice.id,
    ))
    db.add(Evidence(
        argument_node_id=r2_alt1.id,
        evidence_type=EvidenceType.LAW,
        title="Students for Fair Admissions v. Harvard (2023)",
        url="https://www.supremecourt.gov/opinions/22pdf/20-1199_hgdj.pdf",
        quality_score=0.95,
        created_by=bob.id,
    ))

    # ── Labels ────────────────────────────────────────────────────
    db.add(NodeLabel(
        argument_node_id=l2.id,
        label_type=LabelType.FALLACY,
        justification="No-True-Scotsman / Definitionsverschiebung: Die Definition von Rassismus "
                       "wird so verengt, dass Gegenbeispiele per Definition ausgeschlossen werden.",
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
    # Ein Argument pro Turn, chronologisch. Der rote Faden ist implizit
    # über die parent_id-Kette: b1 → a1 → a2 → a3 → a4 → a5

    b1 = ArgumentNode(
        topic_id=topic2.id,
        title="B₁: Quotenregelungen sind Diskriminierung",
        description="These klar formulieren: Ungleichbehandlung nach Ethnie ist per Definition Diskriminierung.",
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
        description="Steelmanning: Die beste Version des Gegenarguments. "
                    "Formale Gleichheit reicht nicht, wenn Startbedingungen ungleich sind.",
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
                    "eine umstrittene Definition voraus. Edge Attack auf die Inferenz.",
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
        description="Der Definitionskonflikt wird explizit gemacht. Verschiedene Positionen "
                    "existieren nebeneinander: akademisch vs. alltagssprachlich vs. kontextuell.",
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
        description="Alternativ-Eröffnung: Fokus auf Meritokratie statt auf Rassismus-Begriff.",
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

    db.commit()
    t1_title = topic1.title
    t2_title = topic2.title
    q_count = db.query(ArgumentNode).filter(ArgumentNode.topic_id == topic1.id).count()
    b_count = db.query(ArgumentNode).filter(ArgumentNode.topic_id == topic2.id).count()
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


if __name__ == "__main__":
    seed()

