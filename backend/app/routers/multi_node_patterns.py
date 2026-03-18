from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import MultiNodePattern, ArgumentNode, PatternType
from ..schemas import MultiNodePatternCreate, MultiNodePatternOut

router = APIRouter(prefix="/patterns", tags=["patterns"])


@router.post("/", response_model=MultiNodePatternOut, status_code=201)
def create_pattern(payload: MultiNodePatternCreate, user_id: int, db: Session = Depends(get_db)):
    try:
        pattern_type = PatternType(payload.pattern_type)
    except ValueError:
        raise HTTPException(400, f"Invalid pattern type: {payload.pattern_type}")

    members = []
    for nid in payload.member_ids:
        node = db.query(ArgumentNode).filter(ArgumentNode.id == nid).first()
        if not node:
            raise HTTPException(404, f"Argument node {nid} not found")
        if node.topic_id != payload.topic_id:
            raise HTTPException(400, f"Argument node {nid} belongs to a different topic")
        members.append(node)

    pattern = MultiNodePattern(
        topic_id=payload.topic_id,
        name=payload.name,
        pattern_type=pattern_type,
        description=payload.description,
        created_by=user_id,
    )
    pattern.members = members
    db.add(pattern)
    db.commit()
    db.refresh(pattern)

    return _to_out(pattern)


@router.get("/", response_model=list[MultiNodePatternOut])
def list_patterns(topic_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(MultiNodePattern)
    if topic_id:
        query = query.filter(MultiNodePattern.topic_id == topic_id)
    return [_to_out(p) for p in query.all()]


@router.get("/{pattern_id}", response_model=MultiNodePatternOut)
def get_pattern(pattern_id: int, db: Session = Depends(get_db)):
    pattern = db.query(MultiNodePattern).filter(MultiNodePattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(404, "Pattern not found")
    return _to_out(pattern)


@router.delete("/{pattern_id}", status_code=204)
def delete_pattern(pattern_id: int, db: Session = Depends(get_db)):
    pattern = db.query(MultiNodePattern).filter(MultiNodePattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(404, "Pattern not found")
    db.delete(pattern)
    db.commit()


def _to_out(pattern: MultiNodePattern) -> MultiNodePatternOut:
    """Convert ORM model to response schema, extracting member IDs."""
    return MultiNodePatternOut(
        id=pattern.id,
        topic_id=pattern.topic_id,
        name=pattern.name,
        pattern_type=pattern.pattern_type.value,
        description=pattern.description,
        created_by=pattern.created_by,
        member_ids=[m.id for m in pattern.members],
        created_at=pattern.created_at,
    )

