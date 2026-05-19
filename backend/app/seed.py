"""
Seed script: Creates one example topic for the Zigzag view:
  "Sollte es Quoten für Minderheiten geben?" — a full Stage-0…2 example
  with raw transcript, basis arguments, splits, a consensus node, evidence,
  votes, comments and a fallacy label.

Usage:  python -m app.seed
"""
import json
from datetime import datetime
from pathlib import Path

from .database import engine, SessionLocal, Base
from .models import (
    User, Topic, ArgumentNode, ArgumentGroup, Vote, Tag, Comment,
    Evidence, NodeLabel, Position, EvidenceType, LabelType, MoralFoundation,
    StatementType, Visibility, TagCategory, TagOrigin, ArgumentNodeTag,
    ConflictZone, EdgeType,
    Source, SourceTag, SourceComment, SourceUsage, SourceKind,
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
        title="Quoten sind rassistisch gegenüber Weißen",
        description="Quotenregelungen sind rassistisch gegenüber Weißen und schlecht.",
        position=Position.CONTRA, created_by=bob.id,
        conflict_zone=ConflictZone.VALUE,
        stage_added=1,
    )
    db.add(r1)
    db.flush()

    l2 = ArgumentNode(
        topic_id=topic1.id, parent_id=r1.id,
        title="Rassismus braucht Macht – Quoten korrigieren strukturelle Diskriminierung",
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
        title="Gruppenunterschiede sind durch Kultur und IQ erklärbar",
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
        title="IQ-Argument ist rassistisch und sachlich falsch",
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
    # Titles deliberately drop the "(2.1) ↩ 2.1:" notation — the UI derives
    # short reference IDs (#L1.1 etc.) automatically from position + order.
    l2_1 = ArgumentNode(
        topic_id=topic1.id, parent_id=r1.id, split_from_id=l2.id,
        title="Rassismus gegen Weiße gibt es nicht",
        description=None,
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    l2_2 = ArgumentNode(
        topic_id=topic1.id, parent_id=r1.id, split_from_id=l2.id,
        title="Quoten korrigieren Unterrepräsentation durch strukturelle Diskriminierung",
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
        title="Doch, Rassismus gegen Weiße gibt es",
        description="Jede Ungleichbehandlung aufgrund von Ethnie ist Rassismus — "
                    "unabhängig von Machtstrukturen.",
        position=Position.CONTRA, created_by=bob.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    r3_2 = ArgumentNode(
        topic_id=topic1.id, parent_id=l2_2.id, split_from_id=r3.id,
        title="Unterschiede erklärbar durch Kultur- und IQ-Unterschiede",
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
        title="Das ist Rassismus",
        description="Gruppenunterschiede mit IQ zu erklären reproduziert rassistische Denkmuster.",
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.VALUE,
        stage_added=2,
    )
    l4_2 = ArgumentNode(
        topic_id=topic1.id, parent_id=r3_2.id, split_from_id=l4.id,
        title="IQ hat keine Bedeutung für den Erfolg",
        description="Beruflicher Erfolg wird durch soziale Netzwerke, Kapital und Chancen bestimmt — nicht durch IQ.",
        position=Position.PRO, created_by=alice.id,
        conflict_zone=ConflictZone.FACT,
        stage_added=2,
    )
    l4_3 = ArgumentNode(
        topic_id=topic1.id, parent_id=r3_2.id, split_from_id=l4.id,
        title="IQ ist nicht angeboren — Unterschiede folgen aus struktureller Diskriminierung",
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
        # Ad-hominem documentation: the phrase "Bist du bescheuert?" appears
        # in the Stage-0 transcript right before L4 (Anna → Ben). It is *not*
        # represented as its own ArgumentNode, because it carries no
        # argumentative content. Instead it is flagged here as part of the
        # discussion record so reviewers know it was noticed and discarded.
        Comment(argument_node_id=l4.id, user_id=charlie.id,
                text='Hinweis zum Verlauf: Anna sagt vor L4 wörtlich „Bist du '
                     'bescheuert?". Das ist ein Ad-hominem-Angriff auf Ben und '
                     'wird nicht als Argument geführt.'),
    ])

    # ── Labels ────────────────────────────────────────────────────
    db.add(NodeLabel(
        argument_node_id=l2_1.id,
        label_type=LabelType.FALLACY,
        justification="No-True-Scotsman: Die akademische Rassismus-Definition wird so gewählt, "
                      "dass Weiße per Definition keine Opfer sein können.",
        created_by=bob.id,
    ))

    # ── Consensus node (NEUTRAL + CONCESSION) ─────────────────────
    # Demonstrates a distinct argument type: both speakers agree that the
    # term "Rassismus" must be defined before progress is possible. Kept as
    # the only ported addition from the former blueprint topic — concession
    # nodes are not otherwise represented in this discussion.
    consensus = ArgumentNode(
        topic_id=topic1.id, parent_id=l4.id,
        title='Konsens — Begriff „Rassismus" muss erst geklärt werden',
        description="Beide Seiten stimmen überein: ohne gemeinsame Definition "
                    "von Rassismus reden sie aneinander vorbei. Klärung der "
                    "Definitionsfrage geht der Sachdebatte voraus.",
        position=Position.NEUTRAL, created_by=charlie.id,
        statement_type=StatementType.MIXED,
        conflict_zone=ConflictZone.VALUE,
        edge_type=EdgeType.CONCESSION,
        opens_conflict="Was ist die korrekte Definition von Rassismus?",
        stage_added=1,
    )
    db.add(consensus)
    db.flush()

    # ── Evidence (demonstrates the Evidence model) ────────────────
    # Attached to L2 (structural-correction argument); referenced in the
    # transcript via the McKinsey claim.
    db.add(Evidence(
        argument_node_id=l2.id,
        evidence_type=EvidenceType.STUDY,
        title="McKinsey: Diversity Wins (2020)",
        url="https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/diversity-wins-how-inclusion-matters",
        quality_score=0.85,
        created_by=alice.id,
    ))

    db.commit()
    t1_title = topic1.title
    q_count = db.query(ArgumentNode).filter(ArgumentNode.topic_id == topic1.id).count()
    # ── Quellensammlung: import curated JSON if present and DB is empty ─────
    src_count = _seed_sources_from_json(db)
    db.close()
    print("Seed data created successfully!")
    print(f"   Topic: '{t1_title}' with {q_count} argument nodes")
    if src_count:
        print(f"   Quellensammlung: {src_count} sources imported from sources.json")


def _seed_sources_from_json(db) -> int:
    """Import sources from data/sources.json into the DB.

    Idempotent: skipped if any Source already exists (re-import would create
    duplicates because the JSON ids don't survive across DB lifetimes).
    Returns the number of newly created Source rows.
    """
    if db.query(Source).first() is not None:
        return 0
    src_file = _DATA_DIR / "sources.json"
    if not src_file.exists():
        return 0
    try:
        raw = json.loads(src_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    tag_cache: dict[str, SourceTag] = {}

    def _tag(name: str) -> SourceTag:
        if name not in tag_cache:
            existing = db.query(SourceTag).filter(SourceTag.name == name).first()
            tag_cache[name] = existing or SourceTag(name=name)
        return tag_cache[name]

    def _parse_date(s: str | None):
        if not s:
            return None
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            return None

    created = 0
    for entry in raw.get("sources", []):
        try:
            kind = SourceKind(entry.get("kind", "TEXT").upper())
        except ValueError:
            continue
        src = Source(
            title=entry.get("title") or "(ohne Titel)",
            kind=kind,
            url=entry.get("url"),
            description=entry.get("description"),
            thumbnail=entry.get("thumbnail"),
            media_url=entry.get("media_url"),
            up=int(entry.get("up", 0)),
            down=int(entry.get("down", 0)),
        )
        ca = _parse_date(entry.get("created_at"))
        if ca:
            src.created_at = ca
        src.tags = [_tag(t) for t in entry.get("tags", []) if t]
        for c in entry.get("comments", []):
            sc = SourceComment(
                user=c.get("user") or "anonym",
                text=c.get("text") or "",
            )
            cc = _parse_date(c.get("created_at"))
            if cc:
                sc.created_at = cc
            src.comments.append(sc)
        for u in entry.get("usages", []):
            src.usages.append(SourceUsage(
                argument_id=u.get("argument_id"),
                context=u.get("context") or "",
                note=u.get("note"),
            ))
        db.add(src)
        created += 1
    db.commit()
    return created


if __name__ == "__main__":
    seed()

