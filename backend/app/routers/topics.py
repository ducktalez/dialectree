from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func

from ..database import get_db
from ..models import Topic, ArgumentNode, ArgumentNodeTag, Vote, Visibility
from ..schemas import TopicCreate, TopicOut, ArgumentTreeNode, TagOnNode

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


@router.delete("/{topic_id}", status_code=204)
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")
    db.delete(topic)
    db.commit()

