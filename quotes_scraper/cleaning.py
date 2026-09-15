"""String and field cleaning helpers."""

from __future__ import annotations

import html
import re
from typing import Iterable

_WHITESPACE_RE = re.compile(r"\s+")
_WRAPPING_QUOTES = ('"', "'", "“", "”", "‘", "’")


def clean_text(value: str | None) -> str:
    """Unescape HTML entities, collapse whitespace, and strip wrapping quotes."""
    if not value:
        return ""

    text = html.unescape(value)
    text = _WHITESPACE_RE.sub(" ", text).strip()

    while len(text) >= 2 and text[0] in _WRAPPING_QUOTES and text[-1] in _WRAPPING_QUOTES:
        text = text[1:-1].strip()

    return text


def clean_tags(tags: Iterable[str]) -> list[str]:
    """Return unique, cleaned tags while preserving first-seen order."""
    cleaned: list[str] = []
    seen: set[str] = set()

    for tag in tags:
        normalized = clean_text(tag).lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(normalized)

    return cleaned
