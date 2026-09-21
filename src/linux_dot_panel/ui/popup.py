"""Reusable floating panel shell."""

from __future__ import annotations

import logging

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QKeyEvent, QKeySequence, QPalette, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from linux_dot_panel.config import TABS, Settings
from linux_dot_panel.insertion import TextInserter
from linux_dot_panel.storage.repositories.clipboard_repository import ClipboardRepository
from linux_dot_panel.storage.repositories.emoji_repository import EmojiRepository
from linux_dot_panel.ui.pages.clipboard_page import ClipboardPage
from linux_dot_panel.ui.pages.emoji_page import EmojiPage
from linux_dot_panel.ui.pages.text_picker_page import TextPickerPage
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

    def __init__(
        self,
        settings: Settings,
        emoji_repository: EmojiRepository | None = None,
        clipboard_repository: ClipboardRepository | None = None,
    ) -> None:
        super().__init__()
        self.settings = settings
        self.inserter = TextInserter()
        self._dark = is_dark(settings.theme)
        self.setWindowTitle("Linux Dot Panel")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(480, 480)
        self.resize(540, 560)
        self.setStyleSheet(stylesheet(self._dark))

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
            EmojiPage(emoji_repository, dark=self._dark) if emoji_repository is not None else None
        )
        self.clipboard_page = (
            ClipboardPage(clipboard_repository, dark=self._dark)
            if clipboard_repository is not None
            else None
        )
        self.kaomoji_page = TextPickerPage("Kaomoji", dark=self._dark)
        self.symbols_page = TextPickerPage("Symbols", dark=self._dark)
        for name in TABS:
            if name == "Emoji" and self.emoji_page is not None:
                page = self.emoji_page
            elif name == "Clipboard" and self.clipboard_page is not None:
                page = self.clipboard_page
            elif name == "Kaomoji":
                page = self.kaomoji_page
            elif name == "Symbols":
                page = self.symbols_page
            else:
                page = self._empty_page(name)
            self.pages.addWidget(page)
        content.addWidget(self.pages, 1)

        self.search.textChanged.connect(self._search_changed)
        self.search.returnPressed.connect(self._select_search_result)
        if self.emoji_page is not None:
            self.emoji_page.emoji_selected.connect(self._insert_text)
        if self.clipboard_page is not None:
            self.clipboard_page.copied.connect(self.hide_panel)
        self.kaomoji_page.text_selected.connect(self._insert_text)
        self.symbols_page.text_selected.connect(self._insert_text)

        self.hint = QLabel("Ctrl+Tab  Switch tab     Esc  Close")
        self.hint.setObjectName("hint")
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.addWidget(self.hint)
        hint_opacity = QGraphicsOpacityEffect(self.hint)
        self.hint.setGraphicsEffect(hint_opacity)
        self.hint_animation = QPropertyAnimation(hint_opacity, b"opacity", self)
        self.hint_animation.setDuration(180)
        self.hint_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

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
        if settings.theme == "system":
            QApplication.instance().paletteChanged.connect(self._refresh_theme)

    def _refresh_theme(self, _palette: QPalette) -> None:
        dark = is_dark(self.settings.theme)
        if dark == self._dark:
            return
        self._dark = dark
        self.setStyleSheet(stylesheet(dark))
        if self.emoji_page is not None:
            self.emoji_page.set_dark(dark)
        if self.clipboard_page is not None:
            self.clipboard_page.set_dark(dark)
        self.kaomoji_page.set_dark(dark)
        self.symbols_page.set_dark(dark)

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
        if name == "Clipboard" and self.clipboard_page is not None:
            self.clipboard_page.refresh()
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
        if not self.isVisible():
            self.inserter.capture_focused_field()
        self.hint_animation.stop()
        self.hint.graphicsEffect().setOpacity(1.0)
        self.hint.setText("Ctrl+Tab  Switch tab     Esc  Close")
        if self.emoji_page is not None and self.pages.currentIndex() == 0:
            self.emoji_page.refresh()
        if self.clipboard_page is not None and self.pages.currentIndex() == 1:
            self.clipboard_page.refresh()
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
            and event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up)
        ):
            view = None
            page = self.pages.currentWidget()
            if isinstance(page, EmojiPage) and page.model.records:
                view = page.grid
            elif isinstance(page, ClipboardPage) and page.model.records:
                view = page.list
            elif isinstance(page, TextPickerPage) and page.model.records:
                view = page.view
            if view is not None:
                view.setCurrentIndex(view.model().index(0, 0))
                view.setFocus()
                return True
        return super().eventFilter(watched, event)

    def _search_changed(self, text: str) -> None:
        if self.pages.currentIndex() == 0 and self.emoji_page is not None:
            self.emoji_page.set_query(text)
        elif self.pages.currentIndex() == 1 and self.clipboard_page is not None:
            self.clipboard_page.set_query(text)
        elif self.pages.currentIndex() == 2:
            self.kaomoji_page.set_query(text)
        elif self.pages.currentIndex() == 3:
            self.symbols_page.set_query(text)

    def _select_search_result(self) -> None:
        if self.pages.currentIndex() == 0 and self.emoji_page is not None:
            self.emoji_page.select_current_or_first()
        elif self.pages.currentIndex() == 1 and self.clipboard_page is not None:
            self.clipboard_page.select_current_or_first()
        elif self.pages.currentIndex() == 2:
            self.kaomoji_page.select_current_or_first()
        elif self.pages.currentIndex() == 3:
            self.symbols_page.select_current_or_first()

    def _insert_text(self, value: str) -> None:
        if self.inserter.insert(value):
            self.hint.setText("Inserted at the previous cursor position")
        else:
            QApplication.clipboard().setText(value)
            self.hint.setText("Copied — paste with Ctrl+V")
        self.hint_animation.stop()
        self.hint_animation.setStartValue(0.35)
        self.hint_animation.setEndValue(1.0)
        self.hint_animation.start()
