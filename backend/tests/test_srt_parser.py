"""Tests for the SRT parser module and import endpoint."""

from app.srt_parser import parse_srt, parse_srt_to_yaml, _strip_tags, _find_overlap


# ── Unit tests: parse_srt ──────────────────────────────────────────────

SIMPLE_SRT = """\
1
00:00:00,080 --> 00:00:03,439
Hello world this is a test

2
00:00:03,439 --> 00:00:06,960
of the subtitle parser

3
00:00:06,960 --> 00:00:10,000
and it should produce clean text
"""


def test_parse_srt_simple():
    result = parse_srt(SIMPLE_SRT)
    assert result == "Hello world this is a test of the subtitle parser and it should produce clean text"


def test_parse_srt_strips_html_tags():
    srt_with_tags = """\
1
00:00:00,000 --> 00:00:02,000
<i>italic text</i> and <b>bold</b>

2
00:00:02,000 --> 00:00:04,000
<font color="#CCCCCC">colored</font> words
"""
    result = parse_srt(srt_with_tags)
    assert "<" not in result
    assert ">" not in result
    assert "italic text" in result
    assert "colored" in result


def test_parse_srt_handles_empty_entries():
    srt_with_empty = """\
1
00:00:00,000 --> 00:00:01,000
first line

2
00:00:01,000 --> 00:00:02,000


3
00:00:02,000 --> 00:00:03,000
third line
"""
    result = parse_srt(srt_with_empty)
    assert result == "first line third line"


def test_parse_srt_deduplicates_overlapping_fragments():
    """YouTube ASR often repeats words across subtitle entries."""
    overlapping_srt = """\
1
00:00:00,000 --> 00:00:03,000
so if you were to intentionally

2
00:00:01,000 --> 00:00:05,000
to intentionally misgender a trans woman

3
00:00:03,000 --> 00:00:07,000
a trans woman that could put her at risk
"""
    result = parse_srt(overlapping_srt)
    # "to intentionally" should not be duplicated
    assert result.count("to intentionally") == 1
    # "a trans woman" should not be duplicated
    assert result.count("a trans woman") == 1


def test_parse_srt_handles_unicode():
    unicode_srt = """\
1
00:00:00,000 --> 00:00:02,000
Ça fait plaisir de discuter

2
00:00:02,000 --> 00:00:04,000
über Quotenregelungen — sind sie rassistisch?
"""
    result = parse_srt(unicode_srt)
    assert "Ça fait plaisir" in result
    assert "Quotenregelungen" in result


def test_parse_srt_empty_input():
    # srt library returns empty list for empty input
    result = parse_srt("")
    assert result == ""


# ── Unit tests: helper functions ───────────────────────────────────────

def test_strip_tags():
    assert _strip_tags("<i>hello</i>") == "hello"
    assert _strip_tags('<font color="#FFF">text</font>') == "text"
    assert _strip_tags("no tags here") == "no tags here"


def test_find_overlap_match():
    overlap = _find_overlap("hello world is great", "is great indeed")
    assert overlap == "is great"


def test_find_overlap_no_match():
    overlap = _find_overlap("hello world", "completely different")
    assert overlap is None


def test_find_overlap_single_word_ignored():
    """Single word overlaps are ignored to avoid false positives."""
    overlap = _find_overlap("hello world", "world domination")
    assert overlap is None


# ── Unit tests: parse_srt_to_yaml ──────────────────────────────────────

def test_parse_srt_to_yaml_structure():
    result = parse_srt_to_yaml(SIMPLE_SRT, title="Test Video", source_url="https://youtube.com/watch?v=abc")
    assert 'title: "Test Video"' in result
    assert 'source_url: "https://youtube.com/watch?v=abc"' in result
    assert "stage_0:" in result
    assert "transcript: |" in result
    assert "Hello world" in result


def test_parse_srt_to_yaml_without_optionals():
    result = parse_srt_to_yaml(SIMPLE_SRT)
    assert "title:" not in result
    assert "source_url:" not in result
    assert "stage_0:" in result


# ── Integration test: import-srt endpoint ──────────────────────────────

def test_import_srt_endpoint(client, sample_user, sample_topic):
    """POST /api/topics/{id}/import-srt stores parsed SRT as transcript_yaml."""
    topic_id = sample_topic["id"]

    resp = client.post(
        f"/api/topics/{topic_id}/import-srt",
        json={
            "srt_content": SIMPLE_SRT,
            "source_url": "https://www.youtube.com/watch?v=WtftZPL-k7Y",
            "title": "Test Discussion",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["topic_id"] == topic_id
    assert data["transcript_yaml"] is not None
    assert "Hello world" in data["transcript_yaml"]
    assert "stage_0:" in data["transcript_yaml"]

    # Verify transcript is persisted by fetching it
    get_resp = client.get(f"/api/topics/{topic_id}/transcript")
    assert get_resp.status_code == 200
    assert "Hello world" in get_resp.json()["transcript_yaml"]


def test_import_srt_endpoint_topic_not_found(client):
    resp = client.post(
        "/api/topics/9999/import-srt",
        json={"srt_content": SIMPLE_SRT},
    )
    assert resp.status_code == 404


