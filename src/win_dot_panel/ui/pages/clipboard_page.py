"""Paged clipboard history with copy and management actions."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QKeyEvent, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from win_dot_panel.clipboard.models import ClipboardPreview
from win_dot_panel.storage.repositories.clipboard_repository import ClipboardRepository

PAGE_SIZE = 30


class ClipboardListModel(QAbstractListModel):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[ClipboardPreview] = []

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return 0 if parent is not None and parent.isValid() else len(self.records)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self.records):
            return None
        record = self.records[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return record.preview
        if role == Qt.ItemDataRole.AccessibleTextRole:
            label = "Pinned clipboard item" if record.is_pinned else "Clipboard item"
            return f"{label}: {record.preview}"
        if role == Qt.ItemDataRole.ToolTipRole:
            return record.preview
        if role == Qt.ItemDataRole.UserRole:
            return record.id
        return None

    def replace(self, records: list[ClipboardPreview]) -> None:
        self.beginResetModel()
        self.records = records
        self.endResetModel()

    def append(self, records: list[ClipboardPreview]) -> None:
        if not records:
            return
        start = len(self.records)
        self.beginInsertRows(QModelIndex(), start, start + len(records) - 1)
        self.records.extend(records)
        self.endInsertRows()


class ClipboardCardDelegate(QStyledItemDelegate):
    def __init__(self, *, dark: bool, parent: QWidget) -> None:
        super().__init__(parent)
        self.dark = dark

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        record: ClipboardPreview = index.model().records[index.row()]
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        if selected:
            fill = "#405476" if self.dark else "#e5edfb"
        else:
            fill = "#34363d" if self.dark else "#f5f6f8"
        if hovered and not selected:
            fill = "#3c3f49" if self.dark else "#f0f2f7"
        painter.setBrush(QColor(fill))
        painter.setPen(QColor("#555862" if self.dark else "#e1e3e8"))
        card = option.rect.adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(card, 11, 11)

        left = card.left() + 14
        width = card.width() - 28
        text = record.preview.replace("\t", "    ").splitlines()
        title = text[0] if text else ""
        font = QFont(option.font)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)
        painter.setPen(QColor("#f4f4f6" if self.dark else "#20232b"))
        metrics = painter.fontMetrics()
        available = width - (64 if record.is_pinned else 0)
        painter.drawText(
            QRect(left, card.top() + 12, available, 22),
            Qt.AlignmentFlag.AlignVCenter,
            metrics.elidedText(title, Qt.TextElideMode.ElideRight, available),
        )

        painter.setFont(option.font)
        painter.setPen(QColor("#a6a9b2" if self.dark else "#727782"))
        detail = text[1] if len(text) > 1 else f"{record.char_count} characters"
        if record.char_count > len(record.preview) and len(text) > 1:
            detail += "…"
        painter.drawText(
            QRect(left, card.top() + 39, width, 20),
            Qt.AlignmentFlag.AlignVCenter,
            painter.fontMetrics().elidedText(detail, Qt.TextElideMode.ElideRight, width),
        )
        if record.is_pinned:
            painter.setPen(QColor("#87adff" if self.dark else "#336dca"))
            painter.drawText(
                QRect(card.right() - 71, card.top() + 11, 57, 22),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                "Pinned",
            )
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(100, 72)


class ClipboardList(QListView):
    copy_requested = Signal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.copy_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class ClipboardPage(QWidget):
    copied = Signal()

    def __init__(self, repository: ClipboardRepository, *, dark: bool) -> None:
        super().__init__()
        self.repository = repository
        self.query = ""
        self.has_more = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        heading = QHBoxLayout()
        title = QLabel("History")
        title.setObjectName("clipboardHeading")
        heading.addWidget(title)
        heading.addStretch()
        self.clear_button = QPushButton("Clear unpinned")
        self.clear_button.setObjectName("clipboardClear")
        self.clear_button.clicked.connect(self.confirm_clear)
        self.clear_timer = QTimer(self)
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self._reset_clear)
        self._clear_armed = False
        heading.addWidget(self.clear_button)
        layout.addLayout(heading)

        self.model = ClipboardListModel()
        self.list = ClipboardList()
        self.list.setObjectName("clipboardList")
        self.list.setAccessibleName("Clipboard history")
        self.list.setModel(self.model)
        self.list.setItemDelegate(ClipboardCardDelegate(dark=dark, parent=self.list))
        self.list.setSpacing(5)
        self.list.setUniformItemSizes(True)
        self.list.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self.list.doubleClicked.connect(self.copy_current)
        self.list.copy_requested.connect(self.copy_current)
        self.list.selectionModel().currentChanged.connect(self._selection_changed)
        layout.addWidget(self.list, 1)

        self.empty = QLabel("No copied text yet")
        self.empty.setObjectName("emptyCaption")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty)

        actions = QHBoxLayout()
        self.copy_button = QPushButton("Copy")
        self.copy_button.setObjectName("clipboardCopy")
        self.copy_button.clicked.connect(self.copy_current)
        actions.addWidget(self.copy_button)
        self.pin_button = QPushButton("Pin")
        self.pin_button.setObjectName("clipboardPin")
        self.pin_button.clicked.connect(self.toggle_pin)
        actions.addWidget(self.pin_button)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("clipboardDelete")
        self.delete_button.clicked.connect(self.delete_current)
        actions.addWidget(self.delete_button)
        layout.addLayout(actions)

        self.more = QPushButton("Load more")
        self.more.setObjectName("clipboardMore")
        self.more.clicked.connect(self.load_more)
        layout.addWidget(self.more)
        self.refresh()

    def set_dark(self, dark: bool) -> None:
        self.list.itemDelegate().dark = dark
        self.list.viewport().update()

    def set_query(self, text: str) -> None:
        self.query = text.strip()
        self.refresh()

    def refresh(self, *, select_id: int | None = None) -> None:
        records = self.repository.list_previews(query=self.query, limit=PAGE_SIZE + 1)
        self.has_more = len(records) > PAGE_SIZE
        self.model.replace(records[:PAGE_SIZE])
        self._update_view()
        if select_id is not None:
            for row, record in enumerate(self.model.records):
                if record.id == select_id:
                    self.list.setCurrentIndex(self.model.index(row, 0))
                    return
        if self.model.records:
            self.list.setCurrentIndex(self.model.index(0, 0))

    def load_more(self) -> None:
        offset = len(self.model.records)
        records = self.repository.list_previews(
            query=self.query, limit=PAGE_SIZE + 1, offset=offset
        )
        self.has_more = len(records) > PAGE_SIZE
        self.model.append(records[:PAGE_SIZE])
        self._update_view()

    def _update_view(self) -> None:
        has_items = bool(self.model.records)
        self.list.setVisible(has_items)
        self.empty.setText("No matches" if self.query else "No copied text yet")
        self.empty.setVisible(not has_items)
        self.more.setVisible(self.has_more)
        self._selection_changed()

    def _current(self) -> ClipboardPreview | None:
        index = self.list.currentIndex()
        if not index.isValid() or index.row() >= len(self.model.records):
            return None
        return self.model.records[index.row()]

    def _selection_changed(self) -> None:
        record = self._current()
        selected = record is not None
        self.copy_button.setEnabled(selected)
        self.pin_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)
        self.pin_button.setText("Unpin" if selected and record.is_pinned else "Pin")

    def select_current_or_first(self) -> None:
        if self._current() is None and self.model.records:
            self.list.setCurrentIndex(self.model.index(0, 0))
        self.copy_current()

    def copy_current(self, _index: QModelIndex | None = None) -> None:
        record = self._current()
        if record is None:
            return
        item = self.repository.get(record.id)
        if item is None:
            self.refresh()
            return
        QApplication.clipboard().setText(item.text_content)
        self.copied.emit()

    def toggle_pin(self) -> None:
        record = self._current()
        if record is not None and self.repository.set_pinned(record.id, not record.is_pinned):
            self.refresh(select_id=record.id)

    def delete_current(self) -> None:
        record = self._current()
        if record is not None and self.repository.delete(record.id):
            self.refresh()

    def confirm_clear(self) -> None:
        if not self._clear_armed:
            self._clear_armed = True
            self.clear_button.setText("Confirm clear")
            self.clear_timer.start(4000)
            return
        self.repository.clear()
        self._reset_clear()
        self.refresh()

    def _reset_clear(self) -> None:
        self._clear_armed = False
        self.clear_timer.stop()
        self.clear_button.setText("Clear unpinned")
