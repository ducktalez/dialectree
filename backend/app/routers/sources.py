"""Source collection (Quellensammlung) – MVP.

Reads from a manually curated JSON file. No DB table yet (see
docs/implementation-plan.md → Phase 2 → Quellensammlung). Kept intentionally
simple so the schema can be revised without migration pain.

Endpoints:
- GET  /api/sources/        list with optional filters (?tag, ?kind, ?q, ?sort)
- GET  /api/sources/tags    aggregated tag list with counts
- GET  /api/sources/{id}    single source incl. comments + usages
- POST /api/sources/        create source (multipart: title, kind, url, description, tags, thumbnail file)
- POST /api/sources/{id}/comments   add comment (JSON)
- POST /api/sources/{id}/usages     add usage entry  (JSON)

Writes persist to the same JSON file. Auth is not implemented; user is passed
as ?user_id (query param) — same convention as the rest of the API.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/sources", tags=["sources"])

_DATA_FILE = Path(__file__).parent.parent / "data" / "sources.json"
_THUMB_DIR = Path(__file__).parent.parent / "static" / "sources"

def _media_dir() -> Path:
    # Lazy lookup so tests can monkeypatch _THUMB_DIR.
    return _THUMB_DIR / "media"

# Simple mtime-based cache so editing the JSON during dev does not require
# a server restart. Not thread-safe but irrelevant for the dev server.
_cache: dict[str, Any] = {"mtime": None, "data": None}

_ALLOWED_THUMB_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
_ALLOWED_VIDEO_EXT = {".mp4", ".webm", ".ogg", ".mov", ".m4v"}
_ALLOWED_AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".oga", ".flac"}
_ALLOWED_KINDS = {"QUOTE", "VIDEO", "AUDIO", "PAPER", "TWEET", "IMAGE", "TEXT"}


def _load() -> dict:
    mtime = _DATA_FILE.stat().st_mtime
    if _cache["mtime"] != mtime:
        with _DATA_FILE.open(encoding="utf-8") as f:
            _cache["data"] = json.load(f)
        _cache["mtime"] = mtime
    return _cache["data"]


def _persist(data: dict) -> None:
    """Write back to JSON and refresh cache."""
    with _DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    _cache["mtime"] = _DATA_FILE.stat().st_mtime
    _cache["data"] = data


def _all_sources() -> list[dict]:
    return list(_load().get("sources", []))


def _find_source(source_id: int) -> dict:
    for s in _load().get("sources", []):
        if s.get("id") == source_id:
            return s
    raise HTTPException(404, f"Source {source_id} not found")


def _next_id(sources: list[dict]) -> int:
    return max((s.get("id", 0) for s in sources), default=0) + 1


def _generate_placeholder_svg(path: Path, title: str, kind: str) -> None:
    """Minimal placeholder SVG so every source has a visual tile."""
    import html
    safe_title = html.escape((title or "")[:60])
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

import re as _re

# Common German + English stop words. The list is intentionally small;
# the goal is rough deduplication, not search-engine quality.
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
    # Lowercase, split on non-letters/digits, drop short + stop words.
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
def list_tags() -> list[dict]:
    """All tags with usage counts. Used by the frontend filter bar."""
    counts: dict[str, int] = {}
    for src in _all_sources():
        for t in src.get("tags", []):
            counts[t] = counts.get(t, 0) + 1
    # Stable sort: TOPIC:* tags grouped at the end, otherwise by count desc.
    def key(item: tuple[str, int]) -> tuple[int, int, str]:
        tag, cnt = item
        is_topic = 1 if tag.startswith("TOPIC:") else 0
        return (is_topic, -cnt, tag)
    return [{"tag": t, "count": c} for t, c in sorted(counts.items(), key=key)]


@router.get("/similar")
def find_similar(
    title: str = Query(default="", description="Candidate title to compare against existing sources"),
    description: str = Query(default=""),
    threshold: float = Query(default=0.25, ge=0.0, le=1.0),
    limit: int = Query(default=5, ge=1, le=50),
    exclude_id: int | None = Query(default=None, description="Skip this source id (used by edit dialogs)"),
) -> list[dict]:
    """Lightweight duplicate suggestions for the 'new source' modal.

    Uses normalized token-set Jaccard similarity over title + description.
    Stand-in for embedding-based dedup (post-dev: replace with vector search).
    Returns at most `limit` items above `threshold`, ordered by similarity.
    """
    candidate = _tokens(title) | _tokens(description)
    if not candidate:
        return []
    scored: list[tuple[float, dict]] = []
    for s in _all_sources():
        if exclude_id is not None and s.get("id") == exclude_id:
            continue
        their = _tokens(s.get("title") or "") | _tokens(s.get("description") or "")
        score = _jaccard(candidate, their)
        if score >= threshold:
            scored.append((score, s))
    scored.sort(key=lambda x: (-x[0], x[1].get("id", 0)))
    return [
        {
            "id": s["id"],
            "title": s.get("title"),
            "kind": s.get("kind"),
            "thumbnail": s.get("thumbnail"),
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
) -> list[dict]:
    items = _all_sources()

    if tag:
        wanted = {t.upper() for t in tag}
        items = [s for s in items if wanted.issubset({t.upper() for t in s.get("tags", [])})]
    if kind:
        items = [s for s in items if s.get("kind", "").upper() == kind.upper()]
    if argument_id is not None:
        items = [
            s for s in items
            if any(u.get("argument_id") == argument_id for u in s.get("usages", []))
        ]
    if q:
        needle = q.lower()
        items = [
            s for s in items
            if needle in (s.get("title") or "").lower()
            or needle in (s.get("description") or "").lower()
        ]

    if sort == "neu":
        items.sort(key=lambda s: (s.get("created_at", ""), s.get("id", 0)), reverse=True)
    elif sort == "alt":
        items.sort(key=lambda s: (s.get("created_at", ""), s.get("id", 0)))
    elif sort == "titel":
        items.sort(key=lambda s: (s.get("title") or "").lower())
    elif sort == "top":
        items.sort(key=lambda s: (s.get("up", 0) - s.get("down", 0), s.get("id", 0)), reverse=True)
    elif sort == "kontrovers":
        # Highest total engagement, score near zero ranks higher within equal totals.
        items.sort(
            key=lambda s: (
                s.get("up", 0) + s.get("down", 0),
                -abs(s.get("up", 0) - s.get("down", 0)),
            ),
            reverse=True,
        )
    elif sort == "zufall":
        # pr0gramm-style "Müll": serendipity for browsing. Different every call.
        import random as _r
        _r.shuffle(items)

    # List view: omit heavy fields. Detail endpoint returns everything.
    return [
        {
            "id": s["id"],
            "title": s.get("title"),
            "kind": s.get("kind"),
            "thumbnail": s.get("thumbnail"),
            "tags": s.get("tags", []),
            "created_at": s.get("created_at"),
            "comment_count": len(s.get("comments", [])),
            "usage_count": len(s.get("usages", [])),
            "up": s.get("up", 0),
            "down": s.get("down", 0),
            "score": s.get("up", 0) - s.get("down", 0),
            # Surfaced so the tile can show a play icon without an extra request
            "url": s.get("url"),
            "media_url": s.get("media_url"),
        }
        for s in items
    ]


@router.get("/{source_id}")
def get_source(source_id: int) -> dict:
    src = _find_source(source_id)
    # Ensure vote fields are always present for the frontend.
    up = int(src.get("up", 0))
    down = int(src.get("down", 0))
    return {**src, "up": up, "down": down, "score": up - down}


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
) -> dict:
    kind = kind.upper()
    if kind not in _ALLOWED_KINDS:
        raise HTTPException(400, f"Invalid kind: {kind}. Allowed: {sorted(_ALLOWED_KINDS)}")

    data = _load()
    sources = data.setdefault("sources", [])
    new_id = _next_id(sources)

    _THUMB_DIR.mkdir(parents=True, exist_ok=True)

    if thumbnail is not None and thumbnail.filename:
        ext = Path(thumbnail.filename).suffix.lower()
        if ext not in _ALLOWED_THUMB_EXT:
            raise HTTPException(400, f"Unsupported thumbnail format: {ext}")
        out = _THUMB_DIR / f"{new_id}{ext}"
        out.write_bytes(await thumbnail.read())
        thumb_path = f"/static/sources/{new_id}{ext}"
    else:
        thumb_path = f"/static/sources/{new_id}.svg"
        _generate_placeholder_svg(_THUMB_DIR / f"{new_id}.svg", title, kind)

    # Optional media file (audio/video). Inline-player consumes this on the
    # detail view. Bigger files belong on a CDN long-term, but for the MVP
    # we just store them under /static/sources/media/.
    media_path: str | None = None
    if media is not None and media.filename:
        ext = Path(media.filename).suffix.lower()
        allowed = _ALLOWED_VIDEO_EXT | _ALLOWED_AUDIO_EXT
        if ext not in allowed:
            raise HTTPException(400, f"Unsupported media format: {ext}")
        _media_dir().mkdir(parents=True, exist_ok=True)
        out = _media_dir() / f"{new_id}{ext}"
        out.write_bytes(await media.read())
        media_path = f"/static/sources/media/{new_id}{ext}"

    new_source = {
        "id": new_id,
        "title": title.strip(),
        "kind": kind,
        "url": (url or None) and url.strip(),
        "thumbnail": thumb_path,
        "media_url": media_path,
        "description": (description or None) and description.strip(),
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "created_at": date.today().isoformat(),
        "usages": [],
        "comments": [],
    }
    sources.append(new_source)
    _persist(data)
    return new_source


class CommentIn(BaseModel):
    text: str
    user: str | None = None  # TODO: post-dev — replace with auth context


@router.post("/{source_id}/comments", status_code=201)
def add_comment(source_id: int, payload: CommentIn) -> dict:
    if not payload.text.strip():
        raise HTTPException(400, "Comment text is required")
    data = _load()
    src = next((s for s in data.get("sources", []) if s.get("id") == source_id), None)
    if not src:
        raise HTTPException(404, f"Source {source_id} not found")
    comment = {
        "user": (payload.user or "anonym").strip() or "anonym",
        "created_at": date.today().isoformat(),
        "text": payload.text.strip(),
    }
    src.setdefault("comments", []).append(comment)
    _persist(data)
    return comment


class UsageIn(BaseModel):
    context: str
    argument_id: int | None = None
    note: str | None = None


@router.post("/{source_id}/usages", status_code=201)
def add_usage(source_id: int, payload: UsageIn) -> dict:
    if not payload.context.strip():
        raise HTTPException(400, "Usage context is required")
    data = _load()
    src = next((s for s in data.get("sources", []) if s.get("id") == source_id), None)
    if not src:
        raise HTTPException(404, f"Source {source_id} not found")
    usage = {
        "context": payload.context.strip(),
        "argument_id": payload.argument_id,
        "note": (payload.note or None) and payload.note.strip(),
    }
    src.setdefault("usages", []).append(usage)
    _persist(data)
    return usage


# ── PATCH / DELETE ───────────────────────────────────────────────────────────


class VoteIn(BaseModel):
    """Vote transition. Client passes the previous vote so the server can adjust
    the counters correctly without per-user tracking (deferred — see Phase 2)."""
    value: int  # 1, -1, or 0 (clear)
    previous: int = 0  # 1, -1, or 0


@router.post("/{source_id}/vote")
def cast_vote(source_id: int, payload: VoteIn) -> dict:
    # TODO: post-dev — replace with per-user vote tracking (auth required)
    if payload.value not in (-1, 0, 1) or payload.previous not in (-1, 0, 1):
        raise HTTPException(400, "value/previous must be -1, 0, or 1")
    data = _load()
    src = next((s for s in data.get("sources", []) if s.get("id") == source_id), None)
    if not src:
        raise HTTPException(404, f"Source {source_id} not found")
    up = int(src.get("up", 0))
    down = int(src.get("down", 0))
    # Undo previous vote
    if payload.previous == 1:
        up = max(0, up - 1)
    elif payload.previous == -1:
        down = max(0, down - 1)
    # Apply new vote
    if payload.value == 1:
        up += 1
    elif payload.value == -1:
        down += 1
    src["up"] = up
    src["down"] = down
    _persist(data)
    return {"id": source_id, "up": up, "down": down, "score": up - down}


class SourcePatch(BaseModel):
    title: str | None = None
    kind: str | None = None
    url: str | None = None
    description: str | None = None
    tags: list[str] | None = None  # full replacement, not append


@router.patch("/{source_id}")
def update_source(source_id: int, payload: SourcePatch) -> dict:
    data = _load()
    src = next((s for s in data.get("sources", []) if s.get("id") == source_id), None)
    if not src:
        raise HTTPException(404, f"Source {source_id} not found")
    changes = payload.model_dump(exclude_unset=True)
    if "kind" in changes:
        k = (changes["kind"] or "").upper()
        if k not in _ALLOWED_KINDS:
            raise HTTPException(400, f"Invalid kind: {k}")
        changes["kind"] = k
    if "title" in changes and not (changes["title"] or "").strip():
        raise HTTPException(400, "Title must not be empty")
    if "tags" in changes and changes["tags"] is not None:
        changes["tags"] = [t.strip() for t in changes["tags"] if t and t.strip()]
    src.update(changes)
    _persist(data)
    return src


@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: int) -> None:
    data = _load()
    sources = data.get("sources", [])
    src = next((s for s in sources if s.get("id") == source_id), None)
    if not src:
        raise HTTPException(404, f"Source {source_id} not found")
    # Best-effort delete of the managed thumbnail file (only if it lives under
    # our static/sources directory — never delete arbitrary referenced URLs).
    thumb = src.get("thumbnail") or ""
    if thumb.startswith("/static/sources/"):
        thumb_file = _THUMB_DIR / Path(thumb).name
        if thumb_file.exists():
            try:
                thumb_file.unlink()
            except OSError:
                pass  # leave dangling file rather than fail the request
    # Same for an uploaded media file.
    media_url = src.get("media_url") or ""
    if media_url.startswith("/static/sources/media/"):
        media_file = _media_dir() / Path(media_url).name
        if media_file.exists():
            try:
                media_file.unlink()
            except OSError:
                pass
    data["sources"] = [s for s in sources if s.get("id") != source_id]
    _persist(data)


@router.delete("/{source_id}/comments/{index}", status_code=204)
def delete_comment(source_id: int, index: int) -> None:
    data = _load()
    src = next((s for s in data.get("sources", []) if s.get("id") == source_id), None)
    if not src:
        raise HTTPException(404, f"Source {source_id} not found")
    comments = src.get("comments", [])
    if not 0 <= index < len(comments):
        raise HTTPException(404, f"Comment index {index} out of range")
    comments.pop(index)
    _persist(data)


@router.delete("/{source_id}/usages/{index}", status_code=204)
def delete_usage(source_id: int, index: int) -> None:
    data = _load()
    src = next((s for s in data.get("sources", []) if s.get("id") == source_id), None)
    if not src:
        raise HTTPException(404, f"Source {source_id} not found")
    usages = src.get("usages", [])
    if not 0 <= index < len(usages):
        raise HTTPException(404, f"Usage index {index} out of range")
    usages.pop(index)
    _persist(data)




