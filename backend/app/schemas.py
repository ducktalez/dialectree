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


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
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


class ArgumentNodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topic_id: int
    parent_id: Optional[int]
    argument_group_id: Optional[int]
    title: str
    description: Optional[str]
    position: str
    created_by: int
    created_at: datetime


class ArgumentNodeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[str] = None


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


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    moral_foundation: Optional[str]
    created_at: datetime


class TagAssign(BaseModel):
    tag_id: int
    argument_node_id: int


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
    evidence_type: str  # STUDY / STATISTIC / ARTICLE / HISTORICAL_EVENT
    url: Optional[str] = None
    title: str
    description: Optional[str] = None
    quality_score: Optional[float] = None


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
    label_type: str  # FALLACY / DOUBLE_STANDARD / CIRCULAR
    justification: str


class NodeLabelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    argument_node_id: int
    label_type: str
    justification: str
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
    parent_id: Optional[int]
    created_by: int = 0
    vote_score: int = 0
    tags: list[str] = []
    labels: list[str] = []
    evidence_count: int = 0
    comment_count: int = 0
    children: list["ArgumentTreeNode"] = []

