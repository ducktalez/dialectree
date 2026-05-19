"""
SRT subtitle file parser for the Dialectree transcript pipeline.

Converts YouTube .srt files (auto-generated or manual) into clean flowing text
suitable for Stage 0 (raw transcript) of the zigzag refinement model.

Typical YouTube ASR subtitles have overlapping timestamps and fragmented
sentences.  This module merges them into readable prose.
"""

import re
from typing import Optional

import srt


def parse_srt(srt_content: str) -> str:
    """Parse an SRT subtitle string into clean flowing text.

    Handles:
    - Sequence numbers and timestamps (removed)
    - HTML/formatting tags like <i>, <b>, <font color="..."> (stripped)
    - Duplicate / overlapping subtitle fragments (deduplicated)
    - Multiple whitespace / blank lines (normalized)

    Args:
        srt_content: Raw content of an .srt file.

    Returns:
        Clean flowing text with subtitle fragments joined into paragraphs.
    """
    subtitles = list(srt.parse(srt_content))

    lines: list[str] = []
    for sub in subtitles:
        text = _strip_tags(sub.content)
        text = text.strip()
        if text:
            lines.append(text)

    # Deduplicate overlapping fragments:
    # YouTube ASR often repeats the end of one subtitle at the start of the next.
    merged = _merge_overlapping_lines(lines)

    # Join into a single block of text; normalize whitespace
    result = " ".join(merged)
    result = re.sub(r" {2,}", " ", result)
    return result.strip()


def parse_srt_to_yaml(
    srt_content: str,
    *,
    source_url: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """Parse SRT content and wrap it in the Stage-0 YAML transcript format.

    The output is a minimal YAML wrapper around the flowing transcript text —
    just enough metadata (source URL, title, imported_at) for provenance.
    Any richer structure (speaker turns, splits, labels) is the job of the
    later zigzag stages, not of this importer.

    Speaker assignment is NOT performed here — the transcript is stored as
    unsegmented flowing text.  Speaker diarization is a separate step
    (manual or LLM-assisted).
    # TODO: post-dev — automated speaker diarization

    Args:
        srt_content: Raw .srt file content.
        source_url:  Optional YouTube URL for provenance.
        title:       Optional descriptive title for the transcript.

    Returns:
        YAML string ready to be stored in ``Topic.transcript_yaml``.
    """
    text = parse_srt(srt_content)

    yaml_lines = []
    if title:
        yaml_lines.append(f"title: \"{title}\"")
    if source_url:
        yaml_lines.append(f"source_url: \"{source_url}\"")
    yaml_lines.append("stage_0:")
    yaml_lines.append("  label: \"Raw transcript (auto-generated from SRT)\"")
    yaml_lines.append("  transcript: |")

    # Wrap text at ~80 chars for readability in YAML
    wrapped = _wrap_text(text, width=80)
    for line in wrapped:
        yaml_lines.append(f"    {line}")

    return "\n".join(yaml_lines) + "\n"


def _strip_tags(text: str) -> str:
    """Remove HTML/formatting tags from subtitle text."""
    return re.sub(r"<[^>]+>", "", text)


def _merge_overlapping_lines(lines: list[str]) -> list[str]:
    """Deduplicate overlapping subtitle fragments.

    YouTube ASR subtitles often repeat text across consecutive entries.
    For example:
        Entry 1: "so if you were to intentionally"
        Entry 2: "misgender a trans woman"
        Entry 3: "that could put her at risk of murder you"

    With overlapping timestamps, the end of one entry may be repeated at
    the start of the next.  This function detects and removes such overlaps.
    """
    if not lines:
        return []

    merged = [lines[0]]
    for line in lines[1:]:
        prev = merged[-1]
        # Check if the previous line ends with words that start the current line
        overlap = _find_overlap(prev, line)
        if overlap:
            # Append only the non-overlapping part
            merged.append(line[len(overlap):].strip())
        else:
            merged.append(line)

    # Filter out empty strings that may result from full overlaps
    return [m for m in merged if m]


def _find_overlap(prev: str, current: str) -> Optional[str]:
    """Find the overlapping suffix of `prev` that is a prefix of `current`.

    Returns the overlapping string, or None if no meaningful overlap exists.
    Only considers overlaps of at least 2 words to avoid false positives.
    """
    prev_words = prev.lower().split()
    current_words = current.lower().split()

    if len(prev_words) < 2 or len(current_words) < 2:
        return None

    # Try progressively smaller suffixes of prev as prefix of current
    max_check = min(len(prev_words), len(current_words))
    for size in range(max_check, 1, -1):  # at least 2 words overlap
        suffix = prev_words[-size:]
        prefix = current_words[:size]
        if suffix == prefix:
            # Return the overlap using the original (non-lowered) current text
            overlap_text = " ".join(current.split()[:size])
            return overlap_text

    return None


def _wrap_text(text: str, width: int = 80) -> list[str]:
    """Word-wrap text into lines of approximately `width` characters."""
    words = text.split()
    lines = []
    current_line: list[str] = []
    current_len = 0

    for word in words:
        if current_len + len(word) + (1 if current_line else 0) > width:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = []
                current_len = 0
        current_line.append(word)
        current_len += len(word) + (1 if len(current_line) > 1 else 0)

    if current_line:
        lines.append(" ".join(current_line))

    return lines

