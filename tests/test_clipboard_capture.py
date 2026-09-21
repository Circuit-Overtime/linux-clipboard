from __future__ import annotations

from linux_dot_panel.clipboard.capture import MAX_TEXT_BYTES, ClipboardCapture
from linux_dot_panel.storage.database import open_database
from linux_dot_panel.storage.repositories.clipboard_repository import ClipboardRepository


def test_capture_deduplicates_and_rejects_unsafe_text(tmp_path):
    connection = open_database(tmp_path / "panel.db")
    repository = ClipboardRepository(connection)
    capture = ClipboardCapture(repository, history_limit=1)

    assert capture.capture("first\r\nline")
    assert capture.capture("first\nline")
    assert repository.list_recent()[0].use_count == 2
    assert repository.list_recent()[0].text_content == "first\nline"

    assert not capture.capture("secret", sensitive=True)
    assert not capture.capture("")
    assert not capture.capture("bad\x00text")
    assert not capture.capture("x" * (MAX_TEXT_BYTES + 1))
    assert len(repository.list_recent()) == 1

    assert capture.capture("second")
    assert [item.text_content for item in repository.list_recent()] == ["second"]
    connection.close()
