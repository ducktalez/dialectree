from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func

from ..database import get_db
from ..models import Topic, ArgumentNode, ArgumentNodeTag, Vote, Visibility
from ..schemas import (
    TopicCreate, TopicOut, ArgumentTreeNode, TagOnNode,
    ZigzagStepOut, ZigzagTopicInfo, ZigzagResponse, TranscriptResponse, TranscriptUpdate,
)

router = APIRouter(prefix="/topics", tags=["topics"])


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


@router.post("/", response_model=TopicOut, status_code=201)
def create_topic(payload: TopicCreate, user_id: int, db: Session = Depends(get_db)):
    # TODO: get user_id from auth token
    topic = Topic(title=payload.title, description=payload.description, created_by=user_id)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/", response_model=list[TopicOut])
def list_topics(db: Session = Depends(get_db)):
    return db.query(Topic).all()


@router.get("/{topic_id}", response_model=TopicOut)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")
    return topic


@router.patch("/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: int, payload: TopicUpdate, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")
    if payload.title is not None:
        topic.title = payload.title
    if payload.description is not None:
        topic.description = payload.description
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/{topic_id}/tree", response_model=list[ArgumentTreeNode])
def get_argument_tree(topic_id: int, show_hidden: bool = False, db: Session = Depends(get_db)):
    """Returns the full argument tree for a topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")

    query = (
        db.query(ArgumentNode)
        .filter(ArgumentNode.topic_id == topic_id)
        .options(
            selectinload(ArgumentNode.tag_links).selectinload(ArgumentNodeTag.tag),
            selectinload(ArgumentNode.labels),
            selectinload(ArgumentNode.evidence),
            selectinload(ArgumentNode.comments),
        )
    )
    if not show_hidden:
        query = query.filter(ArgumentNode.visibility == Visibility.VISIBLE)

    nodes = query.all()

    # Calculate vote scores
    vote_scores = {}
    for node in nodes:
        score = db.query(func.coalesce(func.sum(Vote.value), 0)).filter(
            Vote.argument_node_id == node.id
        ).scalar()
        vote_scores[node.id] = score

    # Build tree nodes
    node_map = {}
    for node in nodes:
        node_map[node.id] = ArgumentTreeNode(
            id=node.id,
            title=node.title,
            description=node.description,
            position=node.position.value,
            position_score=node.position_score,
            statement_type=node.statement_type.value if node.statement_type else "UNCLASSIFIED",
            visibility=node.visibility.value if node.visibility else "VISIBLE",
            hidden_reason=node.hidden_reason,
            parent_id=node.parent_id,
            argument_group_id=node.argument_group_id,
            claim=node.claim,
            reason=node.reason,
            example=node.example,
            implication=node.implication,
            conflict_zone=node.conflict_zone.value if node.conflict_zone else None,
            edge_type=node.edge_type.value if node.edge_type else None,
            is_edge_attack=node.is_edge_attack or False,
            opens_conflict=node.opens_conflict,
            created_by=node.created_by,
            vote_score=vote_scores.get(node.id, 0),
            tags=[
                TagOnNode(
                    tag_id=link.tag.id,
                    tag_name=link.tag.name,
                    category=link.tag.category.value if link.tag.category else None,
                    moral_foundation=link.tag.moral_foundation.value if link.tag.moral_foundation else None,
                    origin=link.origin.value if link.origin else "USER",
                )
                for link in node.tag_links
            ],
            labels=[lb.label_type.value for lb in node.labels],
            evidence_count=len(node.evidence),
            comment_count=len(node.comments),
            children=[],
        )

    roots = []
    for node in nodes:
        tree_node = node_map[node.id]
        if node.parent_id and node.parent_id in node_map:
            node_map[node.parent_id].children.append(tree_node)
        else:
            roots.append(tree_node)

    return roots


@router.get("/{topic_id}/transcript", response_model=TranscriptResponse)
def get_transcript(topic_id: int, db: Session = Depends(get_db)):
    """Returns the raw YAML transcript for Stage 0 of the refinement model."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")
    return TranscriptResponse(
        topic_id=topic.id,
        topic_title=topic.title,
        transcript_yaml=topic.transcript_yaml,
    )


@router.put("/{topic_id}/transcript", response_model=TranscriptResponse)
def update_transcript(topic_id: int, payload: TranscriptUpdate, db: Session = Depends(get_db)):
    """Updates the raw YAML transcript for Stage 0. Replaces the full content."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")
    topic.transcript_yaml = payload.transcript_yaml
    db.commit()
    db.refresh(topic)
    return TranscriptResponse(
        topic_id=topic.id,
        topic_title=topic.title,
        transcript_yaml=topic.transcript_yaml,
    )


@router.get("/{topic_id}/zigzag", response_model=ZigzagResponse)
def get_zigzag(
    topic_id: int,
    stage: int = Query(default=2, ge=1, le=5, description="Refinement stage filter (1=base only, 2=with splits)"),
    db: Session = Depends(get_db),
):
    """Returns a flat, chronologically sorted list of arguments for the zigzag view.
    
    stage parameter filters nodes by stage_added <= stage:
      1 = base arguments only (one per turn, the red thread chain)
      2 = base + split sub-arguments (default, full view)
      3-5 = same as 2 for now (stages 3-5 not yet implemented)
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")

    nodes = (
        db.query(ArgumentNode)
        .filter(
            ArgumentNode.topic_id == topic_id,
            ArgumentNode.visibility == Visibility.VISIBLE,
            ArgumentNode.stage_added <= stage,
        )
        .order_by(ArgumentNode.created_at.asc())
        .all()
    )

    # Pre-compute vote scores
    vote_scores: dict[int, int] = {}
    for node in nodes:
        score = db.query(func.coalesce(func.sum(Vote.value), 0)).filter(
            Vote.argument_node_id == node.id
        ).scalar()
        vote_scores[node.id] = score

    # Group by parent_id for sibling lookup (only among visible nodes in this stage)
    node_ids = {n.id for n in nodes}
    parent_groups: dict[int | None, list[int]] = {}
    for node in nodes:
        parent_groups.setdefault(node.parent_id, []).append(node.id)

    steps = []
    for node in nodes:
        siblings = [sid for sid in parent_groups.get(node.parent_id, []) if sid != node.id]
        steps.append(ZigzagStepOut(
            id=node.id,
            parent_id=node.parent_id,
            title=node.title,
            description=node.description,
            position=node.position.value,
            position_score=node.position_score,
            conflict_zone=node.conflict_zone.value if node.conflict_zone else None,
            edge_type=node.edge_type.value if node.edge_type else None,
            is_edge_attack=node.is_edge_attack or False,
            opens_conflict=node.opens_conflict,
            stage_added=node.stage_added,
            split_from_id=node.split_from_id,
            vote_score=vote_scores.get(node.id, 0),
            sibling_ids=siblings,
            created_at=node.created_at,
        ))

    return ZigzagResponse(
        topic=ZigzagTopicInfo(id=topic.id, title=topic.title),
        stage=stage,
        steps=steps,
    )


@router.delete("/{topic_id}", status_code=204)
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")
    db.delete(topic)
    db.commit()

