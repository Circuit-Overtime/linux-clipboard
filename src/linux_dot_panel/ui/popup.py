"""Reusable floating panel shell."""

from __future__ import annotations

import logging

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QKeyEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from linux_dot_panel.config import TABS, Settings
from linux_dot_panel.storage.repositories.emoji_repository import EmojiRepository
from linux_dot_panel.ui.pages.emoji_page import EmojiPage
from linux_dot_panel.ui.theme import is_dark, stylesheet

LOGGER = logging.getLogger(__name__)


PAGE_TEXT = {
    "Emoji": ("☺", "Find the right emoji", "Search or browse your favorite expressions."),
    "Clipboard": ("▤", "Your clipboard, close at hand", "Recent copied text will appear here."),
    "Kaomoji": ("( ˶ˆᗜˆ˵ )", "A little more expression", "Kaomoji will appear here."),
    "Symbols": ("✦", "Every symbol in one place", "Search for arrows, marks, and more."),
}


class PopupPanel(QWidget):
    panel_hidden = Signal()

    def __init__(self, settings: Settings, emoji_repository: EmojiRepository | None = None) -> None:
        super().__init__()
        self.settings = settings
        self.setWindowTitle("Linux Dot Panel")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(480, 480)
        self.resize(540, 560)
        self.setStyleSheet(stylesheet(is_dark(settings.theme)))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        panel = QFrame()
        panel.setObjectName("panel")
        outer.addWidget(panel)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 65))
        panel.setGraphicsEffect(shadow)

        content = QVBoxLayout(panel)
        content.setContentsMargins(24, 22, 24, 18)
        content.setSpacing(16)

        title = QLabel("Dot Panel")
        title.setObjectName("title")
        content.addWidget(title)

        self.search = QLineEdit()
        self.search.setObjectName("search")
        self.search.setClearButtonEnabled(True)
        self.search.setAccessibleName("Search current tab")
        self.search.installEventFilter(self)
        content.addWidget(self.search)

        tab_bar = QFrame()
        tab_bar.setObjectName("tabBar")
        tabs_layout = QHBoxLayout(tab_bar)
        tabs_layout.setContentsMargins(4, 4, 4, 4)
        tabs_layout.setSpacing(3)
        self.tab_buttons: list[QPushButton] = []
        for index, name in enumerate(TABS):
            button = QPushButton(name)
            button.setProperty("tabButton", True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setAccessibleName(f"{name} tab")
            button.clicked.connect(lambda checked=False, tab=index: self.select_tab(tab))
            tabs_layout.addWidget(button, 1)
            self.tab_buttons.append(button)
        content.addWidget(tab_bar)

        self.pages = QStackedWidget()
        self.emoji_page = (
            EmojiPage(emoji_repository, dark=is_dark(settings.theme))
            if emoji_repository is not None
            else None
        )
        for name in TABS:
            page = (
                self.emoji_page if name == "Emoji" and self.emoji_page else self._empty_page(name)
            )
            self.pages.addWidget(page)
        content.addWidget(self.pages, 1)

        self.search.textChanged.connect(self._search_changed)
        self.search.returnPressed.connect(self._select_search_result)
        if self.emoji_page is not None:
            self.emoji_page.emoji_selected.connect(self.hide_panel)

        hint = QLabel("Ctrl+Tab  Switch tab     Esc  Close")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.addWidget(hint)

        next_tab = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab.activated.connect(
            lambda: self.select_tab((self.pages.currentIndex() + 1) % len(TABS))
        )
        previous_tab = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        previous_tab.activated.connect(
            lambda: self.select_tab((self.pages.currentIndex() - 1) % len(TABS))
        )
        close = QShortcut(QKeySequence("Escape"), self)
        close.activated.connect(self.hide_panel)

        self.select_tab(TABS.index(settings.last_tab), persist=False)

    def _empty_page(self, name: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        icon, heading, caption = PAGE_TEXT[name]
        for text, object_name in (
            (icon, "emptyIcon"),
            (heading, "emptyTitle"),
            (caption, "emptyCaption"),
        ):
            label = QLabel(text)
            label.setObjectName(object_name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        return page

    def select_tab(self, index: int, *, persist: bool = True) -> None:
        self.pages.setCurrentIndex(index)
        name = TABS[index]
        self.search.setPlaceholderText(f"Search {name.lower()}…")
        self.search.clear()
        for tab_index, button in enumerate(self.tab_buttons):
            button.setProperty("active", tab_index == index)
            button.style().unpolish(button)
            button.style().polish(button)
        if persist and self.settings.last_tab != name:
            self.settings.last_tab = name
            try:
                self.settings.save()
            except OSError as error:
                LOGGER.warning("Could not save settings: %s", error)
        self.search.setFocus()

    def show_panel(self) -> None:
        if self.emoji_page is not None and self.pages.currentIndex() == 0:
            self.emoji_page.refresh()
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            self.move(
                area.x() + (area.width() - self.width()) // 2,
                area.y() + (area.height() - self.height()) // 2 + 20,
            )
        self.show()
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(0, self.search.setFocus)

    def hide_panel(self) -> None:
        if self.isVisible():
            self.hide()
            self.panel_hidden.emit()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.WindowDeactivate and self.isVisible():
            self.hide_panel()
        super().changeEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if (
            watched is self.search
            and isinstance(event, QKeyEvent)
            and event.type() == QEvent.Type.KeyPress
            and event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up, Qt.Key.Key_Left, Qt.Key.Key_Right)
            and self.pages.currentIndex() == 0
            and self.emoji_page is not None
            and self.emoji_page.model.records
        ):
            self.emoji_page.grid.setFocus()
            return True
        return super().eventFilter(watched, event)

    def _search_changed(self, text: str) -> None:
        if self.pages.currentIndex() == 0 and self.emoji_page is not None:
            self.emoji_page.set_query(text)

    def _select_search_result(self) -> None:
        if self.pages.currentIndex() == 0 and self.emoji_page is not None:
            self.emoji_page.select_current_or_first()
