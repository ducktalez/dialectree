from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Evidence, EvidenceType
from ..schemas import EvidenceCreate, EvidenceOut

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/", response_model=EvidenceOut, status_code=201)
def create_evidence(payload: EvidenceCreate, user_id: int, db: Session = Depends(get_db)):
    try:
        ev_type = EvidenceType(payload.evidence_type)
    except ValueError:
        raise HTTPException(400, f"Invalid evidence type: {payload.evidence_type}")

    if payload.quality_score is not None and not (0.0 <= payload.quality_score <= 1.0):
        raise HTTPException(400, "quality_score must be between 0.0 and 1.0")

    evidence = Evidence(
        argument_node_id=payload.argument_node_id,
        evidence_type=ev_type,
        url=payload.url,
        title=payload.title,
        description=payload.description,
        quality_score=payload.quality_score,
        created_by=user_id,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


@router.get("/", response_model=list[EvidenceOut])
def list_evidence(argument_node_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Evidence)
    if argument_node_id:
        query = query.filter(Evidence.argument_node_id == argument_node_id)
    return query.all()


@router.delete("/{evidence_id}", status_code=204)
def delete_evidence(evidence_id: int, db: Session = Depends(get_db)):
    ev = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(404, "Evidence not found")
    db.delete(ev)
    db.commit()

