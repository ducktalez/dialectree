"""
Seed script: Creates the example topic "Sollte Rauchen verboten werden?"
with a full argument tree, tags, evidence, labels and an argument group.

Usage:  python -m app.seed
"""
from .database import engine, SessionLocal, Base
from .models import (
    User, Topic, ArgumentNode, ArgumentGroup, Vote, Tag, Comment,
    Evidence, NodeLabel, Position, EvidenceType, LabelType, MoralFoundation,
)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # ── Users ──────────────────────────────────────────────────────
    alice = User(username="alice", email="alice@example.com", password_hash="TODO")
    bob = User(username="bob", email="bob@example.com", password_hash="TODO")
    charlie = User(username="charlie", email="charlie@example.com", password_hash="TODO")
    db.add_all([alice, bob, charlie])
    db.flush()

    # ── Topic ──────────────────────────────────────────────────────
    topic = Topic(
        title="Sollte Rauchen verboten werden?",
        description="Eine strukturierte Analyse der Argumente für und gegen ein Rauchverbot.",
        created_by=alice.id,
    )
    db.add(topic)
    db.flush()

    # ── Argument Group (similar arguments bundled) ─────────────────
    health_group = ArgumentGroup(
        topic_id=topic.id,
        canonical_title="Gesundheitsschäden durch Rauchen",
        description="Verschiedene Formulierungen des Gesundheitsarguments.",
    )
    db.add(health_group)
    db.flush()

    # ── Argument Nodes (the tree) ──────────────────────────────────
    # Level 1: Direct arguments pro/contra
    pro1 = ArgumentNode(
        topic_id=topic.id, title="Rauchen verursacht nachweislich Krebs und Herzkrankheiten",
        description="Tausende Studien belegen den kausalen Zusammenhang.",
        position=Position.PRO, created_by=alice.id, argument_group_id=health_group.id,
    )
    pro2 = ArgumentNode(
        topic_id=topic.id, title="Passivrauchen schädigt unbeteiligte Dritte",
        description="Nichtraucher werden unfreiwillig gesundheitlichen Risiken ausgesetzt.",
        position=Position.PRO, created_by=alice.id,
    )
    pro3 = ArgumentNode(
        topic_id=topic.id, title="Gesundheitskosten belasten die Allgemeinheit",
        description="Rauchbedingte Krankheiten verursachen Milliarden an Behandlungskosten.",
        position=Position.PRO, created_by=charlie.id, argument_group_id=health_group.id,
    )
    con1 = ArgumentNode(
        topic_id=topic.id, title="Persönliche Freiheit: Jeder darf über seinen Körper entscheiden",
        description="Ein Verbot wäre ein unverhältnismäßiger Eingriff in die Selbstbestimmung.",
        position=Position.CONTRA, created_by=bob.id,
    )
    con2 = ArgumentNode(
        topic_id=topic.id, title="Prohibition funktioniert nicht – Schwarzmarkt entsteht",
        description="Historisch haben Verbote den Konsum nie eliminiert, sondern in die Illegalität verschoben.",
        position=Position.CONTRA, created_by=bob.id,
    )
    con3 = ArgumentNode(
        topic_id=topic.id, title="Wirtschaftliche Folgen: Arbeitsplatzverluste in der Tabakindustrie",
        description="Hunderttausende Arbeitsplätze hängen an der Tabakbranche.",
        position=Position.CONTRA, created_by=bob.id,
    )
    neutral1 = ArgumentNode(
        topic_id=topic.id, title="Stufenweise Regulierung statt Totalverbot",
        description="Altersgrenzen, Werbeverbote und rauchfreie Zonen als Mittelweg.",
        position=Position.NEUTRAL, created_by=charlie.id,
    )
    db.add_all([pro1, pro2, pro3, con1, con2, con3, neutral1])
    db.flush()

    # Level 2: Sub-arguments
    pro1_1 = ArgumentNode(
        topic_id=topic.id, parent_id=pro1.id,
        title="WHO klassifiziert Tabakrauch als Karzinogen der Gruppe 1",
        position=Position.PRO, created_by=alice.id,
    )
    pro2_1 = ArgumentNode(
        topic_id=topic.id, parent_id=pro2.id,
        title="Kinder von Rauchern haben höheres Asthmarisiko",
        position=Position.PRO, created_by=alice.id,
    )
    con1_1 = ArgumentNode(
        topic_id=topic.id, parent_id=con1.id,
        title="Wo zieht man die Grenze? Alkohol, Zucker, Extremsport auch verbieten?",
        description="Das Argument der Selbstbestimmung führt zur Frage der Konsistenz.",
        position=Position.CONTRA, created_by=bob.id,
    )
    con2_1 = ArgumentNode(
        topic_id=topic.id, parent_id=con2.id,
        title="Alkoholprohibition in den USA (1920–1933) gescheitert",
        position=Position.CONTRA, created_by=bob.id,
    )
    con1_1_1 = ArgumentNode(
        topic_id=topic.id, parent_id=con1_1.id,
        title="Passivrauchen unterscheidet Rauchen von rein selbstschädigendem Verhalten",
        description="Rauchen in Gegenwart anderer ist keine rein private Entscheidung.",
        position=Position.PRO, created_by=charlie.id,
    )
    # A counter to the counter
    pro3_1 = ArgumentNode(
        topic_id=topic.id, parent_id=pro3.id,
        title="Tabaksteuereinnahmen kompensieren die Kosten nicht vollständig",
        position=Position.PRO, created_by=alice.id,
    )
    con3_1 = ArgumentNode(
        topic_id=topic.id, parent_id=con3.id,
        title="Umschulung und Strukturwandel sind machbar – Kohleausstieg als Beispiel",
        position=Position.PRO, created_by=charlie.id,
    )
    neutral1_1 = ArgumentNode(
        topic_id=topic.id, parent_id=neutral1.id,
        title="Neuseeland plant generationelles Rauchverbot ab 2027",
        description="Personen geboren nach 2008 dürfen nie legal Tabak kaufen.",
        position=Position.NEUTRAL, created_by=charlie.id,
    )
    db.add_all([pro1_1, pro2_1, con1_1, con2_1, con1_1_1, pro3_1, con3_1, neutral1_1])
    db.flush()

    # ── Tags ───────────────────────────────────────────────────────
    tag_health = Tag(name="Gesundheit")
    tag_freedom = Tag(name="Freiheit", moral_foundation=MoralFoundation.CARE)
    tag_economics = Tag(name="Wirtschaft")
    tag_history = Tag(name="Historischer Vergleich")
    tag_fairness = Tag(name="Fairness", moral_foundation=MoralFoundation.FAIRNESS)
    db.add_all([tag_health, tag_freedom, tag_economics, tag_history, tag_fairness])
    db.flush()

    # Assign tags
    pro1.tags.extend([tag_health])
    pro2.tags.extend([tag_health, tag_fairness])
    pro3.tags.extend([tag_health, tag_economics])
    con1.tags.extend([tag_freedom])
    con2.tags.extend([tag_history])
    con3.tags.extend([tag_economics])
    con2_1.tags.extend([tag_history])

    # ── Votes ──────────────────────────────────────────────────────
    db.add_all([
        Vote(user_id=alice.id, argument_node_id=pro1.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=pro1.id, value=1),
        Vote(user_id=bob.id, argument_node_id=pro1.id, value=-1),
        Vote(user_id=bob.id, argument_node_id=con1.id, value=1),
        Vote(user_id=alice.id, argument_node_id=con1.id, value=-1),
        Vote(user_id=charlie.id, argument_node_id=neutral1.id, value=1),
        Vote(user_id=alice.id, argument_node_id=neutral1.id, value=1),
    ])

    # ── Comments ───────────────────────────────────────────────────
    db.add_all([
        Comment(argument_node_id=pro1.id, user_id=bob.id,
                text="Die Studien sind valide, aber ein Verbot ist trotzdem der falsche Weg."),
        Comment(argument_node_id=con1.id, user_id=alice.id,
                text="Selbstbestimmung endet dort, wo andere geschädigt werden."),
    ])

    # ── Evidence ───────────────────────────────────────────────────
    db.add(Evidence(
        argument_node_id=pro1.id,
        evidence_type=EvidenceType.STUDY,
        title="WHO Report on the Global Tobacco Epidemic 2023",
        url="https://www.who.int/publications/i/item/9789240077164",
        quality_score=0.95,
        created_by=alice.id,
    ))
    db.add(Evidence(
        argument_node_id=con2_1.id,
        evidence_type=EvidenceType.HISTORICAL_EVENT,
        title="US Prohibition (Volstead Act, 1920–1933)",
        description="18th Amendment: Alkoholverbot führte zu organisierter Kriminalität.",
        quality_score=0.8,
        created_by=bob.id,
    ))
    db.add(Evidence(
        argument_node_id=pro3_1.id,
        evidence_type=EvidenceType.STATISTIC,
        title="Tabaksteuer vs. Gesundheitskosten – DKFZ Studie",
        url="https://www.dkfz.de/",
        quality_score=0.85,
        created_by=charlie.id,
    ))

    # ── Labels (fallacy marking) ──────────────────────────────────
    db.add(NodeLabel(
        argument_node_id=con1_1.id,
        label_type=LabelType.FALLACY,
        justification="Whataboutism / Slippery Slope: 'Dann müsste man auch X verbieten' "
                       "lenkt vom eigentlichen Argument ab, ohne es zu widerlegen.",
        created_by=alice.id,
    ))

    db.commit()
    topic_title = topic.title
    db.close()
    print("✅ Seed data created successfully!")
    print(f"   Topic: '{topic_title}' with 16 argument nodes")


if __name__ == "__main__":
    seed()



