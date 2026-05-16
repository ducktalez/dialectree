"""Source collection (Quellensammlung) – MVP.

Reads from a manually curated JSON file. No DB table yet (see
docs/implementation-plan.md → Phase 2 → Quellensammlung). Kept intentionally
simple so the schema can be revised without migration pain.

Endpoints:
- GET /api/sources/        list with optional filters (?tag, ?kind, ?q, ?sort)
- GET /api/sources/tags    aggregated tag list with counts
- GET /api/sources/{id}    single source incl. comments + usages
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/sources", tags=["sources"])

_DATA_FILE = Path(__file__).parent.parent / "data" / "sources.json"

# Simple mtime-based cache so editing the JSON during dev does not require
# a server restart. Not thread-safe but irrelevant for the dev server.
_cache: dict[str, Any] = {"mtime": None, "data": None}


def _load() -> dict:
    mtime = _DATA_FILE.stat().st_mtime
    if _cache["mtime"] != mtime:
        with _DATA_FILE.open(encoding="utf-8") as f:
            _cache["data"] = json.load(f)
        _cache["mtime"] = mtime
    return _cache["data"]


def _all_sources() -> list[dict]:
    return list(_load().get("sources", []))


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
    for s in _all_sources():
        if s.get("id") == source_id:
            return s
    raise HTTPException(404, f"Source {source_id} not found")

