from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Topic, ArgumentNode, Vote
from ..schemas import TopicCreate, TopicOut, ArgumentTreeNode

router = APIRouter(prefix="/topics", tags=["topics"])


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


@router.get("/{topic_id}/tree", response_model=list[ArgumentTreeNode])
def get_argument_tree(topic_id: int, db: Session = Depends(get_db)):
    """Returns the full argument tree for a topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")

    nodes = db.query(ArgumentNode).filter(ArgumentNode.topic_id == topic_id).all()

    # Calculate vote scores
    vote_scores = {}
    for node in nodes:
        score = db.query(func.coalesce(func.sum(Vote.value), 0)).filter(
            Vote.argument_node_id == node.id
        ).scalar()
        vote_scores[node.id] = score

    # Build tree
    node_map: dict[int, ArgumentTreeNode] = {}
    for node in nodes:
        node_map[node.id] = ArgumentTreeNode(
            id=node.id,
            title=node.title,
            description=node.description,
            position=node.position.value,
            parent_id=node.parent_id,
            vote_score=vote_scores.get(node.id, 0),
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

