from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ArgumentNode, Position
from ..schemas import ArgumentNodeCreate, ArgumentNodeOut

router = APIRouter(prefix="/arguments", tags=["arguments"])


@router.post("/", response_model=ArgumentNodeOut, status_code=201)
def create_argument(payload: ArgumentNodeCreate, user_id: int, db: Session = Depends(get_db)):
    # Validate position
    try:
        position = Position(payload.position)
    except ValueError:
        raise HTTPException(400, f"Invalid position: {payload.position}. Must be PRO, CONTRA or NEUTRAL")

    # Validate parent belongs to same topic
    if payload.parent_id:
        parent = db.query(ArgumentNode).filter(ArgumentNode.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(404, "Parent argument not found")
        if parent.topic_id != payload.topic_id:
            raise HTTPException(400, "Parent argument belongs to a different topic")

    node = ArgumentNode(
        topic_id=payload.topic_id,
        parent_id=payload.parent_id,
        argument_group_id=payload.argument_group_id,
        title=payload.title,
        description=payload.description,
        position=position,
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


@router.delete("/{node_id}", status_code=204)
def delete_argument(node_id: int, db: Session = Depends(get_db)):
    node = db.query(ArgumentNode).filter(ArgumentNode.id == node_id).first()
    if not node:
        raise HTTPException(404, "Argument not found")
    db.delete(node)
    db.commit()

