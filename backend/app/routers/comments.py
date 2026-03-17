from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Comment
from ..schemas import CommentCreate, CommentOut

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentOut, status_code=201)
def create_comment(payload: CommentCreate, user_id: int, db: Session = Depends(get_db)):
    comment = Comment(
        argument_node_id=payload.argument_node_id,
        user_id=user_id,
        text=payload.text,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/", response_model=list[CommentOut])
def list_comments(argument_node_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Comment)
    if argument_node_id:
        query = query.filter(Comment.argument_node_id == argument_node_id)
    return query.all()


@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(404, "Comment not found")
    db.delete(comment)
    db.commit()

