"""Tests for the SQLAlchemy-backed Quellensammlung (sources) router.

The router now uses the shared in-memory test DB (see conftest.py). The only
filesystem dependency left is the thumbnail/media upload directory — those
are redirected per-test via monkeypatch.
"""
from pathlib import Path

import pytest

from app.routers import sources as sources_mod


@pytest.fixture(autouse=True)
def isolated_thumb_dir(tmp_path, monkeypatch):
    """Redirect the sources router thumbnail/media dir for upload tests."""
    thumb_dir = tmp_path / "static" / "sources"
    thumb_dir.mkdir(parents=True)
    monkeypatch.setattr(sources_mod, "_THUMB_DIR", thumb_dir)
    yield thumb_dir


class TestSourcesCRUD:
    def _create(self, client, **overrides):
        data = {"title": "T", "kind": "TEXT", "tags": "QUELLE"}
        data.update(overrides)
        return client.post("/api/sources/", data=data)

    def test_empty_list(self, client):
        r = client.get("/api/sources/")
        assert r.status_code == 200
        assert r.json() == []

    def test_create_with_placeholder_thumbnail(self, client, isolated_thumb_dir):
        r = self._create(client, title="Hello", description="world")
        assert r.status_code == 201
        body = r.json()
        sid = body["id"]
        assert body["title"] == "Hello"
        assert body["kind"] == "TEXT"
        assert body["thumbnail"] == f"/static/sources/{sid}.svg"
        assert (isolated_thumb_dir / f"{sid}.svg").exists()
        assert body["comments"] == []
        assert body["usages"] == []
        assert body["tags"] == ["QUELLE"]

    def test_create_with_uploaded_thumbnail(self, client, isolated_thumb_dir):
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32  # fake but non-empty
        r = client.post(
            "/api/sources/",
            data={"title": "Img", "kind": "IMAGE"},
            files={"thumbnail": ("pic.png", png_bytes, "image/png")},
        )
        assert r.status_code == 201
        sid = r.json()["id"]
        assert r.json()["thumbnail"] == f"/static/sources/{sid}.png"
        assert (isolated_thumb_dir / f"{sid}.png").read_bytes() == png_bytes

    def test_create_rejects_invalid_kind(self, client):
        r = self._create(client, kind="UNKNOWN")
        assert r.status_code == 400

    def test_create_rejects_unsupported_thumbnail_format(self, client):
        r = client.post(
            "/api/sources/",
            data={"title": "X", "kind": "TEXT"},
            files={"thumbnail": ("evil.exe", b"\x00", "application/octet-stream")},
        )
        assert r.status_code == 400

    def test_get_404(self, client):
        assert client.get("/api/sources/999").status_code == 404

    def test_get_detail(self, client):
        created = self._create(client).json()
        r = client.get(f"/api/sources/{created['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_id_autoincrement(self, client):
        a = self._create(client).json()
        b = self._create(client).json()
        assert b["id"] == a["id"] + 1

    def test_persistence_across_requests(self, client):
        self._create(client, title="persisted")
        r = client.get("/api/sources/")
        assert len(r.json()) == 1
        assert r.json()[0]["title"] == "persisted"


class TestSourcesFilters:
    def _seed(self, client):
        client.post("/api/sources/", data={"title": "Paper A", "kind": "PAPER", "tags": "QUELLE,WISSENSCHAFT"})
        client.post("/api/sources/", data={"title": "Quote B", "kind": "QUOTE", "tags": "GEGENSEITE,SOUNDBOARD"})
        client.post("/api/sources/", data={"title": "Tweet C", "kind": "TWEET", "tags": "QUELLE,TOPIC:KLIMA"})

    def test_filter_by_kind(self, client):
        self._seed(client)
        r = client.get("/api/sources/?kind=PAPER")
        assert [s["title"] for s in r.json()] == ["Paper A"]

    def test_filter_by_tag_single(self, client):
        self._seed(client)
        r = client.get("/api/sources/?tag=QUELLE")
        titles = {s["title"] for s in r.json()}
        assert titles == {"Paper A", "Tweet C"}

    def test_filter_by_tag_and_combined(self, client):
        self._seed(client)
        r = client.get("/api/sources/?tag=QUELLE&tag=WISSENSCHAFT")
        assert [s["title"] for s in r.json()] == ["Paper A"]

    def test_full_text_search(self, client):
        self._seed(client)
        r = client.get("/api/sources/?q=quote")
        assert [s["title"] for s in r.json()] == ["Quote B"]

    def test_sort_alphabetical(self, client):
        self._seed(client)
        r = client.get("/api/sources/?sort=titel")
        assert [s["title"] for s in r.json()] == ["Paper A", "Quote B", "Tweet C"]

    def test_tags_aggregation(self, client):
        self._seed(client)
        r = client.get("/api/sources/tags")
        by_tag = {t["tag"]: t["count"] for t in r.json()}
        assert by_tag["QUELLE"] == 2
        assert by_tag["GEGENSEITE"] == 1
        # Topic tags sorted last
        topic_idx = next(i for i, t in enumerate(r.json()) if t["tag"].startswith("TOPIC:"))
        non_topic_indices = [i for i, t in enumerate(r.json()) if not t["tag"].startswith("TOPIC:")]
        assert topic_idx > max(non_topic_indices)

    def test_tag_reuse_is_deduplicated(self, client):
        """Same tag string across sources must produce a single SourceTag row."""
        from app.models import SourceTag as _ST
        client.post("/api/sources/", data={"title": "A", "kind": "TEXT", "tags": "SHARED"})
        client.post("/api/sources/", data={"title": "B", "kind": "TEXT", "tags": "SHARED"})
        # Access via the client's DB session is not available here; use a
        # fresh count via the API instead.
        r = client.get("/api/sources/tags")
        shared = [t for t in r.json() if t["tag"] == "SHARED"]
        assert len(shared) == 1
        assert shared[0]["count"] == 2


class TestSourceComments:
    def test_add_and_delete_comment(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        r = client.post(f"/api/sources/{sid}/comments", json={"text": "hi", "user": "alice"})
        assert r.status_code == 201
        assert r.json()["text"] == "hi"
        assert r.json()["user"] == "alice"
        # Reflected in detail
        assert len(client.get(f"/api/sources/{sid}").json()["comments"]) == 1
        # Delete by index (backward-compatible with JSON era)
        r = client.delete(f"/api/sources/{sid}/comments/0")
        assert r.status_code == 204
        assert client.get(f"/api/sources/{sid}").json()["comments"] == []

    def test_empty_comment_rejected(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        r = client.post(f"/api/sources/{sid}/comments", json={"text": "   "})
        assert r.status_code == 400

    def test_anonymous_default(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        r = client.post(f"/api/sources/{sid}/comments", json={"text": "hi"})
        assert r.json()["user"] == "anonym"

    def test_delete_comment_404(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        assert client.delete(f"/api/sources/{sid}/comments/5").status_code == 404


class TestSourceUsages:
    def test_add_and_delete_usage(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        r = client.post(f"/api/sources/{sid}/usages", json={"context": "Diskussion XY"})
        assert r.status_code == 201
        assert r.json()["context"] == "Diskussion XY"
        assert r.json()["argument_id"] is None
        r = client.delete(f"/api/sources/{sid}/usages/0")
        assert r.status_code == 204
        assert client.get(f"/api/sources/{sid}").json()["usages"] == []

    def test_empty_context_rejected(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        r = client.post(f"/api/sources/{sid}/usages", json={"context": "  "})
        assert r.status_code == 400

    def test_usage_with_valid_argument_id(self, client, sample_argument):
        """argument_id is now a real FK and must reference an existing node."""
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        r = client.post(
            f"/api/sources/{sid}/usages",
            json={"context": "verlinkt", "argument_id": sample_argument["id"]},
        )
        assert r.status_code == 201
        assert r.json()["argument_id"] == sample_argument["id"]

    def test_usage_rejects_unknown_argument_id(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        r = client.post(
            f"/api/sources/{sid}/usages",
            json={"context": "bogus", "argument_id": 99999},
        )
        assert r.status_code == 404

    def test_argument_delete_sets_usage_argument_id_null(self, client, sample_user, sample_topic):
        """ON DELETE SET NULL: usage row survives, just loses the link."""
        arg = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Temp", "position": "PRO",
        }).json()
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        client.post(f"/api/sources/{sid}/usages", json={"context": "ref", "argument_id": arg["id"]})
        # Delete the argument
        client.delete(f"/api/arguments/{arg['id']}")
        usages = client.get(f"/api/sources/{sid}").json()["usages"]
        assert len(usages) == 1
        assert usages[0]["argument_id"] is None
        assert usages[0]["context"] == "ref"


class TestSourcePatchDelete:
    def test_patch_title_and_tags(self, client):
        sid = client.post("/api/sources/", data={"title": "Old", "kind": "TEXT", "tags": "A"}).json()["id"]
        r = client.patch(f"/api/sources/{sid}", json={"title": "New", "tags": ["B", "C"]})
        assert r.status_code == 200
        body = r.json()
        assert body["title"] == "New"
        assert body["tags"] == ["B", "C"]
        # Untouched fields preserved
        assert body["kind"] == "TEXT"

    def test_patch_rejects_invalid_kind(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        assert client.patch(f"/api/sources/{sid}", json={"kind": "NOPE"}).status_code == 400

    def test_patch_rejects_empty_title(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        assert client.patch(f"/api/sources/{sid}", json={"title": "   "}).status_code == 400

    def test_patch_404(self, client):
        assert client.patch("/api/sources/999", json={"title": "x"}).status_code == 404

    def test_delete_source_also_removes_managed_thumbnail(self, client, isolated_thumb_dir):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        thumb = isolated_thumb_dir / f"{sid}.svg"
        assert thumb.exists()
        r = client.delete(f"/api/sources/{sid}")
        assert r.status_code == 204
        assert not thumb.exists()
        assert client.get(f"/api/sources/{sid}").status_code == 404

    def test_delete_cascades_to_comments_and_usages(self, client):
        sid = client.post("/api/sources/", data={"title": "X", "kind": "TEXT"}).json()["id"]
        client.post(f"/api/sources/{sid}/comments", json={"text": "c"})
        client.post(f"/api/sources/{sid}/usages", json={"context": "u"})
        client.delete(f"/api/sources/{sid}")
        # 404 indicates the source is gone; children should be cascaded out
        assert client.get(f"/api/sources/{sid}").status_code == 404

    def test_delete_source_404(self, client):
        assert client.delete("/api/sources/999").status_code == 404


class TestSourcesVoting:
    def _create(self, client, title="V"):
        return client.post("/api/sources/", data={"title": title, "kind": "TEXT"}).json()["id"]

    def test_initial_score_zero(self, client):
        sid = self._create(client)
        body = client.get(f"/api/sources/{sid}").json()
        assert body["up"] == 0 and body["down"] == 0 and body["score"] == 0

    def test_upvote_increments(self, client):
        sid = self._create(client)
        r = client.post(f"/api/sources/{sid}/vote", json={"value": 1, "previous": 0})
        assert r.status_code == 200
        assert r.json() == {"id": sid, "up": 1, "down": 0, "score": 1}

    def test_downvote_increments(self, client):
        sid = self._create(client)
        r = client.post(f"/api/sources/{sid}/vote", json={"value": -1, "previous": 0})
        assert r.json() == {"id": sid, "up": 0, "down": 1, "score": -1}

    def test_toggle_off_clears(self, client):
        sid = self._create(client)
        client.post(f"/api/sources/{sid}/vote", json={"value": 1, "previous": 0})
        r = client.post(f"/api/sources/{sid}/vote", json={"value": 0, "previous": 1})
        assert r.json() == {"id": sid, "up": 0, "down": 0, "score": 0}

    def test_switch_from_up_to_down(self, client):
        sid = self._create(client)
        client.post(f"/api/sources/{sid}/vote", json={"value": 1, "previous": 0})
        r = client.post(f"/api/sources/{sid}/vote", json={"value": -1, "previous": 1})
        assert r.json() == {"id": sid, "up": 0, "down": 1, "score": -1}

    def test_invalid_value(self, client):
        sid = self._create(client)
        assert client.post(f"/api/sources/{sid}/vote", json={"value": 2, "previous": 0}).status_code == 400

    def test_vote_404(self, client):
        assert client.post("/api/sources/999/vote", json={"value": 1, "previous": 0}).status_code == 404

    def test_list_includes_score_and_sort_top(self, client):
        a = self._create(client, "A")
        b = self._create(client, "B")
        c = self._create(client, "C")
        client.post(f"/api/sources/{a}/vote", json={"value": 1, "previous": 0})
        client.post(f"/api/sources/{b}/vote", json={"value": -1, "previous": 0})
        # c stays at 0
        items = client.get("/api/sources/?sort=top").json()
        assert [s["id"] for s in items] == [a, c, b]
        assert items[0]["score"] == 1 and items[2]["score"] == -1


class TestSourcesMedia:
    def test_create_with_media_upload(self, client, isolated_thumb_dir):
        mp4 = b"\x00\x00\x00 ftypisom" + b"\x00" * 16
        r = client.post(
            "/api/sources/",
            data={"title": "Clip", "kind": "VIDEO"},
            files={"media": ("clip.mp4", mp4, "video/mp4")},
        )
        assert r.status_code == 201
        sid = r.json()["id"]
        assert r.json()["media_url"] == f"/static/sources/media/{sid}.mp4"
        assert (isolated_thumb_dir / "media" / f"{sid}.mp4").read_bytes() == mp4

    def test_create_with_audio_upload(self, client, isolated_thumb_dir):
        r = client.post(
            "/api/sources/",
            data={"title": "Snippet", "kind": "AUDIO"},
            files={"media": ("a.mp3", b"ID3" + b"\x00" * 32, "audio/mpeg")},
        )
        sid = r.json()["id"]
        assert r.json()["media_url"] == f"/static/sources/media/{sid}.mp3"

    def test_create_rejects_unsupported_media(self, client):
        r = client.post(
            "/api/sources/",
            data={"title": "X", "kind": "VIDEO"},
            files={"media": ("evil.exe", b"\x00", "application/octet-stream")},
        )
        assert r.status_code == 400

    def test_delete_removes_media_file(self, client, isolated_thumb_dir):
        sid = client.post(
            "/api/sources/",
            data={"title": "X", "kind": "VIDEO"},
            files={"media": ("c.mp4", b"x" * 16, "video/mp4")},
        ).json()["id"]
        media_file = isolated_thumb_dir / "media" / f"{sid}.mp4"
        assert media_file.exists()
        client.delete(f"/api/sources/{sid}")
        assert not media_file.exists()

    def test_list_surfaces_url_and_media(self, client):
        client.post("/api/sources/", data={"title": "YT", "kind": "VIDEO", "url": "https://youtu.be/abc123"})
        items = client.get("/api/sources/").json()
        assert items[0]["url"] == "https://youtu.be/abc123"
        assert items[0]["media_url"] is None


class TestSourcesQueryExtras:
    def test_filter_by_argument_id(self, client, sample_user, sample_topic):
        # Need real argument nodes (FK now)
        def _arg(title):
            return client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
                "topic_id": sample_topic["id"], "title": title, "position": "PRO",
            }).json()["id"]
        arg42 = _arg("arg42")
        arg99 = _arg("arg99")
        a = client.post("/api/sources/", data={"title": "A", "kind": "TEXT"}).json()["id"]
        b = client.post("/api/sources/", data={"title": "B", "kind": "TEXT"}).json()["id"]
        client.post("/api/sources/", data={"title": "C", "kind": "TEXT"})
        client.post(f"/api/sources/{a}/usages", json={"context": "x", "argument_id": arg42})
        client.post(f"/api/sources/{b}/usages", json={"context": "y", "argument_id": arg42})
        client.post(f"/api/sources/{b}/usages", json={"context": "z", "argument_id": arg99})
        r = client.get(f"/api/sources/?argument_id={arg42}")
        assert {s["id"] for s in r.json()} == {a, b}
        r = client.get(f"/api/sources/?argument_id={arg99}")
        assert [s["id"] for s in r.json()] == [b]
        r = client.get("/api/sources/?argument_id=12345")
        assert r.json() == []

    def test_sort_zufall_returns_all_items(self, client):
        for t in ("A", "B", "C", "D", "E"):
            client.post("/api/sources/", data={"title": t, "kind": "TEXT"})
        r = client.get("/api/sources/?sort=zufall")
        assert {s["title"] for s in r.json()} == {"A", "B", "C", "D", "E"}

    def test_sort_invalid_rejected(self, client):
        assert client.get("/api/sources/?sort=bogus").status_code == 422


class TestSourcesSimilarity:
    def test_empty_query_returns_empty(self, client):
        client.post("/api/sources/", data={"title": "Anything", "kind": "TEXT"})
        assert client.get("/api/sources/similar?title=").json() == []

    def test_finds_obvious_duplicate(self, client):
        client.post(
            "/api/sources/",
            data={"title": "Menapt-Statistik zu IQ-Unterschieden", "kind": "TWEET"},
        )
        client.post("/api/sources/", data={"title": "Unrelated PubMed Paper", "kind": "PAPER"})
        r = client.get("/api/sources/similar?title=Menapt IQ Statistik")
        body = r.json()
        assert len(body) == 1
        assert "Menapt" in body[0]["title"]
        assert body[0]["similarity"] >= 0.25

    def test_threshold_filters(self, client):
        client.post("/api/sources/", data={"title": "Klimawandel und Folgen", "kind": "PAPER"})
        # Only one shared meaningful token would give a low jaccard
        r = client.get("/api/sources/similar?title=Klimawandel&threshold=0.9")
        assert r.json() == []

    def test_exclude_id(self, client):
        sid = client.post("/api/sources/", data={"title": "Same Title Here", "kind": "TEXT"}).json()["id"]
        r = client.get(f"/api/sources/similar?title=Same Title Here&exclude_id={sid}")
        assert r.json() == []

    def test_orders_by_similarity_desc(self, client):
        client.post("/api/sources/", data={"title": "Klima Wandel Folgen", "kind": "PAPER"})
        client.post("/api/sources/", data={"title": "Klima Wandel jetzt", "kind": "TEXT"})
        client.post("/api/sources/", data={"title": "Quotenregelung Deutschland", "kind": "QUOTE"})
        r = client.get("/api/sources/similar?title=Klima Wandel Folgen Studie")
        body = r.json()
        assert len(body) == 2
        assert body[0]["similarity"] >= body[1]["similarity"]

