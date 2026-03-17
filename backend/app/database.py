import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

# In-memory SQLite by default (no DB files to manage during dev).
# Set DATABASE_URL env var to use a persistent DB (e.g. PostgreSQL in prod).
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite://")

_engine_kwargs: dict = {}
if SQLALCHEMY_DATABASE_URL == "sqlite://":
    # StaticPool keeps a single connection alive so all sessions share the
    # same in-memory database.
    _engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
elif SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    _engine_kwargs = {"connect_args": {"check_same_thread": False}}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

