from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ArgumentNode, Position, StatementType, Visibility, ConflictZone, EdgeType, EdgeAdmissibility
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

    # Validate edge_admissibility (Z.4b). Defaults to ADMISSIBLE on the
    # column; we only override when the caller explicitly sets it.
    edge_admissibility = EdgeAdmissibility.ADMISSIBLE
    if payload.edge_admissibility:
        try:
            edge_admissibility = EdgeAdmissibility(payload.edge_admissibility)
        except ValueError:
            raise HTTPException(400, f"Invalid edge_admissibility: {payload.edge_admissibility}")

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
        edge_admissibility=edge_admissibility,
        # stage_added defaults to 1 (Z.1 base). Stage-4 UI passes 4 for
        # late additions ("teacher's view": noticed only when reviewing).
        stage_added=payload.stage_added or 1,
        split_from_id=payload.split_from_id,
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
    if payload.edge_admissibility is not None:
        try:
            node.edge_admissibility = EdgeAdmissibility(payload.edge_admissibility)
        except ValueError:
            raise HTTPException(400, f"Invalid edge_admissibility: {payload.edge_admissibility}")
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


# ── Z.2c: split a Stage-1 base node into a split-set ──────────────────


class SplitItem(BaseModel):
    """A single split derived from a base argument.

    `parent_id` lets the caller wire the split directly to the opponent node
    it answers (logical reference). It may be omitted and added later via
    PATCH; in that case the split inherits the base node's parent.
    """
    title: str = Field(min_length=1, max_length=300)
    description: Optional[str] = None
    position: str = "NEUTRAL"  # PRO / CONTRA / NEUTRAL
    parent_id: Optional[int] = None


class SplitRequest(BaseModel):
    splits: list[SplitItem] = Field(min_length=1)


@router.post("/{node_id}/split", response_model=list[ArgumentNodeOut], status_code=201)
def split_argument(
    node_id: int,
    payload: SplitRequest,
    user_id: int,
    db: Session = Depends(get_db),
):
    """Create a split-set from an existing Stage-1 base argument.

    Each generated child node:
      - has `stage_added = 2` (becomes visible only from Stage 2 onward)
      - has `split_from_id = node_id` (visual grouping in Stage 2)
      - has its own `parent_id` (logical reference in Stage 2/3); defaults to
        the base node's `parent_id` if the request omits it.

    The base node itself is **not** modified — Stage 3 hides it automatically
    because it is now referenced by `split_from_id`.
    """
    base = db.query(ArgumentNode).filter(ArgumentNode.id == node_id).first()
    if not base:
        raise HTTPException(404, "Base argument not found")
    if base.stage_added != 1:
        # Splits can only be derived from raw/base nodes — splitting a split
        # would create ambiguous origin chains. Discuss before relaxing.
        raise HTTPException(400, "Only Stage-1 base arguments can be split")

    created: list[ArgumentNode] = []
    for item in payload.splits:
        try:
            position = Position(item.position)
        except ValueError:
            raise HTTPException(400, f"Invalid position: {item.position}")
        parent_id = item.parent_id if item.parent_id is not None else base.parent_id
        if parent_id is not None:
            parent = db.query(ArgumentNode).filter(ArgumentNode.id == parent_id).first()
            if not parent:
                raise HTTPException(404, f"Parent argument {parent_id} not found")
            if parent.topic_id != base.topic_id:
                raise HTTPException(400, "Parent argument belongs to a different topic")
        node = ArgumentNode(
            topic_id=base.topic_id,
            parent_id=parent_id,
            title=item.title,
            description=item.description,
            position=position,
            stage_added=2,
            split_from_id=base.id,
            created_by=user_id,
        )
        db.add(node)
        created.append(node)

    db.commit()
    for n in created:
        db.refresh(n)
    return created


class SplitConnectIn(BaseModel):
    parent_id: Optional[int] = None  # None unlinks the logical reference


@router.patch("/{node_id}/connect", response_model=ArgumentNodeOut)
def connect_split(node_id: int, payload: SplitConnectIn, db: Session = Depends(get_db)):
    """Rewire a split node's logical reference (`parent_id`).

    Convenience endpoint for the Stage-2 GUI: drawing a connection from a
    split to a target opponent argument. Generic PATCH /arguments/{id} does
    not currently expose `parent_id`, and exposing it there would invite
    accidental tree restructuring on unrelated nodes.
    """
    node = db.query(ArgumentNode).filter(ArgumentNode.id == node_id).first()
    if not node:
        raise HTTPException(404, "Argument not found")
    if node.split_from_id is None:
        raise HTTPException(400, "Only split nodes can be connected via this endpoint")
    if payload.parent_id is not None:
        if payload.parent_id == node.id:
            raise HTTPException(400, "A node cannot be its own parent")
        parent = db.query(ArgumentNode).filter(ArgumentNode.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(404, "Parent argument not found")
        if parent.topic_id != node.topic_id:
            raise HTTPException(400, "Parent argument belongs to a different topic")
    node.parent_id = payload.parent_id
    db.commit()
    db.refresh(node)
    return node


# ── Z.4b: edge admissibility ──────────────────────────────────────────


class EdgeAdmissibilityIn(BaseModel):
    """Body for PATCH /arguments/{id}/edge-admissibility.

    `admissibility=None` resets the edge to the default `ADMISSIBLE` value
    so the UI can offer a one-click "Markierung entfernen" action without
    having to know the string literal.
    """
    admissibility: Optional[str] = None


@router.patch("/{node_id}/edge-admissibility", response_model=ArgumentNodeOut)
def set_edge_admissibility(node_id: int, payload: EdgeAdmissibilityIn, db: Session = Depends(get_db)):
    """Mark the parent→child edge of `node_id` as (in)admissible.

    Z.4b — see taxonomy.md §27. The child argument is **not** modified
    semantically; only the connection to its parent is annotated. We refuse
    the call when the node has no parent (a root cannot have an inadmissible
    incoming edge — there is no edge).
    """
    node = db.query(ArgumentNode).filter(ArgumentNode.id == node_id).first()
    if not node:
        raise HTTPException(404, "Argument not found")
    if node.parent_id is None:
        raise HTTPException(400, "Root arguments have no incoming edge to annotate")
    if payload.admissibility is None:
        node.edge_admissibility = EdgeAdmissibility.ADMISSIBLE
    else:
        try:
            node.edge_admissibility = EdgeAdmissibility(payload.admissibility)
        except ValueError:
            raise HTTPException(400, f"Invalid edge_admissibility: {payload.admissibility}")
    db.commit()
    db.refresh(node)
    return node


