from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import NodeLabel, LabelType
from ..schemas import NodeLabelCreate, NodeLabelOut

router = APIRouter(prefix="/labels", tags=["labels"])


@router.post("/", response_model=NodeLabelOut, status_code=201)
def create_label(payload: NodeLabelCreate, user_id: int, db: Session = Depends(get_db)):
    try:
        label_type = LabelType(payload.label_type)
    except ValueError:
        raise HTTPException(400, f"Invalid label type: {payload.label_type}")

    if not payload.justification.strip():
        raise HTTPException(400, "Justification is required for labels")

    label = NodeLabel(
        argument_node_id=payload.argument_node_id,
        label_type=label_type,
        justification=payload.justification,
        created_by=user_id,
    )
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


@router.get("/", response_model=list[NodeLabelOut])
def list_labels(argument_node_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(NodeLabel)
    if argument_node_id:
        query = query.filter(NodeLabel.argument_node_id == argument_node_id)
    return query.all()


@router.delete("/{label_id}", status_code=204)
def delete_label(label_id: int, db: Session = Depends(get_db)):
    label = db.query(NodeLabel).filter(NodeLabel.id == label_id).first()
    if not label:
        raise HTTPException(404, "Label not found")
    db.delete(label)
    db.commit()

