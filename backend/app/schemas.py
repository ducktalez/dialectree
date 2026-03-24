from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ── User ───────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: str
    password: str  # TODO: hash on server


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    created_at: datetime


# ── Topic ──────────────────────────────────────────────────────────────

class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = None
    transcript_yaml: Optional[str] = None


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    transcript_yaml: Optional[str] = None
    created_by: int
    created_at: datetime


# ── ArgumentNode ───────────────────────────────────────────────────────

class ArgumentNodeCreate(BaseModel):
    topic_id: int
    parent_id: Optional[int] = None
    argument_group_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    position: str  # PRO / CONTRA / NEUTRAL
    position_score: Optional[float] = None  # 0.0–1.0
    statement_type: Optional[str] = "UNCLASSIFIED"
    # Argument anatomy (taxonomy §3)
    claim: Optional[str] = None
    reason: Optional[str] = None
    example: Optional[str] = None
    implication: Optional[str] = None
    # Zigzag view fields (Phase Z)
    conflict_zone: Optional[str] = None  # FACT / CAUSAL / VALUE
    edge_type: Optional[str] = None  # COMMUNITY_NOTE / CONSEQUENCES / WEAKENING / REFRAME / CONCESSION
    is_edge_attack: bool = False
    opens_conflict: Optional[str] = None
    # 5-step refinement model
    stage_added: int = 1
    split_from_id: Optional[int] = None  # Stage-1 base argument this was split from


class ArgumentNodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topic_id: int
    parent_id: Optional[int]
    argument_group_id: Optional[int]
    title: str
    description: Optional[str]
    position: str
    position_score: Optional[float]
    statement_type: str
    visibility: str
    hidden_reason: Optional[str]
    claim: Optional[str]
    reason: Optional[str]
    example: Optional[str]
    implication: Optional[str]
    conflict_zone: Optional[str]
    edge_type: Optional[str]
    is_edge_attack: bool
    opens_conflict: Optional[str]
    stage_added: int = 1
    split_from_id: Optional[int] = None
    created_by: int
    created_at: datetime


class ArgumentNodeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[str] = None
    position_score: Optional[float] = None
    statement_type: Optional[str] = None
    visibility: Optional[str] = None
    hidden_reason: Optional[str] = None
    claim: Optional[str] = None
    reason: Optional[str] = None
    example: Optional[str] = None
    implication: Optional[str] = None
    conflict_zone: Optional[str] = None
    edge_type: Optional[str] = None
    is_edge_attack: Optional[bool] = None
    opens_conflict: Optional[str] = None


# ── ArgumentGroup ─────────────────────────────────────────────────────

class ArgumentGroupCreate(BaseModel):
    topic_id: int
    canonical_title: str
    description: Optional[str] = None


class ArgumentGroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topic_id: int
    canonical_title: str
    description: Optional[str]
    created_at: datetime


class ArgumentGroupUpdate(BaseModel):
    canonical_title: Optional[str] = None
    description: Optional[str] = None


# ── Vote ───────────────────────────────────────────────────────────────

class VoteCreate(BaseModel):
    argument_node_id: int
    value: int  # +1 or -1


class VoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    argument_node_id: int
    value: int
    created_at: datetime


# ── Tag ────────────────────────────────────────────────────────────────

class TagCreate(BaseModel):
    name: str
    moral_foundation: Optional[str] = None
    category: Optional[str] = None  # TagCategory; defaults to OTHER


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    moral_foundation: Optional[str]
    category: Optional[str]
    created_at: datetime


class TagAssign(BaseModel):
    tag_id: int
    argument_node_id: int
    origin: Optional[str] = "USER"  # TagOrigin: USER / MODERATOR / AI


class TagOnNode(BaseModel):
    """Lightweight tag info included in tree responses."""
    model_config = ConfigDict(from_attributes=True)
    tag_id: int
    tag_name: str
    category: Optional[str] = None
    moral_foundation: Optional[str] = None
    origin: str = "USER"


# ── TagVote ────────────────────────────────────────────────────────────

class TagVoteCreate(BaseModel):
    tag_id: int
    argument_node_id: int
    value: int  # +1 or -1


class TagVoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    tag_id: int
    argument_node_id: int
    value: int
    created_at: datetime


# ── Comment ────────────────────────────────────────────────────────────

class CommentCreate(BaseModel):
    argument_node_id: int
    text: str


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    argument_node_id: int
    user_id: int
    text: str
    created_at: datetime


# ── Evidence ───────────────────────────────────────────────────────────

class EvidenceCreate(BaseModel):
    argument_node_id: int
    evidence_type: str  # See taxonomy §7: PROOF, META_ANALYSIS, STUDY, STATISTIC, LAW, etc.
    url: Optional[str] = None
    title: str
    description: Optional[str] = None
    quality_score: Optional[float] = None  # If None, default derived from evidence_type


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    argument_node_id: int
    evidence_type: str
    url: Optional[str]
    title: str
    description: Optional[str]
    quality_score: Optional[float]
    created_by: int
    created_at: datetime


# ── NodeLabel ──────────────────────────────────────────────────────────

class NodeLabelCreate(BaseModel):
    argument_node_id: int
    label_type: str  # See taxonomy §13: FALLACY, MISSING_EVIDENCE, OFF_TOPIC, SPAM, etc.
    justification: str


class NodeLabelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    argument_node_id: int
    label_type: str
    justification: str
    confirmed: int
    confirmed_at: Optional[datetime]
    created_by: int
    created_at: datetime


# ── Tree response ──────────────────────────────────────────────────────

# ── DefinitionFork ─────────────────────────────────────────────────────

class DefinitionForkCreate(BaseModel):
    argument_node_id: int
    term: str
    definition_variant: str
    description: Optional[str] = None


class DefinitionForkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    argument_node_id: int
    term: str
    definition_variant: str
    description: Optional[str]
    created_at: datetime


# ── MultiNodePattern ──────────────────────────────────────────────────

class MultiNodePatternCreate(BaseModel):
    topic_id: int
    name: str
    pattern_type: str  # GISH_GALLOP / CREEPING_RELATIVIZATION / OTHER
    description: Optional[str] = None
    member_ids: list[int] = []


class MultiNodePatternOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topic_id: int
    name: str
    pattern_type: str
    description: Optional[str]
    created_by: int
    created_at: datetime
    member_ids: list[int] = []


# ── Tree response (nested) ────────────────────────────────────────────

class ArgumentTreeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    position: str
    position_score: Optional[float] = None
    statement_type: str = "UNCLASSIFIED"
    visibility: str = "VISIBLE"
    hidden_reason: Optional[str] = None
    parent_id: Optional[int]
    argument_group_id: Optional[int] = None
    # Argument anatomy
    claim: Optional[str] = None
    reason: Optional[str] = None
    example: Optional[str] = None
    implication: Optional[str] = None
    # Zigzag view fields
    conflict_zone: Optional[str] = None
    edge_type: Optional[str] = None
    is_edge_attack: bool = False
    opens_conflict: Optional[str] = None
    created_by: int = 0
    vote_score: int = 0
    tags: list[TagOnNode] = []
    labels: list[str] = []
    evidence_count: int = 0
    comment_count: int = 0
    children: list["ArgumentTreeNode"] = []


# ── Zigzag response ───────────────────────────────────────────────────

class ZigzagStepOut(BaseModel):
    """A single argument in the zigzag view (flat, chronological)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    parent_id: Optional[int]
    title: str
    description: Optional[str]
    position: str
    position_score: Optional[float]
    conflict_zone: Optional[str]
    edge_type: Optional[str]
    is_edge_attack: bool
    opens_conflict: Optional[str]
    stage_added: int = 1
    split_from_id: Optional[int] = None
    vote_score: int = 0
    sibling_ids: list[int] = []
    created_at: datetime


class ZigzagTopicInfo(BaseModel):
    id: int
    title: str


class ZigzagResponse(BaseModel):
    topic: ZigzagTopicInfo
    stage: int = 2
    steps: list[ZigzagStepOut]


class TranscriptResponse(BaseModel):
    """Response for GET and PUT /api/topics/{id}/transcript (Stage 0)."""
    topic_id: int
    topic_title: str
    transcript_yaml: Optional[str]


class TranscriptUpdate(BaseModel):
    """Request body for PUT /api/topics/{id}/transcript (Stage 0)."""
    transcript_yaml: Optional[str] = None


