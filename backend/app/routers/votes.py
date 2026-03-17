from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Vote
from ..schemas import VoteCreate, VoteOut

router = APIRouter(prefix="/votes", tags=["votes"])


@router.post("/", response_model=VoteOut, status_code=201)
def cast_vote(payload: VoteCreate, user_id: int, db: Session = Depends(get_db)):
    if payload.value not in (1, -1):
        raise HTTPException(400, "Vote value must be 1 or -1")

    existing = db.query(Vote).filter(
        Vote.user_id == user_id,
        Vote.argument_node_id == payload.argument_node_id,
    ).first()

    if existing:
        existing.value = payload.value
        db.commit()
        db.refresh(existing)
        return existing

    vote = Vote(
        user_id=user_id,
        argument_node_id=payload.argument_node_id,
        value=payload.value,
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote


@router.get("/", response_model=list[VoteOut])
def list_votes(argument_node_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Vote)
    if argument_node_id:
        query = query.filter(Vote.argument_node_id == argument_node_id)
    return query.all()


@router.delete("/{vote_id}", status_code=204)
def delete_vote(vote_id: int, db: Session = Depends(get_db)):
    vote = db.query(Vote).filter(Vote.id == vote_id).first()
    if not vote:
        raise HTTPException(404, "Vote not found")
    db.delete(vote)
    db.commit()

