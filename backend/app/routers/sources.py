"""Source collection (Quellensammlung) — SQLAlchemy-backed.

Promoted from a JSON file to proper SQL models (`Source`, `SourceTag`,
`SourceComment`, `SourceUsage`) so usage links to argument nodes are real
foreign keys and tag deduplication is enforced at the schema level.

Endpoints (same surface as the JSON era so the frontend keeps working):
- GET  /api/sources/           list with optional filters
- GET  /api/sources/tags       aggregated tag list with counts
- GET  /api/sources/similar    lightweight Jaccard-based dedup suggestions
- GET  /api/sources/{id}       single source incl. comments + usages
- POST /api/sources/           create source (multipart)
- POST /api/sources/{id}/comments
- POST /api/sources/{id}/usages
- POST /api/sources/{id}/vote  aggregate vote counter transition
- PATCH /api/sources/{id}
- DELETE /api/sources/{id}
- DELETE /api/sources/{id}/comments/{index}    index-based for FE simplicity
- DELETE /api/sources/{id}/usages/{index}

Per-user vote tracking and auth are still deferred — see implementation-plan.md
(Phase 1 → Auth, Phase 2 → Per-user vote tracking).
"""
from __future__ import annotations

import re as _re
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import (
    ArgumentNode,
    Source,
    SourceComment,
    SourceKind,
    SourceTag,
    SourceUsage,
)

router = APIRouter(prefix="/sources", tags=["sources"])

# Thumbnail / media upload directory. Reassigned by tests via monkeypatch, so
# downstream helpers must look up the *current* value each call instead of
# capturing it at import time.
_THUMB_DIR = Path(__file__).parent.parent / "static" / "sources"


def _media_dir() -> Path:
    return _THUMB_DIR / "media"


_ALLOWED_THUMB_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
_ALLOWED_VIDEO_EXT = {".mp4", ".webm", ".ogg", ".mov", ".m4v"}
_ALLOWED_AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".oga", ".flac"}
_ALLOWED_KINDS = {k.value for k in SourceKind}


# ── Serialisation helpers ────────────────────────────────────────────────────

def _tag_names(src: Source) -> list[str]:
    return [t.name for t in src.tags]


def _to_detail(src: Source) -> dict:
    """Full detail payload (includes comments + usages)."""
    return {
        "id": src.id,
        "title": src.title,
        "kind": src.kind.value,
        "url": src.url,
        "description": src.description,
        "thumbnail": src.thumbnail,
        "media_url": src.media_url,
        "tags": _tag_names(src),
        "created_at": src.created_at.isoformat() if src.created_at else None,
        "up": src.up,
        "down": src.down,
        "score": src.up - src.down,
        "comments": [
            {
                "user": c.user,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "text": c.text,
            }
            for c in src.comments
        ],
        "usages": [
            {
                "context": u.context,
                "argument_id": u.argument_id,
                "note": u.note,
            }
            for u in src.usages
        ],
    }


def _to_list_item(src: Source) -> dict:
    """List payload: heavy fields stripped, but enough metadata for tiles."""
    return {
        "id": src.id,
        "title": src.title,
        "kind": src.kind.value,
        "thumbnail": src.thumbnail,
        "tags": _tag_names(src),
        "created_at": src.created_at.isoformat() if src.created_at else None,
        "comment_count": len(src.comments),
        "usage_count": len(src.usages),
        "up": src.up,
        "down": src.down,
        "score": src.up - src.down,
        "url": src.url,
        "media_url": src.media_url,
    }


def _get_source_or_404(db: Session, source_id: int) -> Source:
    src = db.get(Source, source_id)
    if not src:
        raise HTTPException(404, f"Source {source_id} not found")
    return src


def _get_or_create_tag(db: Session, name: str) -> SourceTag:
    """Tag names are unique per `SourceTag.name`. Reuse if exists, else create."""
    tag = db.query(SourceTag).filter(SourceTag.name == name).first()
    if tag is None:
        tag = SourceTag(name=name)
        db.add(tag)
        db.flush()  # populate id without committing the surrounding tx
    return tag


def _parse_tag_csv(raw: str | None) -> list[str]:
    """Comma-separated input → trimmed, de-duplicated, order-preserving list."""
    if not raw:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for piece in raw.split(","):
        t = piece.strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


# ── Placeholder thumbnail ────────────────────────────────────────────────────

def _generate_placeholder_svg(path: Path, title: str, kind: str) -> None:
    """Minimal placeholder SVG so every source has a visual tile."""
    import html as _html
    safe_title = _html.escape((title or "")[:60])
    kind_label = {
        "QUOTE": "💬 ZITAT", "VIDEO": "🎬 VIDEO", "AUDIO": "🎧 AUDIO",
        "PAPER": "📄 PAPER", "TWEET": "𝕏 TWEET", "IMAGE": "🖼️ BILD", "TEXT": "📝 TEXT",
    }.get(kind.upper(), kind.upper())
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
  <rect width="400" height="400" fill="#1c2128"/>
  <text x="200" y="80" text-anchor="middle" fill="#58a6ff" font-family="system-ui,sans-serif" font-size="20" font-weight="700">{kind_label}</text>
  <foreignObject x="20" y="120" width="360" height="240">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:system-ui,sans-serif;font-size:22px;color:#e6edf3;line-height:1.3;text-align:center">{safe_title}</div>
  </foreignObject>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


# ── Similarity helpers (lightweight, no embeddings) ──────────────────────────

# Small German + English stop-word list. Goal is rough duplicate detection
# in the "Neue Quelle" modal, not search-engine quality.
_STOP = frozenset({
    "der", "die", "das", "und", "oder", "ist", "im", "in", "ein", "eine",
    "den", "dem", "des", "zu", "zur", "zum", "auf", "von", "vom", "mit",
    "für", "fur", "nicht", "nur", "auch", "aber", "als", "an", "am", "bei",
    "the", "and", "or", "is", "a", "an", "of", "to", "for", "on", "in",
    "with", "by", "at", "as",
})


def _tokens(text: str) -> set[str]:
    if not text:
        return set()
    parts = _re.split(r"[^\wäöüß]+", text.lower())
    return {p for p in parts if len(p) >= 3 and p not in _STOP}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


# ── GET endpoints ────────────────────────────────────────────────────────────


@router.get("/tags")
def list_tags(db: Session = Depends(get_db)) -> list[dict]:
    """All tags with usage counts. Used by the frontend filter bar."""
    rows = (
        db.query(SourceTag.name, func.count(Source.id))
        .join(SourceTag.sources)
        .group_by(SourceTag.id)
        .all()
    )

    # Stable sort: TOPIC:* tags grouped at the end, otherwise by count desc.
    def _key(item):
        name, cnt = item
        is_topic = 1 if name.startswith("TOPIC:") else 0
        return (is_topic, -cnt, name)

    return [{"tag": name, "count": cnt} for name, cnt in sorted(rows, key=_key)]


@router.get("/similar")
def find_similar(
    title: str = Query(default=""),
    description: str = Query(default=""),
    threshold: float = Query(default=0.25, ge=0.0, le=1.0),
    limit: int = Query(default=5, ge=1, le=50),
    exclude_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Lightweight duplicate suggestions for the 'new source' modal.

    Token-set Jaccard similarity over title + description. Stand-in for
    embedding-based dedup (post-dev: replace with vector search).
    """
    candidate = _tokens(title) | _tokens(description)
    if not candidate:
        return []
    scored: list[tuple[float, Source]] = []
    for s in db.query(Source).all():
        if exclude_id is not None and s.id == exclude_id:
            continue
        their = _tokens(s.title or "") | _tokens(s.description or "")
        score = _jaccard(candidate, their)
        if score >= threshold:
            scored.append((score, s))
    scored.sort(key=lambda x: (-x[0], x[1].id))
    return [
        {
            "id": s.id,
            "title": s.title,
            "kind": s.kind.value,
            "thumbnail": s.thumbnail,
            "similarity": round(score, 3),
        }
        for score, s in scored[:limit]
    ]


@router.get("/")
def list_sources(
    tag: list[str] | None = Query(default=None, description="Filter by tag (repeatable, AND-combined)"),
    kind: str | None = None,
    q: str | None = Query(default=None, description="Full-text search over title + description"),
    argument_id: int | None = Query(default=None, description="Only sources whose usages reference this argument id"),
    sort: str = Query(default="neu", pattern="^(neu|alt|titel|top|kontrovers|zufall)$"),
    db: Session = Depends(get_db),
) -> list[dict]:
    # Eager-load relationships used in the response shape so we don't hit N+1.
    query = db.query(Source).options(
        selectinload(Source.tags),
        selectinload(Source.comments),
        selectinload(Source.usages),
    )
    items: list[Source] = query.all()

    if tag:
        wanted = {t.upper() for t in tag}
        items = [s for s in items if wanted.issubset({t.name.upper() for t in s.tags})]
    if kind:
        items = [s for s in items if s.kind.value.upper() == kind.upper()]
    if argument_id is not None:
        items = [s for s in items if any(u.argument_id == argument_id for u in s.usages)]
    if q:
        needle = q.lower()
        items = [
            s for s in items
            if needle in (s.title or "").lower()
            or needle in (s.description or "").lower()
        ]

    if sort == "neu":
        items.sort(key=lambda s: (s.created_at, s.id), reverse=True)
    elif sort == "alt":
        items.sort(key=lambda s: (s.created_at, s.id))
    elif sort == "titel":
        items.sort(key=lambda s: (s.title or "").lower())
    elif sort == "top":
        items.sort(key=lambda s: (s.up - s.down, s.id), reverse=True)
    elif sort == "kontrovers":
        items.sort(
            key=lambda s: (s.up + s.down, -abs(s.up - s.down)),
            reverse=True,
        )
    elif sort == "zufall":
        import random as _r
        _r.shuffle(items)

    return [_to_list_item(s) for s in items]


@router.get("/{source_id}")
def get_source(source_id: int, db: Session = Depends(get_db)) -> dict:
    return _to_detail(_get_source_or_404(db, source_id))


# ── POST endpoints ───────────────────────────────────────────────────────────


@router.post("/", status_code=201)
async def create_source(
    title: str = Form(..., min_length=1),
    kind: str = Form(...),
    url: str | None = Form(None),
    description: str | None = Form(None),
    # Comma-separated. Topic tags use "TOPIC:<SLUG>" convention.
    tags: str = Form(""),
    thumbnail: UploadFile | None = File(None),
    media: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> dict:
    kind_upper = kind.upper()
    if kind_upper not in _ALLOWED_KINDS:
        raise HTTPException(400, f"Invalid kind: {kind_upper}. Allowed: {sorted(_ALLOWED_KINDS)}")

    # Validate uploaded files *before* creating the row so an early 400 doesn't
    # leave an orphan Source behind.
    thumb_ext: str | None = None
    if thumbnail is not None and thumbnail.filename:
        thumb_ext = Path(thumbnail.filename).suffix.lower()
        if thumb_ext not in _ALLOWED_THUMB_EXT:
            raise HTTPException(400, f"Unsupported thumbnail format: {thumb_ext}")
    media_ext: str | None = None
    if media is not None and media.filename:
        media_ext = Path(media.filename).suffix.lower()
        if media_ext not in (_ALLOWED_VIDEO_EXT | _ALLOWED_AUDIO_EXT):
            raise HTTPException(400, f"Unsupported media format: {media_ext}")

    tag_names = _parse_tag_csv(tags)
    # Convention: every entry carries at least the generic "QUELLE" tag so the
    # filter bar always has a stable bucket — matches the legacy JSON seed.
    if not tag_names:
        tag_names = ["QUELLE"]

    src = Source(
        title=title.strip(),
        kind=SourceKind(kind_upper),
        url=(url or None) and url.strip(),
        description=(description or None) and description.strip(),
    )
    src.tags = [_get_or_create_tag(db, n) for n in tag_names]
    db.add(src)
    db.flush()  # need src.id for filenames

    _THUMB_DIR.mkdir(parents=True, exist_ok=True)
    if thumb_ext is not None and thumbnail is not None:
        out = _THUMB_DIR / f"{src.id}{thumb_ext}"
        out.write_bytes(await thumbnail.read())
        src.thumbnail = f"/static/sources/{src.id}{thumb_ext}"
    else:
        _generate_placeholder_svg(_THUMB_DIR / f"{src.id}.svg", title, kind_upper)
        src.thumbnail = f"/static/sources/{src.id}.svg"

    if media_ext is not None and media is not None:
        _media_dir().mkdir(parents=True, exist_ok=True)
        out = _media_dir() / f"{src.id}{media_ext}"
        out.write_bytes(await media.read())
        src.media_url = f"/static/sources/media/{src.id}{media_ext}"

    db.commit()
    db.refresh(src)
    return _to_detail(src)


class CommentIn(BaseModel):
    text: str
    user: str | None = None  # TODO: post-dev — replace with auth context


@router.post("/{source_id}/comments", status_code=201)
def add_comment(source_id: int, payload: CommentIn, db: Session = Depends(get_db)) -> dict:
    if not payload.text.strip():
        raise HTTPException(400, "Comment text is required")
    src = _get_source_or_404(db, source_id)
    comment = SourceComment(
        source_id=src.id,
        user=(payload.user or "anonym").strip() or "anonym",
        text=payload.text.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "user": comment.user,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
        "text": comment.text,
    }


class UsageIn(BaseModel):
    context: str
    argument_id: int | None = None
    note: str | None = None


@router.post("/{source_id}/usages", status_code=201)
def add_usage(source_id: int, payload: UsageIn, db: Session = Depends(get_db)) -> dict:
    if not payload.context.strip():
        raise HTTPException(400, "Usage context is required")
    src = _get_source_or_404(db, source_id)
    if payload.argument_id is not None:
        # argument_id is a real FK now — reject dangling references with 404
        # instead of letting the DB raise IntegrityError on commit.
        if db.get(ArgumentNode, payload.argument_id) is None:
            raise HTTPException(404, f"Argument {payload.argument_id} not found")
    usage = SourceUsage(
        source_id=src.id,
        argument_id=payload.argument_id,
        context=payload.context.strip(),
        note=(payload.note or None) and payload.note.strip(),
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return {
        "context": usage.context,
        "argument_id": usage.argument_id,
        "note": usage.note,
    }


class VoteIn(BaseModel):
    """Vote transition. Client passes the previous vote so the server can
    adjust the aggregate counters without per-user tracking (deferred — see
    implementation-plan.md → Phase 1/2)."""
    value: int  # 1, -1, or 0 (clear)
    previous: int = 0  # 1, -1, or 0


@router.post("/{source_id}/vote")
def cast_vote(source_id: int, payload: VoteIn, db: Session = Depends(get_db)) -> dict:
    # TODO: post-dev — replace with per-user vote tracking (requires auth).
    if payload.value not in (-1, 0, 1) or payload.previous not in (-1, 0, 1):
        raise HTTPException(400, "value/previous must be -1, 0, or 1")
    src = _get_source_or_404(db, source_id)
    up, down = src.up, src.down
    if payload.previous == 1:
        up = max(0, up - 1)
    elif payload.previous == -1:
        down = max(0, down - 1)
    if payload.value == 1:
        up += 1
    elif payload.value == -1:
        down += 1
    src.up = up
    src.down = down
    db.commit()
    return {"id": src.id, "up": up, "down": down, "score": up - down}


# ── PATCH / DELETE ───────────────────────────────────────────────────────────


class SourcePatch(BaseModel):
    title: str | None = None
    kind: str | None = None
    url: str | None = None
    description: str | None = None
    tags: list[str] | None = None  # full replacement, not append


@router.patch("/{source_id}")
def update_source(source_id: int, payload: SourcePatch, db: Session = Depends(get_db)) -> dict:
    src = _get_source_or_404(db, source_id)
    changes = payload.model_dump(exclude_unset=True)

    if "kind" in changes:
        k = (changes["kind"] or "").upper()
        if k not in _ALLOWED_KINDS:
            raise HTTPException(400, f"Invalid kind: {k}")
        src.kind = SourceKind(k)
    if "title" in changes:
        new_title = (changes["title"] or "").strip()
        if not new_title:
            raise HTTPException(400, "Title must not be empty")
        src.title = new_title
    if "url" in changes:
        src.url = (changes["url"] or None) and changes["url"].strip()
    if "description" in changes:
        src.description = (changes["description"] or None) and changes["description"].strip()
    if "tags" in changes and changes["tags"] is not None:
        clean, seen = [], set()
        for t in changes["tags"]:
            if not t:
                continue
            stripped = t.strip()
            if stripped and stripped not in seen:
                seen.add(stripped)
                clean.append(stripped)
        src.tags = [_get_or_create_tag(db, n) for n in clean]

    db.commit()
    db.refresh(src)
    return _to_detail(src)


@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: int, db: Session = Depends(get_db)) -> None:
    src = _get_source_or_404(db, source_id)
    # Best-effort cleanup of managed files (only ones we created under
    # /static/sources/ — never touch arbitrary externally hosted URLs).
    thumb = src.thumbnail or ""
    if thumb.startswith("/static/sources/") and not thumb.startswith("/static/sources/media/"):
        thumb_file = _THUMB_DIR / Path(thumb).name
        if thumb_file.exists():
            try:
                thumb_file.unlink()
            except OSError:
                pass
    media_url = src.media_url or ""
    if media_url.startswith("/static/sources/media/"):
        media_file = _media_dir() / Path(media_url).name
        if media_file.exists():
            try:
                media_file.unlink()
            except OSError:
                pass

    db.delete(src)  # cascades to comments + usages via relationship config
    db.commit()


@router.delete("/{source_id}/comments/{index}", status_code=204)
def delete_comment(source_id: int, index: int, db: Session = Depends(get_db)) -> None:
    src = _get_source_or_404(db, source_id)
    comments = list(src.comments)  # ordered by id ASC (relationship config)
    if not 0 <= index < len(comments):
        raise HTTPException(404, f"Comment index {index} out of range")
    db.delete(comments[index])
    db.commit()


@router.delete("/{source_id}/usages/{index}", status_code=204)
def delete_usage(source_id: int, index: int, db: Session = Depends(get_db)) -> None:
    src = _get_source_or_404(db, source_id)
    usages = list(src.usages)
    if not 0 <= index < len(usages):
        raise HTTPException(404, f"Usage index {index} out of range")
    db.delete(usages[index])
    db.commit()

