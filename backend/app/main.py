import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import engine, Base
from .routers import (
    users, topics, arguments, votes, tags, comments, evidence, labels,
    argument_groups, definition_forks, multi_node_patterns, sources,
)

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
app.include_router(argument_groups.router, prefix="/api")
app.include_router(definition_forks.router, prefix="/api")
app.include_router(multi_node_patterns.router, prefix="/api")
app.include_router(sources.router, prefix="/api")

_STATIC_DIR = Path(__file__).parent / "static"

# Serve thumbnails / source assets under /static/sources/<file>.
# Other static pages are mapped via explicit FileResponse routes below.
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/", response_class=FileResponse)
def root():
    """Serves the Zickzack view as main entry point."""
    return FileResponse(_STATIC_DIR / "zickzack.html")



@app.get("/dialog", response_class=FileResponse)
def dialog_view():
    """Zig-zag dialectical dialogue visualisation."""
    return FileResponse(_STATIC_DIR / "dialog.html")


@app.get("/zickzack", response_class=FileResponse)
def zickzack_view():
    """SVG-based zig-zag argument strength visualisation (alias for /)."""
    return FileResponse(_STATIC_DIR / "zickzack.html")


@app.get("/quellen", response_class=FileResponse)
def quellen_view():
    """Quellensammlung – central evidence/source collection (placeholder page)."""
    return FileResponse(_STATIC_DIR / "quellen.html")


@app.get("/sw.js", response_class=FileResponse)
def service_worker():
    """Dummy service worker to prevent 404."""
    return FileResponse(_STATIC_DIR / "sw.js", media_type="application/javascript")


@app.get("/favicon.ico", response_class=FileResponse)
def favicon():
    """Favicon to prevent 404."""
    return FileResponse(_STATIC_DIR / "favicon.svg", media_type="image/svg+xml")


