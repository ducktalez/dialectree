from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Tag, ArgumentNode, ArgumentNodeTag, TagVote, MoralFoundation, TagCategory, TagOrigin
from ..schemas import TagCreate, TagOut, TagAssign, TagVoteCreate, TagVoteOut

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagOut, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    existing = db.query(Tag).filter(Tag.name == payload.name).first()
    if existing:
        raise HTTPException(400, "Tag already exists")

    moral = None
    if payload.moral_foundation:
        try:
            moral = MoralFoundation(payload.moral_foundation)
        except ValueError:
            raise HTTPException(400, f"Invalid moral foundation: {payload.moral_foundation}")

    category = TagCategory.OTHER
    if payload.category:
        try:
            category = TagCategory(payload.category)
        except ValueError:
            raise HTTPException(400, f"Invalid tag category: {payload.category}")

    tag = Tag(name=payload.name, moral_foundation=moral, category=category)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.get("/", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()


@router.post("/assign", status_code=201)
def assign_tag(payload: TagAssign, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == payload.tag_id).first()
    if not tag:
        raise HTTPException(404, "Tag not found")
    node = db.query(ArgumentNode).filter(ArgumentNode.id == payload.argument_node_id).first()
    if not node:
        raise HTTPException(404, "Argument not found")

    existing = db.query(ArgumentNodeTag).filter(
        ArgumentNodeTag.argument_node_id == payload.argument_node_id,
        ArgumentNodeTag.tag_id == payload.tag_id,
    ).first()
    if existing:
        raise HTTPException(400, "Tag already assigned")

    # Validate origin
    origin = TagOrigin.USER
    if payload.origin:
        try:
            origin = TagOrigin(payload.origin)
        except ValueError:
            raise HTTPException(400, f"Invalid tag origin: {payload.origin}")

    link = ArgumentNodeTag(
        argument_node_id=payload.argument_node_id,
        tag_id=payload.tag_id,
        origin=origin,
    )
    db.add(link)
    db.commit()
    return {"status": "assigned"}


@router.post("/vote", response_model=TagVoteOut, status_code=201)
def vote_on_tag(payload: TagVoteCreate, user_id: int, db: Session = Depends(get_db)):
    if payload.value not in (1, -1):
        raise HTTPException(400, "Vote value must be 1 or -1")

    existing = db.query(TagVote).filter(
        TagVote.user_id == user_id,
        TagVote.tag_id == payload.tag_id,
        TagVote.argument_node_id == payload.argument_node_id,
    ).first()

    if existing:
        existing.value = payload.value
        db.commit()
        db.refresh(existing)
        return existing

    tv = TagVote(
        user_id=user_id,
        tag_id=payload.tag_id,
        argument_node_id=payload.argument_node_id,
        value=payload.value,
    )
    db.add(tv)
    db.commit()
    db.refresh(tv)
    return tv

