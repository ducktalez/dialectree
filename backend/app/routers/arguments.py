from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ArgumentNode, Position, StatementType, Visibility, ConflictZone, EdgeType
from ..schemas import ArgumentNodeCreate, ArgumentNodeOut, ArgumentNodeUpdate

router = APIRouter(prefix="/arguments", tags=["arguments"])


def _derive_position(score: float) -> Position:
    """Derive discrete position from continuous score."""
    if score < 0.33:
        return Position.CONTRA
    elif score > 0.66:
        return Position.PRO
    return Position.NEUTRAL


@router.post("/", response_model=ArgumentNodeOut, status_code=201)
def create_argument(payload: ArgumentNodeCreate, user_id: int, db: Session = Depends(get_db)):
    # Derive position from score if score is provided
    if payload.position_score is not None:
        position = _derive_position(payload.position_score)
    else:
        try:
            position = Position(payload.position)
        except ValueError:
            raise HTTPException(400, f"Invalid position: {payload.position}. Must be PRO, CONTRA or NEUTRAL")

    # Validate statement_type
    stmt_type = StatementType.UNCLASSIFIED
    if payload.statement_type:
        try:
            stmt_type = StatementType(payload.statement_type)
        except ValueError:
            raise HTTPException(400, f"Invalid statement_type: {payload.statement_type}")

    # Validate parent belongs to same topic
    if payload.parent_id:
        parent = db.query(ArgumentNode).filter(ArgumentNode.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(404, "Parent argument not found")
        if parent.topic_id != payload.topic_id:
            raise HTTPException(400, "Parent argument belongs to a different topic")

    # Validate conflict_zone
    conflict_zone = None
    if payload.conflict_zone:
        try:
            conflict_zone = ConflictZone(payload.conflict_zone)
        except ValueError:
            raise HTTPException(400, f"Invalid conflict_zone: {payload.conflict_zone}")

    # Validate edge_type
    edge_type = None
    if payload.edge_type:
        try:
            edge_type = EdgeType(payload.edge_type)
        except ValueError:
            raise HTTPException(400, f"Invalid edge_type: {payload.edge_type}")

    node = ArgumentNode(
        topic_id=payload.topic_id,
        parent_id=payload.parent_id,
        argument_group_id=payload.argument_group_id,
        title=payload.title,
        description=payload.description,
        position=position,
        position_score=payload.position_score,
        statement_type=stmt_type,
        claim=payload.claim,
        reason=payload.reason,
        example=payload.example,
        implication=payload.implication,
        conflict_zone=conflict_zone,
        edge_type=edge_type,
        is_edge_attack=payload.is_edge_attack,
        opens_conflict=payload.opens_conflict,
        created_by=user_id,
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


@router.get("/", response_model=list[ArgumentNodeOut])
def list_arguments(topic_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(ArgumentNode)
    if topic_id:
        query = query.filter(ArgumentNode.topic_id == topic_id)
    return query.all()


@router.get("/{node_id}", response_model=ArgumentNodeOut)
def get_argument(node_id: int, db: Session = Depends(get_db)):
    node = db.query(ArgumentNode).filter(ArgumentNode.id == node_id).first()
    if not node:
        raise HTTPException(404, "Argument not found")
    return node


@router.patch("/{node_id}", response_model=ArgumentNodeOut)
def update_argument(node_id: int, payload: ArgumentNodeUpdate, db: Session = Depends(get_db)):
    node = db.query(ArgumentNode).filter(ArgumentNode.id == node_id).first()
    if not node:
        raise HTTPException(404, "Argument not found")
    if payload.title is not None:
        node.title = payload.title
    if payload.description is not None:
        node.description = payload.description
    if payload.position is not None:
        try:
            node.position = Position(payload.position)
        except ValueError:
            raise HTTPException(400, f"Invalid position: {payload.position}. Must be PRO, CONTRA or NEUTRAL")
    if payload.position_score is not None:
        node.position_score = payload.position_score
        node.position = _derive_position(payload.position_score)
    if payload.statement_type is not None:
        try:
            node.statement_type = StatementType(payload.statement_type)
        except ValueError:
            raise HTTPException(400, f"Invalid statement_type: {payload.statement_type}")
    if payload.visibility is not None:
        try:
            node.visibility = Visibility(payload.visibility)
        except ValueError:
            raise HTTPException(400, f"Invalid visibility: {payload.visibility}")
    if payload.hidden_reason is not None:
        node.hidden_reason = payload.hidden_reason
    if payload.claim is not None:
        node.claim = payload.claim
    if payload.reason is not None:
        node.reason = payload.reason
    if payload.example is not None:
        node.example = payload.example
    if payload.implication is not None:
        node.implication = payload.implication
    if payload.conflict_zone is not None:
        try:
            node.conflict_zone = ConflictZone(payload.conflict_zone)
        except ValueError:
            raise HTTPException(400, f"Invalid conflict_zone: {payload.conflict_zone}")
    if payload.edge_type is not None:
        try:
            node.edge_type = EdgeType(payload.edge_type)
        except ValueError:
            raise HTTPException(400, f"Invalid edge_type: {payload.edge_type}")
    if payload.is_edge_attack is not None:
        node.is_edge_attack = payload.is_edge_attack
    if payload.opens_conflict is not None:
        node.opens_conflict = payload.opens_conflict
    db.commit()
    db.refresh(node)
    return node


@router.delete("/{node_id}", status_code=204)
def delete_argument(node_id: int, db: Session = Depends(get_db)):
    node = db.query(ArgumentNode).filter(ArgumentNode.id == node_id).first()
    if not node:
        raise HTTPException(404, "Argument not found")
    db.delete(node)
    db.commit()

