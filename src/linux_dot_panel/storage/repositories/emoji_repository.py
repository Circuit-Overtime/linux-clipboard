"""Bundled emoji records and persistent recent usage."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable

from linux_dot_panel.emoji.models import EmojiRecord


def _emoji(row: sqlite3.Row) -> EmojiRecord:
    return EmojiRecord(
        id=row["id"],
        emoji=row["emoji"],
        name=row["name"],
        category=row["category"],
        subcategory=row["subcategory"],
        keywords=row["keywords"],
        sort_order=row["sort_order"],
    )


class EmojiRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def insert_many(self, records: Iterable[EmojiRecord]) -> None:
        with self.connection:
            self.connection.executemany(
                """
                INSERT INTO emoji (id, emoji, name, category, subcategory, keywords, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    emoji = excluded.emoji,
                    name = excluded.name,
                    category = excluded.category,
                    subcategory = excluded.subcategory,
                    keywords = excluded.keywords,
                    sort_order = excluded.sort_order
                """,
                (
                    (
                        record.id,
                        record.emoji,
                        record.name,
                        record.category,
                        record.subcategory,
                        record.keywords,
                        record.sort_order,
                    )
                    for record in records
                ),
            )

    def get(self, emoji_id: int) -> EmojiRecord | None:
        row = self.connection.execute("SELECT * FROM emoji WHERE id = ?", (emoji_id,)).fetchone()
        return _emoji(row) if row is not None else None

    def record_usage(self, emoji_id: int, *, timestamp: int) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO emoji_usage (emoji_id, use_count, last_used_at)
                VALUES (?, 1, ?)
                ON CONFLICT(emoji_id) DO UPDATE SET
                    use_count = emoji_usage.use_count + 1,
                    last_used_at = excluded.last_used_at
                """,
                (emoji_id, timestamp),
            )

    def list_recent(self, *, limit: int = 30) -> list[EmojiRecord]:
        if limit < 1:
            raise ValueError("limit must be positive")
        rows = self.connection.execute(
            """
            SELECT emoji.* FROM emoji
            JOIN emoji_usage ON emoji_usage.emoji_id = emoji.id
            ORDER BY emoji_usage.last_used_at DESC, emoji_usage.emoji_id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [_emoji(row) for row in rows]
