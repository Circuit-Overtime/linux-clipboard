from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from linux_dot_panel.config import Settings
from linux_dot_panel.ui.popup import PopupPanel


def test_kaomoji_search_and_insert_keeps_panel_open(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    QApplication.instance() or QApplication([])
    panel = PopupPanel(Settings())
    inserted: list[str] = []
    monkeypatch.setattr(panel.inserter, "insert", lambda value: inserted.append(value) or True)
    panel.select_tab(2, persist=False)
    panel.show()

    panel.search.setText("shrug")
    assert [item.name for item in panel.kaomoji_page.model.records] == ["Shrug"]
    QTest.keyClick(panel.search, Qt.Key.Key_Return)
    assert inserted == ["¯\\_(ツ)_/¯"]
    assert panel.isVisible()

    panel.search.clear()
    panel.kaomoji_page.category.setCurrentText("Love")
    panel.search.setText("hug")
    assert {item.name for item in panel.kaomoji_page.model.records} == {"Hug", "Open arms"}
    panel.close()


def test_symbols_search_category_and_copy_fallback(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    panel = PopupPanel(Settings())
    monkeypatch.setattr(panel.inserter, "insert", lambda value: False)
    panel.select_tab(3, persist=False)

    panel.search.setText("copyright")
    assert panel.symbols_page.model.records[0].value == "©"
    panel.symbols_page.select_current_or_first()
    assert app.clipboard().text() == "©"

    panel.search.clear()
    panel.symbols_page.category.setCurrentText("Arrows")
    panel.search.setText("right arrow")
    assert "→" in [item.value for item in panel.symbols_page.model.records]
    panel.search.setText("copyright")
    assert panel.symbols_page.model.records == []
    panel.close()
