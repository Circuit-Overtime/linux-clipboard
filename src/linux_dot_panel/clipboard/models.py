"""Stored clipboard item data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ClipboardItem:
    id: int
    text_content: str
    content_hash: str
    created_at: int
    last_used_at: int
    use_count: int
    is_pinned: bool


@dataclass(frozen=True, slots=True)
class ClipboardPreview:
    id: int
    preview: str
    char_count: int
    use_count: int
    is_pinned: bool
