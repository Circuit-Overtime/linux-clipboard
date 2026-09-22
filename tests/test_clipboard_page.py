from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from win_dot_panel.config import Settings
from win_dot_panel.storage.database import open_database
from win_dot_panel.storage.repositories.clipboard_repository import ClipboardRepository
from win_dot_panel.ui.popup import PopupPanel


def test_clipboard_page_search_manage_copy_and_pagination(tmp_path, monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    connection = open_database(tmp_path / "panel.db")
    repository = ClipboardRepository(connection)
    for index in range(35):
        repository.record_text(f"note {index}", f"hash-{index}", timestamp=index, history_limit=100)

    panel = PopupPanel(Settings(), clipboard_repository=repository)
    panel.select_tab(1, persist=False)
    page = panel.clipboard_page
    assert len(page.model.records) == 30
    assert page.has_more
    page.load_more()
    assert len(page.model.records) == 35
    assert not page.has_more

    page.set_query("note 17")
    assert len(page.model.records) == 1
    item_id = page.model.records[0].id
    page.list.setCurrentIndex(page.model.index(0, 0))
    page.toggle_pin()
    assert repository.get(item_id).is_pinned
    assert page.pin_button.text() == "Unpin"

    panel.show()
    page.copy_button.click()
    assert app.clipboard().text() == "note 17"
    assert not panel.isVisible()

    page.set_query("note 18")
    page.list.setCurrentIndex(page.model.index(0, 0))
    deleted_id = page.model.records[0].id
    page.delete_current()
    assert repository.get(deleted_id) is None

    page.clear_button.click()
    assert page.clear_button.text() == "Confirm clear"
    assert repository.get(item_id) is not None
    page.clear_button.click()
    assert repository.get(item_id) is not None
    assert [item.id for item in repository.list_recent()] == [item_id]
    panel.close()
    connection.close()


def test_clipboard_page_copies_full_text_after_loading_only_a_preview(tmp_path, monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    connection = open_database(tmp_path / "panel.db")
    repository = ClipboardRepository(connection)
    content = "start " + "x" * 500 + " ending"
    repository.record_text(content, "long-hash", timestamp=1, history_limit=100)
    panel = PopupPanel(Settings(), clipboard_repository=repository)
    panel.select_tab(1, persist=False)
    page = panel.clipboard_page

    assert len(page.model.records[0].preview) == 240
    page.set_query("ending")
    assert len(page.model.records) == 1
    QTest.keyClick(page.list, Qt.Key.Key_Return)
    assert app.clipboard().text() == content
    panel.close()
    connection.close()
