from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ArgumentNode, DefinitionFork
from ..schemas import DefinitionForkCreate, DefinitionForkOut, DefinitionForkUpdate

router = APIRouter(prefix="/definition-forks", tags=["definition-forks"])


@router.post("/", response_model=DefinitionForkOut, status_code=201)
def create_definition_fork(payload: DefinitionForkCreate, db: Session = Depends(get_db)):
    # Validate FK explicitly so the API returns 404 (not 500/IntegrityError) for
    # dangling argument_node_id values. Mirrors the pattern used by sources.
    if db.get(ArgumentNode, payload.argument_node_id) is None:
        raise HTTPException(404, f"Argument {payload.argument_node_id} not found")
    fork = DefinitionFork(
        argument_node_id=payload.argument_node_id,
        term=payload.term.strip(),
        definition_variant=payload.definition_variant.strip(),
        description=(payload.description or None) and payload.description.strip(),
    )
    db.add(fork)
    db.commit()
    db.refresh(fork)
    return fork


@router.get("/", response_model=list[DefinitionForkOut])
def list_definition_forks(
    argument_node_id: int | None = None,
    topic_id: int | None = None,
    db: Session = Depends(get_db),
):
    """List forks. Filter either by single argument or by entire topic.

    `topic_id` filter is what the Zickzack UI uses to populate fork badges for
    every visible card in one request instead of one-call-per-node.
    """
    query = db.query(DefinitionFork)
    if argument_node_id is not None:
        query = query.filter(DefinitionFork.argument_node_id == argument_node_id)
    if topic_id is not None:
        query = query.join(ArgumentNode).filter(ArgumentNode.topic_id == topic_id)
    return query.order_by(DefinitionFork.id).all()


@router.get("/{fork_id}", response_model=DefinitionForkOut)
def get_definition_fork(fork_id: int, db: Session = Depends(get_db)):
    fork = db.get(DefinitionFork, fork_id)
    if not fork:
        raise HTTPException(404, "Definition fork not found")
    return fork


@router.patch("/{fork_id}", response_model=DefinitionForkOut)
def update_definition_fork(
    fork_id: int, payload: DefinitionForkUpdate, db: Session = Depends(get_db),
):
    fork = db.get(DefinitionFork, fork_id)
    if not fork:
        raise HTTPException(404, "Definition fork not found")
    changes = payload.model_dump(exclude_unset=True)
    if "term" in changes:
        t = (changes["term"] or "").strip()
        if not t:
            raise HTTPException(400, "term must not be empty")
        fork.term = t
    if "definition_variant" in changes:
        v = (changes["definition_variant"] or "").strip()
        if not v:
            raise HTTPException(400, "definition_variant must not be empty")
        fork.definition_variant = v
    if "description" in changes:
        d = changes["description"]
        fork.description = (d or None) and d.strip()
    db.commit()
    db.refresh(fork)
    return fork


@router.delete("/{fork_id}", status_code=204)
def delete_definition_fork(fork_id: int, db: Session = Depends(get_db)):
    fork = db.get(DefinitionFork, fork_id)
    if not fork:
        raise HTTPException(404, "Definition fork not found")
    db.delete(fork)
    db.commit()



