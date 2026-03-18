from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ArgumentGroup
from ..schemas import ArgumentGroupCreate, ArgumentGroupOut, ArgumentGroupUpdate

router = APIRouter(prefix="/argument-groups", tags=["argument-groups"])


@router.post("/", response_model=ArgumentGroupOut, status_code=201)
def create_argument_group(payload: ArgumentGroupCreate, db: Session = Depends(get_db)):
    group = ArgumentGroup(
        topic_id=payload.topic_id,
        canonical_title=payload.canonical_title,
        description=payload.description,
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.get("/", response_model=list[ArgumentGroupOut])
def list_argument_groups(topic_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(ArgumentGroup)
    if topic_id:
        query = query.filter(ArgumentGroup.topic_id == topic_id)
    return query.all()


@router.get("/{group_id}", response_model=ArgumentGroupOut)
def get_argument_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(ArgumentGroup).filter(ArgumentGroup.id == group_id).first()
    if not group:
        raise HTTPException(404, "Argument group not found")
    return group


@router.patch("/{group_id}", response_model=ArgumentGroupOut)
def update_argument_group(group_id: int, payload: ArgumentGroupUpdate, db: Session = Depends(get_db)):
    group = db.query(ArgumentGroup).filter(ArgumentGroup.id == group_id).first()
    if not group:
        raise HTTPException(404, "Argument group not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    db.commit()
    db.refresh(group)
    return group


@router.delete("/{group_id}", status_code=204)
def delete_argument_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(ArgumentGroup).filter(ArgumentGroup.id == group_id).first()
    if not group:
        raise HTTPException(404, "Argument group not found")
    db.delete(group)
    db.commit()

