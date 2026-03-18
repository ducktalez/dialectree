from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DefinitionFork
from ..schemas import DefinitionForkCreate, DefinitionForkOut

router = APIRouter(prefix="/definition-forks", tags=["definition-forks"])


@router.post("/", response_model=DefinitionForkOut, status_code=201)
def create_definition_fork(payload: DefinitionForkCreate, db: Session = Depends(get_db)):
    fork = DefinitionFork(
        argument_node_id=payload.argument_node_id,
        term=payload.term,
        definition_variant=payload.definition_variant,
        description=payload.description,
    )
    db.add(fork)
    db.commit()
    db.refresh(fork)
    return fork


@router.get("/", response_model=list[DefinitionForkOut])
def list_definition_forks(argument_node_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(DefinitionFork)
    if argument_node_id:
        query = query.filter(DefinitionFork.argument_node_id == argument_node_id)
    return query.all()


@router.get("/{fork_id}", response_model=DefinitionForkOut)
def get_definition_fork(fork_id: int, db: Session = Depends(get_db)):
    fork = db.query(DefinitionFork).filter(DefinitionFork.id == fork_id).first()
    if not fork:
        raise HTTPException(404, "Definition fork not found")
    return fork


@router.delete("/{fork_id}", status_code=204)
def delete_definition_fork(fork_id: int, db: Session = Depends(get_db)):
    fork = db.query(DefinitionFork).filter(DefinitionFork.id == fork_id).first()
    if not fork:
        raise HTTPException(404, "Definition fork not found")
    db.delete(fork)
    db.commit()

