"""
Seed script: Creates the example topic "Sollte Rauchen verboten werden?"
with a full argument tree, tags, evidence, labels and an argument group.

Usage:  python -m app.seed
"""
from .database import engine, SessionLocal, Base
from .models import (
    User, Topic, ArgumentNode, ArgumentGroup, Vote, Tag, Comment,
    Evidence, NodeLabel, Position, EvidenceType, LabelType, MoralFoundation,
    StatementType, Visibility, TagCategory, TagOrigin, ArgumentNodeTag,
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
        statement_type=StatementType.POSITIVE,
        claim="Rauchen verursacht Krebs und Herzkrankheiten.",
        reason="Tausende Studien belegen einen kausalen Zusammenhang zwischen Tabakkonsum und Krebserkrankungen.",
        example="Lungenkrebs tritt bei Rauchern 15–30x häufiger auf als bei Nichtrauchern.",
        implication="Ein Verbot würde diese vermeidbaren Todesfälle reduzieren.",
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
        statement_type=StatementType.NORMATIVE,
        claim="Jeder Mensch hat das Recht, über seinen eigenen Körper zu entscheiden.",
        reason="Selbstbestimmung ist ein Grundrecht und darf nur eingeschränkt werden, wenn Dritte geschädigt werden.",
        implication="Ein Rauchverbot wäre ein unverhältnismäßiger Eingriff in die persönliche Freiheit.",
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
        statement_type=StatementType.MIXED,
        claim="Eine stufenweise Regulierung ist dem Totalverbot vorzuziehen.",
        reason="Maßnahmen wie Altersgrenzen und Werbeverbote reduzieren den Konsum, ohne Freiheitsrechte komplett einzuschränken.",
        example="Rauchfreie Zonen in Restaurants haben den Passivrauch-Kontakt drastisch gesenkt.",
        implication="Ein differenzierter Ansatz erreicht gesundheitliche Ziele bei geringerem Freiheitseingriff.",
    )
    db.add_all([pro1, pro2, pro3, con1, con2, con3, neutral1])
    db.flush()

    # Level 2: Sub-arguments (multiple per parent to show real branching)
    pro1_1 = ArgumentNode(
        topic_id=topic.id, parent_id=pro1.id,
        title="WHO klassifiziert Tabakrauch als Karzinogen der Gruppe 1",
        position=Position.PRO, created_by=alice.id,
    )
    pro1_2 = ArgumentNode(
        topic_id=topic.id, parent_id=pro1.id,
        title="Lebenserwartung von Rauchern ist im Schnitt 10 Jahre kürzer",
        position=Position.PRO, created_by=charlie.id,
    )
    pro1_3 = ArgumentNode(
        topic_id=topic.id, parent_id=pro1.id,
        title="Korrelation ≠ Kausalität: Lebensstil-Confounders werden ignoriert",
        description="Raucher haben oft auch andere ungesunde Gewohnheiten.",
        position=Position.CONTRA, created_by=bob.id,
    )
    pro2_1 = ArgumentNode(
        topic_id=topic.id, parent_id=pro2.id,
        title="Kinder von Rauchern haben höheres Asthmarisiko",
        position=Position.PRO, created_by=alice.id,
    )
    pro2_2 = ArgumentNode(
        topic_id=topic.id, parent_id=pro2.id,
        title="Rauchverbote in Gaststätten haben Passivrauch-Belastung bereits drastisch gesenkt",
        position=Position.NEUTRAL, created_by=charlie.id,
    )
    pro2_3 = ArgumentNode(
        topic_id=topic.id, parent_id=pro2.id,
        title="Im Freien ist Passivrauch-Konzentration vernachlässigbar gering",
        position=Position.CONTRA, created_by=bob.id,
    )
    con1_1 = ArgumentNode(
        topic_id=topic.id, parent_id=con1.id,
        title="Wo zieht man die Grenze? Alkohol, Zucker, Extremsport auch verbieten?",
        description="Das Argument der Selbstbestimmung führt zur Frage der Konsistenz.",
        position=Position.CONTRA, created_by=bob.id,
    )
    con1_2 = ArgumentNode(
        topic_id=topic.id, parent_id=con1.id,
        title="Suchtpotenzial schränkt die freie Entscheidung bereits ein",
        description="Nikotinabhängigkeit macht 'freiwilligen' Konsum fragwürdig.",
        position=Position.PRO, created_by=alice.id,
    )
    con2_1 = ArgumentNode(
        topic_id=topic.id, parent_id=con2.id,
        title="Alkoholprohibition in den USA (1920–1933) gescheitert",
        position=Position.CONTRA, created_by=bob.id,
    )
    con2_2 = ArgumentNode(
        topic_id=topic.id, parent_id=con2.id,
        title="Neuseeland und Bhutan zeigen, dass schrittweise Verbote funktionieren können",
        position=Position.PRO, created_by=charlie.id,
    )
    con1_1_1 = ArgumentNode(
        topic_id=topic.id, parent_id=con1_1.id,
        title="Passivrauchen unterscheidet Rauchen von rein selbstschädigendem Verhalten",
        description="Rauchen in Gegenwart anderer ist keine rein private Entscheidung.",
        position=Position.PRO, created_by=charlie.id,
    )
    con1_1_2 = ArgumentNode(
        topic_id=topic.id, parent_id=con1_1.id,
        title="Auch Autofahren schädigt Dritte (Abgase) – trotzdem kein Verbot",
        position=Position.CONTRA, created_by=bob.id,
    )
    # A counter to the counter
    pro3_1 = ArgumentNode(
        topic_id=topic.id, parent_id=pro3.id,
        title="Tabaksteuereinnahmen kompensieren die Kosten nicht vollständig",
        position=Position.PRO, created_by=alice.id,
    )
    pro3_2 = ArgumentNode(
        topic_id=topic.id, parent_id=pro3.id,
        title="Präventionskosten sind geringer als Behandlungskosten",
        position=Position.PRO, created_by=charlie.id,
    )
    pro3_3 = ArgumentNode(
        topic_id=topic.id, parent_id=pro3.id,
        title="Raucher sterben früher und entlasten damit Rentenkassen",
        description="Makabres aber ökonomisch belegtes Gegenargument.",
        position=Position.CONTRA, created_by=bob.id,
    )
    con3_1 = ArgumentNode(
        topic_id=topic.id, parent_id=con3.id,
        title="Umschulung und Strukturwandel sind machbar – Kohleausstieg als Beispiel",
        position=Position.PRO, created_by=charlie.id,
    )
    con3_2 = ArgumentNode(
        topic_id=topic.id, parent_id=con3.id,
        title="Tabak-Landwirte in Entwicklungsländern verlieren Existenzgrundlage",
        position=Position.CONTRA, created_by=bob.id,
    )
    neutral1_1 = ArgumentNode(
        topic_id=topic.id, parent_id=neutral1.id,
        title="Neuseeland plant generationelles Rauchverbot ab 2027",
        description="Personen geboren nach 2008 dürfen nie legal Tabak kaufen.",
        position=Position.NEUTRAL, created_by=charlie.id,
    )
    neutral1_2 = ArgumentNode(
        topic_id=topic.id, parent_id=neutral1.id,
        title="Altersgrenze auf 21 anheben hat in den USA den Jugendkonsum gesenkt",
        position=Position.PRO, created_by=alice.id,
    )
    neutral1_3 = ArgumentNode(
        topic_id=topic.id, parent_id=neutral1.id,
        title="Regulierung wird von der Tabakindustrie systematisch unterlaufen",
        position=Position.CONTRA, created_by=bob.id,
    )
    db.add_all([
        pro1_1, pro1_2, pro1_3,
        pro2_1, pro2_2, pro2_3,
        con1_1, con1_2,
        con2_1, con2_2,
        con1_1_1, con1_1_2,
        pro3_1, pro3_2, pro3_3,
        con3_1, con3_2,
        neutral1_1, neutral1_2, neutral1_3,
    ])
    db.flush()

    # ── Tags ───────────────────────────────────────────────────────
    # Societal goals (the actual sub-goals of "lebenswerte Welt")
    goal_safety = Tag(name="Sicherheit & Gesundheit", category=TagCategory.SOCIETAL_GOAL)
    goal_freedom = Tag(name="Freiheit & Selbstbestimmung", category=TagCategory.SOCIETAL_GOAL)
    goal_justice = Tag(name="Gerechtigkeit & Teilhabe", category=TagCategory.SOCIETAL_GOAL)
    goal_prosperity = Tag(name="Wohlstand & Prosperität", category=TagCategory.SOCIETAL_GOAL)
    goal_sustainability = Tag(name="Nachhaltigkeit", category=TagCategory.SOCIETAL_GOAL)
    # Domain tags (thematic areas)
    tag_health = Tag(name="Gesundheit", category=TagCategory.DOMAIN)
    tag_economics = Tag(name="Wirtschaft", category=TagCategory.DOMAIN)
    tag_history = Tag(name="Historischer Vergleich", category=TagCategory.META_ARGUMENTATION)
    # Moral foundations (stay as tags, explain WHY people prioritize certain goals)
    tag_care = Tag(name="Fürsorge", moral_foundation=MoralFoundation.CARE, category=TagCategory.MORAL_FOUNDATION)
    tag_freedom_mf = Tag(name="Autonomie", moral_foundation=MoralFoundation.FAIRNESS, category=TagCategory.MORAL_FOUNDATION)
    tag_fairness = Tag(name="Fairness", moral_foundation=MoralFoundation.FAIRNESS, category=TagCategory.MORAL_FOUNDATION)
    db.add_all([
        goal_safety, goal_freedom, goal_justice, goal_prosperity, goal_sustainability,
        tag_health, tag_economics, tag_history,
        tag_care, tag_freedom_mf, tag_fairness,
    ])
    db.flush()

    # Assign tags (with origin tracking)
    db.add_all([
        # Societal goals on root arguments
        ArgumentNodeTag(argument_node_id=pro1.id, tag_id=goal_safety.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=pro2.id, tag_id=goal_safety.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=pro3.id, tag_id=goal_prosperity.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=con1.id, tag_id=goal_freedom.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=con3.id, tag_id=goal_prosperity.id, origin=TagOrigin.AI),
        # Domain tags
        ArgumentNodeTag(argument_node_id=pro1.id, tag_id=tag_health.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=pro1_2.id, tag_id=tag_health.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=pro2.id, tag_id=tag_health.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=pro3.id, tag_id=tag_economics.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=pro3_3.id, tag_id=tag_economics.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=con3.id, tag_id=tag_economics.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=con3_2.id, tag_id=tag_economics.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=con2.id, tag_id=tag_history.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=con2_1.id, tag_id=tag_history.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=con2_2.id, tag_id=tag_history.id, origin=TagOrigin.USER),
        # Moral foundations as explanatory tags
        ArgumentNodeTag(argument_node_id=pro1.id, tag_id=tag_care.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=pro2.id, tag_id=tag_care.id, origin=TagOrigin.MODERATOR),
        ArgumentNodeTag(argument_node_id=con1.id, tag_id=tag_freedom_mf.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=con1_2.id, tag_id=tag_health.id, origin=TagOrigin.AI),
    ])

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
        Comment(argument_node_id=pro1.id, user_id=charlie.id,
                text="Wichtigstes Argument in der ganzen Debatte."),
        Comment(argument_node_id=con1.id, user_id=alice.id,
                text="Selbstbestimmung endet dort, wo andere geschädigt werden."),
        Comment(argument_node_id=con1_1.id, user_id=charlie.id,
                text="Klassischer Slippery-Slope. Die Grenze ist klar definierbar."),
        Comment(argument_node_id=neutral1.id, user_id=bob.id,
                text="Pragmatischster Ansatz, aber politisch schwer durchsetzbar."),
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
        evidence_type=EvidenceType.HISTORICAL,
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

    # ══════════════════════════════════════════════════════════════════
    #  TOPIC 2: Klimapolitik
    # ══════════════════════════════════════════════════════════════════

    topic2 = Topic(
        title="Sollte Deutschland bis 2035 klimaneutral werden?",
        description="Analyse der Argumente für und gegen eine beschleunigte Klimaneutralität.",
        created_by=alice.id,
    )
    db.add(topic2)
    db.flush()

    # ── Additional tags for Klimapolitik ──────────────────────────
    tag_environment = Tag(name="Umwelt", category=TagCategory.DOMAIN)
    tag_social = Tag(name="Soziales", category=TagCategory.DOMAIN)
    db.add_all([tag_environment, tag_social])
    db.flush()

    # ── Strand 1: Klimaschäden – die naturwissenschaftliche Kette ──
    k_pro1 = ArgumentNode(
        topic_id=topic2.id,
        title="Klimawandel verursacht irreversible Schäden",
        description="Dürren, Extremwetter und Meeresspiegelanstieg bedrohen Lebensgrundlagen weltweit.",
        position=Position.PRO, created_by=alice.id,
        statement_type=StatementType.POSITIVE,
        claim="Die Folgekosten des Klimawandels übersteigen die Kosten der Transformation.",
        reason="Irreversible Kipppunkte (Permafrost, Golfstrom) machen Verzögerung exponentiell teurer.",
        implication="Schnelles Handeln ist ökonomisch und ethisch geboten.",
    )
    # Sub: Vertiefung + Gegenargument
    k_pro1_1 = ArgumentNode(
        topic_id=topic2.id,
        title="Kipppunkte machen jedes Jahr Verzögerung exponentiell teurer",
        description="Bei Überschreitung von ~1.5°C werden Rückkopplungsschleifen unkontrollierbar.",
        position=Position.PRO, created_by=alice.id,
    )
    k_pro1_2 = ArgumentNode(
        topic_id=topic2.id,
        title="Klimamodelle haben Unsicherheitsbereiche von ±1.5°C",
        description="Die genaue Klimasensitivität ist nicht exakt bestimmt – Handeln unter Unsicherheit.",
        position=Position.CONTRA, created_by=bob.id,
        statement_type=StatementType.MIXED,
    )
    # Premises (depth 2) – Grundwahrheiten
    k_gt1 = ArgumentNode(
        topic_id=topic2.id,
        title="CO₂-Emissionen erhöhen die globale Durchschnittstemperatur",
        description="IPCC AR6: 'Unequivocal' – wissenschaftlicher Konsens seit Jahrzehnten.",
        position=Position.PRO, created_by=charlie.id,
    )
    k_gt1_contra = ArgumentNode(
        topic_id=topic2.id,
        title="Unsicherheit rechtfertigt kein Nichtstun – Vorsorgeprinzip",
        description="Gerade bei irreversiblen Risiken ist Handeln unter Unsicherheit rational.",
        position=Position.PRO, created_by=alice.id,
    )

    # ── Strand 2: Wirtschaftliche Chancen vs. Risiken ─────────────
    k_pro2 = ArgumentNode(
        topic_id=topic2.id,
        title="Frühe Transformation schafft Wettbewerbsvorteile",
        description="First-Mover-Advantage bei erneuerbaren Energien und Speichertechnologien.",
        position=Position.PRO, created_by=charlie.id,
        statement_type=StatementType.POSITIVE,
        claim="Wer früh transformiert, dominiert die Märkte der Zukunft.",
        example="China investierte 2023 über 890 Mrd. $ in Clean Tech.",
    )
    k_con1 = ArgumentNode(
        topic_id=topic2.id,
        title="Zu schnelle Transformation gefährdet Industriestandort und soziale Stabilität",
        description="Energieintensive Branchen (Stahl, Chemie) können nicht über Nacht umgestellt werden.",
        position=Position.CONTRA, created_by=bob.id,
        statement_type=StatementType.POSITIVE,
        claim="Die Geschwindigkeit der Transformation überfordert Wirtschaft und Gesellschaft.",
        reason="Arbeitsplätze gehen schneller verloren als neue entstehen.",
    )
    # Sub-arguments
    k_pro2_1 = ArgumentNode(
        topic_id=topic2.id,
        title="China investiert 890 Mrd. $ in Clean Tech (2023)",
        description="Wer nicht mitzieht, verliert Marktanteile an Länder mit Industriepolitik.",
        position=Position.PRO, created_by=charlie.id,
    )
    k_con1_1 = ArgumentNode(
        topic_id=topic2.id,
        title="Sozialverträglicher Übergang ist mit gezielten Transfers möglich",
        description="Kohleausstieg + Strukturwandelfonds zeigt: Transformation gelingt mit Begleitung.",
        position=Position.PRO, created_by=alice.id,
    )
    k_con1_2 = ArgumentNode(
        topic_id=topic2.id,
        title="Energiepreise steigen kurzfristig und belasten einkommensschwache Haushalte",
        position=Position.CONTRA, created_by=bob.id,
    )
    # Premise
    k_gt2 = ArgumentNode(
        topic_id=topic2.id,
        title="Wirtschaftliche Transformation erfordert Investitionen und verursacht kurzfristige Kosten",
        position=Position.NEUTRAL, created_by=charlie.id,
    )

    # ── Strand 3: Globale Gerechtigkeit ───────────────────────────
    k_neutral1 = ArgumentNode(
        topic_id=topic2.id,
        title="Deutschlands CO₂-Anteil beträgt nur 2% – nationale Maßnahmen allein lösen nichts",
        description="Klimaschutz erfordert globale Kooperation, nicht nur nationale Alleingänge.",
        position=Position.NEUTRAL, created_by=bob.id,
        statement_type=StatementType.MIXED,
    )
    k_neutral1_1 = ArgumentNode(
        topic_id=topic2.id,
        title="Vorbildfunktion und Technologieexport skalieren den Effekt weit über 2%",
        position=Position.PRO, created_by=alice.id,
    )
    k_neutral1_2 = ArgumentNode(
        topic_id=topic2.id,
        title="Carbon Leakage: Produktion verlagert sich in Länder ohne Klimapolitik",
        description="Netto-Effekt kann sogar negativ sein wenn Emissionen nur verlagert werden.",
        position=Position.CONTRA, created_by=bob.id,
    )

    db.add_all([
        k_pro1, k_pro2, k_con1, k_neutral1,
    ])
    db.flush()

    # Set parent IDs for depth-1
    k_pro1_1.parent_id = k_pro1.id
    k_pro1_2.parent_id = k_pro1.id
    k_pro2_1.parent_id = k_pro2.id
    k_con1_1.parent_id = k_con1.id
    k_con1_2.parent_id = k_con1.id
    k_neutral1_1.parent_id = k_neutral1.id
    k_neutral1_2.parent_id = k_neutral1.id
    for n in [k_pro1_1, k_pro1_2, k_pro2_1, k_con1_1, k_con1_2, k_neutral1_1, k_neutral1_2]:
        n.topic_id = topic2.id
    db.add_all([k_pro1_1, k_pro1_2, k_pro2_1, k_con1_1, k_con1_2, k_neutral1_1, k_neutral1_2])
    db.flush()

    # Set parent IDs for depth-2 (premises / ground truths)
    k_gt1.parent_id = k_pro1_1.id
    k_gt1.topic_id = topic2.id
    k_gt1_contra.parent_id = k_pro1_2.id
    k_gt1_contra.topic_id = topic2.id
    k_gt2.parent_id = k_con1_2.id
    k_gt2.topic_id = topic2.id
    db.add_all([k_gt1, k_gt1_contra, k_gt2])
    db.flush()

    # ── Tags for Klimapolitik ─────────────────────────────────────
    db.add_all([
        # Societal goals
        ArgumentNodeTag(argument_node_id=k_pro1.id, tag_id=goal_sustainability.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=k_pro1.id, tag_id=goal_safety.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=k_pro2.id, tag_id=goal_prosperity.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=k_con1.id, tag_id=goal_prosperity.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=k_neutral1.id, tag_id=goal_justice.id, origin=TagOrigin.AI),
        # Domain tags
        ArgumentNodeTag(argument_node_id=k_pro1.id, tag_id=tag_environment.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=k_pro2.id, tag_id=tag_economics.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=k_con1.id, tag_id=tag_economics.id, origin=TagOrigin.USER),
        ArgumentNodeTag(argument_node_id=k_con1.id, tag_id=tag_social.id, origin=TagOrigin.MODERATOR),
        ArgumentNodeTag(argument_node_id=k_neutral1.id, tag_id=tag_environment.id, origin=TagOrigin.USER),
        # Moral foundations
        ArgumentNodeTag(argument_node_id=k_pro1.id, tag_id=tag_care.id, origin=TagOrigin.AI),
        ArgumentNodeTag(argument_node_id=k_neutral1.id, tag_id=tag_fairness.id, origin=TagOrigin.USER),
    ])

    # ── Votes for Klimapolitik ────────────────────────────────────
    db.add_all([
        Vote(user_id=alice.id, argument_node_id=k_pro1.id, value=1),
        Vote(user_id=charlie.id, argument_node_id=k_pro1.id, value=1),
        Vote(user_id=bob.id, argument_node_id=k_con1.id, value=1),
        Vote(user_id=alice.id, argument_node_id=k_neutral1.id, value=1),
    ])

    # ── Comments for Klimapolitik ─────────────────────────────────
    db.add_all([
        Comment(argument_node_id=k_pro1.id, user_id=bob.id,
                text="Die Faktenlage ist klar – die Frage ist nur das Tempo."),
        Comment(argument_node_id=k_con1.id, user_id=alice.id,
                text="Tempo muss sozial begleitet werden, aber kein Grund nicht zu handeln."),
    ])

    # ── Evidence for Klimapolitik ─────────────────────────────────
    db.add(Evidence(
        argument_node_id=k_pro1.id,
        evidence_type=EvidenceType.STUDY,
        title="IPCC AR6 Synthesis Report (2023)",
        url="https://www.ipcc.ch/report/ar6/syr/",
        quality_score=0.98,
        created_by=alice.id,
    ))
    db.add(Evidence(
        argument_node_id=k_pro2_1.id,
        evidence_type=EvidenceType.STATISTIC,
        title="BloombergNEF – Global Clean Energy Investment 2023",
        url="https://about.bnef.com/",
        quality_score=0.9,
        created_by=charlie.id,
    ))

    db.commit()
    topic_title = topic.title
    topic2_title = topic2.title
    db.close()
    print("✅ Seed data created successfully!")
    print(f"   Topic 1: '{topic_title}' with 27 argument nodes")
    print(f"   Topic 2: '{topic2_title}' with 17 argument nodes")


if __name__ == "__main__":
    seed()



