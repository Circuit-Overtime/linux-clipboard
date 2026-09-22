"""Offline kaomoji and symbol browsers."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QKeyEvent, QPainter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListView,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from win_dot_panel.text_picker.data import KAOMOJI, SYMBOLS, TextItem
from win_dot_panel.ui.widgets.category_combo import CategoryComboBox


class TextItemModel(QAbstractListModel):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[TextItem] = []

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return 0 if parent is not None and parent.isValid() else len(self.records)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self.records):
            return None
        item = self.records[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return item.value
        if role in (Qt.ItemDataRole.ToolTipRole, Qt.ItemDataRole.AccessibleTextRole):
            return item.name
        return None

    def replace(self, records: list[TextItem]) -> None:
        self.beginResetModel()
        self.records = records
        self.endResetModel()


class PickerView(QListView):
    selected = Signal(QModelIndex)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.selected.emit(self.currentIndex())
            event.accept()
            return
        super().keyPressEvent(event)


class SymbolDelegate(QStyledItemDelegate):
    def __init__(self, *, dark: bool, parent: QWidget) -> None:
        super().__init__(parent)
        self.dark = dark

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        if selected or hovered:
            painter.setBrush(QColor("#4a4d57" if self.dark else "#e8ecf5"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(option.rect.adjusted(2, 2, -2, -2), 11, 11)
        font = QFont(option.font)
        font.setPointSize(23)
        painter.setFont(font)
        painter.setPen(QColor("#f4f4f6" if self.dark else "#20232b"))
        painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, str(index.data()))
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(56, 58)


class KaomojiDelegate(QStyledItemDelegate):
    def __init__(self, *, dark: bool, parent: QWidget) -> None:
        super().__init__(parent)
        self.dark = dark

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        item: TextItem = index.model().records[index.row()]
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        if selected:
            background = "#405476" if self.dark else "#e5edfb"
        elif hovered:
            background = "#3c3f49" if self.dark else "#f0f2f7"
        else:
            background = "#34363d" if self.dark else "#f5f6f8"
        card = option.rect.adjusted(2, 2, -2, -2)
        painter.setBrush(QColor(background))
        painter.setPen(QColor("#555862" if self.dark else "#e1e3e8"))
        painter.drawRoundedRect(card, 10, 10)
        left = card.left() + 13
        width = card.width() - 26
        font = QFont(option.font)
        font.setPointSize(16)
        painter.setFont(font)
        painter.setPen(QColor("#f4f4f6" if self.dark else "#20232b"))
        painter.drawText(
            QRect(left, card.top() + 5, width, 27),
            Qt.AlignmentFlag.AlignVCenter,
            painter.fontMetrics().elidedText(item.value, Qt.TextElideMode.ElideRight, width),
        )
        painter.setFont(option.font)
        painter.setPen(QColor("#a6a9b2" if self.dark else "#727782"))
        painter.drawText(QRect(left, card.top() + 35, width, 17), item.name)
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(100, 63)


class TextPickerPage(QWidget):
    text_selected = Signal(str)

    def __init__(self, kind: str, *, dark: bool) -> None:
        super().__init__()
        if kind not in ("Kaomoji", "Symbols"):
            raise ValueError(f"Unsupported text picker: {kind}")
        self.kind = kind
        self.items = KAOMOJI if kind == "Kaomoji" else SYMBOLS
        self.query = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        heading = QHBoxLayout()
        label = QLabel("Browse")
        label.setObjectName("textPickerHeading")
        heading.addWidget(label)
        heading.addStretch()
        self.category = CategoryComboBox(dark=dark)
        self.category.setAccessibleName(f"{kind} category")
        self.category.addItems(["All", *dict.fromkeys(item.category for item in self.items)])
        self.category.currentTextChanged.connect(self.refresh)
        heading.addWidget(self.category)
        layout.addLayout(heading)

        self.model = TextItemModel()
        self.view = PickerView()
        self.view.setObjectName("textPickerList")
        self.view.setAccessibleName(f"{kind} results")
        self.view.setModel(self.model)
        self.view.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        if kind == "Symbols":
            self.view.setItemDelegate(SymbolDelegate(dark=dark, parent=self.view))
            self.view.setViewMode(QListView.ViewMode.IconMode)
            self.view.setFlow(QListView.Flow.LeftToRight)
            self.view.setWrapping(True)
            self.view.setResizeMode(QListView.ResizeMode.Adjust)
            self.view.setMovement(QListView.Movement.Static)
            self.view.setGridSize(QSize(56, 58))
            self.view.setUniformItemSizes(True)
        else:
            self.view.setItemDelegate(KaomojiDelegate(dark=dark, parent=self.view))
            self.view.setSpacing(5)
            self.view.setUniformItemSizes(True)
        self.view.clicked.connect(self.select_index)
        self.view.selected.connect(self.select_index)
        layout.addWidget(self.view, 1)

        self.empty = QLabel(f"No {kind.lower()} found")
        self.empty.setObjectName("emptyCaption")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty)
        self.refresh()

    def set_dark(self, dark: bool) -> None:
        self.category.set_dark(dark)
        self.view.itemDelegate().dark = dark
        self.view.viewport().update()

    def set_query(self, text: str) -> None:
        self.query = text.strip().casefold()
        self.refresh()

    def refresh(self) -> None:
        category = self.category.currentText()
        terms = self.query.split()
        records = [
            item
            for item in self.items
            if (category == "All" or item.category == category)
            and all(
                term in f"{item.value} {item.name} {item.keywords}".casefold() for term in terms
            )
        ]
        self.model.replace(records)
        self.view.setVisible(bool(records))
        self.empty.setVisible(not records)
        if records:
            self.view.setCurrentIndex(self.model.index(0, 0))

    def select_current_or_first(self) -> None:
        index = self.view.currentIndex()
        if not index.isValid() and self.model.records:
            index = self.model.index(0, 0)
        self.select_index(index)

    def select_index(self, index: QModelIndex) -> None:
        if index.isValid():
            self.text_selected.emit(self.model.records[index.row()].value)
