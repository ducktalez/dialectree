import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import users, topics, arguments, votes, tags, comments, evidence, labels

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Seed the in-memory DB on startup (skipped during tests)."""
    if not os.environ.get("TESTING"):
        from .database import SessionLocal
        from .models import Topic
        db = SessionLocal()
        if db.query(Topic).count() == 0:
            db.close()
            from .seed import seed
            seed()
        else:
            db.close()
    yield


app = FastAPI(
    title="Dialectree",
    version="0.1.0",
    description="Structured argument trees for better discussions",
    lifespan=lifespan,
)

# TODO: restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api")
app.include_router(topics.router, prefix="/api")
app.include_router(arguments.router, prefix="/api")
app.include_router(votes.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(evidence.router, prefix="/api")
app.include_router(labels.router, prefix="/api")


@app.get("/")
def root():
    return {"name": "Dialectree", "version": "0.1.0"}
