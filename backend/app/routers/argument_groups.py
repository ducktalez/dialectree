from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ArgumentGroup, ArgumentNode
from ..schemas import ArgumentGroupCreate, ArgumentGroupOut, ArgumentGroupUpdate, ArgumentGroupMerge

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


@router.post("/{group_id}/merge", status_code=200)
def merge_arguments(group_id: int, payload: ArgumentGroupMerge, db: Session = Depends(get_db)):
    """Assign multiple ArgumentNodes to this group."""
    group = db.query(ArgumentGroup).filter(ArgumentGroup.id == group_id).first()
    if not group:
        raise HTTPException(404, "Argument group not found")

    nodes = db.query(ArgumentNode).filter(
        ArgumentNode.id.in_(payload.argument_node_ids)
    ).all()

    if len(nodes) != len(payload.argument_node_ids):
        found_ids = {n.id for n in nodes}
        missing = [nid for nid in payload.argument_node_ids if nid not in found_ids]
        raise HTTPException(404, f"Argument nodes not found: {missing}")

    # All nodes must belong to the same topic as the group
    wrong_topic = [n.id for n in nodes if n.topic_id != group.topic_id]
    if wrong_topic:
        raise HTTPException(400, f"Nodes not in group's topic: {wrong_topic}")

    for node in nodes:
        node.argument_group_id = group.id
    db.commit()

    return {"merged": len(nodes), "group_id": group.id}


@router.post("/{group_id}/unmerge/{node_id}", status_code=200)
def unmerge_argument(group_id: int, node_id: int, db: Session = Depends(get_db)):
    """Remove a single ArgumentNode from this group."""
    group = db.query(ArgumentGroup).filter(ArgumentGroup.id == group_id).first()
    if not group:
        raise HTTPException(404, "Argument group not found")

    node = db.query(ArgumentNode).filter(ArgumentNode.id == node_id).first()
    if not node:
        raise HTTPException(404, "Argument node not found")

    if node.argument_group_id != group.id:
        raise HTTPException(400, f"Node {node_id} is not in group {group_id}")

    node.argument_group_id = None
    db.commit()

    return {"unmerged": node_id, "group_id": group.id}


@router.delete("/{group_id}", status_code=204)
def delete_argument_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(ArgumentGroup).filter(ArgumentGroup.id == group_id).first()
    if not group:
        raise HTTPException(404, "Argument group not found")
    db.delete(group)
    db.commit()

