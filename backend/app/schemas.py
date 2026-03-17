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

class ArgumentTreeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    position: str
    parent_id: Optional[int]
    vote_score: int = 0
    children: list["ArgumentTreeNode"] = []

