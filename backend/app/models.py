import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Text, Float, ForeignKey, Enum, DateTime, Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


# ── Enums ──────────────────────────────────────────────────────────────

class Position(str, enum.Enum):
    PRO = "PRO"
    CONTRA = "CONTRA"
    NEUTRAL = "NEUTRAL"


class EvidenceType(str, enum.Enum):
    STUDY = "STUDY"
    STATISTIC = "STATISTIC"
    ARTICLE = "ARTICLE"
    HISTORICAL_EVENT = "HISTORICAL_EVENT"


class LabelType(str, enum.Enum):
    FALLACY = "FALLACY"
    DOUBLE_STANDARD = "DOUBLE_STANDARD"
    CIRCULAR = "CIRCULAR"


class PatternType(str, enum.Enum):
    GISH_GALLOP = "GISH_GALLOP"
    CREEPING_RELATIVIZATION = "CREEPING_RELATIVIZATION"
    OTHER = "OTHER"


class MoralFoundation(str, enum.Enum):
    CARE = "CARE"
    FAIRNESS = "FAIRNESS"
    LOYALTY = "LOYALTY"
    AUTHORITY = "AUTHORITY"
    SANCTITY = "SANCTITY"


def _utcnow():
    return datetime.now(timezone.utc)


# ── Association tables ─────────────────────────────────────────────────

argument_node_tags = Table(
    "argument_node_tags",
    Base.metadata,
    Column("argument_node_id", Integer, ForeignKey("argument_nodes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

multi_node_pattern_members = Table(
    "multi_node_pattern_members",
    Base.metadata,
    Column("pattern_id", Integer, ForeignKey("multi_node_patterns.id", ondelete="CASCADE"), primary_key=True),
    Column("argument_node_id", Integer, ForeignKey("argument_nodes.id", ondelete="CASCADE"), primary_key=True),
)


# ── Models ─────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # TODO: proper hashing
    created_at = Column(DateTime, default=_utcnow)

    topics = relationship("Topic", back_populates="author")
    argument_nodes = relationship("ArgumentNode", back_populates="author")
    votes = relationship("Vote", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    author = relationship("User", back_populates="topics")
    argument_nodes = relationship("ArgumentNode", back_populates="topic", cascade="all, delete-orphan")
    argument_groups = relationship("ArgumentGroup", back_populates="topic", cascade="all, delete-orphan")
    multi_node_patterns = relationship("MultiNodePattern", back_populates="topic", cascade="all, delete-orphan")


class ArgumentGroup(Base):
    __tablename__ = "argument_groups"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    canonical_title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    topic = relationship("Topic", back_populates="argument_groups")
    argument_nodes = relationship("ArgumentNode", back_populates="argument_group")


class ArgumentNode(Base):
    __tablename__ = "argument_nodes"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("argument_nodes.id"), nullable=True)
    argument_group_id = Column(Integer, ForeignKey("argument_groups.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    position = Column(Enum(Position), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    topic = relationship("Topic", back_populates="argument_nodes")
    author = relationship("User", back_populates="argument_nodes")
    argument_group = relationship("ArgumentGroup", back_populates="argument_nodes")
    parent = relationship("ArgumentNode", remote_side="ArgumentNode.id", back_populates="children")
    children = relationship("ArgumentNode", back_populates="parent", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=argument_node_tags, back_populates="argument_nodes")
    votes = relationship("Vote", back_populates="argument_node", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="argument_node", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="argument_node", cascade="all, delete-orphan")
    labels = relationship("NodeLabel", back_populates="argument_node", cascade="all, delete-orphan")
    definition_forks = relationship("DefinitionFork", back_populates="argument_node", cascade="all, delete-orphan")
    patterns = relationship("MultiNodePattern", secondary=multi_node_pattern_members, back_populates="members")


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("user_id", "argument_node_id", name="uq_user_node_vote"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    argument_node_id = Column(Integer, ForeignKey("argument_nodes.id"), nullable=False)
    value = Column(Integer, nullable=False)  # +1 or -1
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="votes")
    argument_node = relationship("ArgumentNode", back_populates="votes")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    moral_foundation = Column(Enum(MoralFoundation), nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    argument_nodes = relationship("ArgumentNode", secondary=argument_node_tags, back_populates="tags")
    tag_votes = relationship("TagVote", back_populates="tag")


class TagVote(Base):
    __tablename__ = "tag_votes"
    __table_args__ = (
        UniqueConstraint("user_id", "tag_id", "argument_node_id", name="uq_user_tag_node_vote"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    argument_node_id = Column(Integer, ForeignKey("argument_nodes.id"), nullable=False)
    value = Column(Integer, nullable=False)  # +1 or -1
    created_at = Column(DateTime, default=_utcnow)

    tag = relationship("Tag", back_populates="tag_votes")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    argument_node_id = Column(Integer, ForeignKey("argument_nodes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    argument_node = relationship("ArgumentNode", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    argument_node_id = Column(Integer, ForeignKey("argument_nodes.id"), nullable=False)
    evidence_type = Column(Enum(EvidenceType), nullable=False)
    url = Column(String(2000), nullable=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)  # 0.0–1.0
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    argument_node = relationship("ArgumentNode", back_populates="evidence")


class NodeLabel(Base):
    __tablename__ = "node_labels"

    id = Column(Integer, primary_key=True, index=True)
    argument_node_id = Column(Integer, ForeignKey("argument_nodes.id"), nullable=False)
    label_type = Column(Enum(LabelType), nullable=False)
    justification = Column(Text, nullable=False)  # Begründungspflicht
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    argument_node = relationship("ArgumentNode", back_populates="labels")


class MultiNodePattern(Base):
    __tablename__ = "multi_node_patterns"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    name = Column(String(200), nullable=False)
    pattern_type = Column(Enum(PatternType), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    topic = relationship("Topic", back_populates="multi_node_patterns")
    members = relationship("ArgumentNode", secondary=multi_node_pattern_members, back_populates="patterns")


class DefinitionFork(Base):
    __tablename__ = "definition_forks"

    id = Column(Integer, primary_key=True, index=True)
    argument_node_id = Column(Integer, ForeignKey("argument_nodes.id"), nullable=False)
    term = Column(String(200), nullable=False)
    definition_variant = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    argument_node = relationship("ArgumentNode", back_populates="definition_forks")

