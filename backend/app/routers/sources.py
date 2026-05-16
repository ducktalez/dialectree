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

# Simple mtime-based cache so editing the JSON during dev does not require
# a server restart. Not thread-safe but irrelevant for the dev server.
_cache: dict[str, Any] = {"mtime": None, "data": None}

_ALLOWED_THUMB_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
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


@router.get("/")
def list_sources(
    tag: list[str] | None = Query(default=None, description="Filter by tag (repeatable, AND-combined)"),
    kind: str | None = None,
    q: str | None = Query(default=None, description="Full-text search over title + description"),
    sort: str = Query(default="neu", pattern="^(neu|alt|titel)$"),
) -> list[dict]:
    items = _all_sources()

    if tag:
        wanted = {t.upper() for t in tag}
        items = [s for s in items if wanted.issubset({t.upper() for t in s.get("tags", [])})]
    if kind:
        items = [s for s in items if s.get("kind", "").upper() == kind.upper()]
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
        }
        for s in items
    ]


@router.get("/{source_id}")
def get_source(source_id: int) -> dict:
    return _find_source(source_id)


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

    new_source = {
        "id": new_id,
        "title": title.strip(),
        "kind": kind,
        "url": (url or None) and url.strip(),
        "thumbnail": thumb_path,
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




