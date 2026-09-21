from __future__ import annotations

from PySide6.QtWidgets import QApplication

from linux_dot_panel.emoji.importer import ensure_emoji_dataset
from linux_dot_panel.storage.database import open_database
from linux_dot_panel.ui.pages.emoji_page import EmojiPage


def test_search_selection_copies_emoji_and_updates_recents(tmp_path, monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    connection = open_database(tmp_path / "panel.db")
    page = EmojiPage(ensure_emoji_dataset(connection), dark=False)

    page.set_query("rocket")
    assert page.model.records[0].emoji == "🚀"
    page.select_current_or_first()
    assert app.clipboard().text() == "🚀"

    page.set_query("")
    page.category.setCurrentText("Recent")
    assert page.model.records[0].emoji == "🚀"
    page.close()
    connection.close()
