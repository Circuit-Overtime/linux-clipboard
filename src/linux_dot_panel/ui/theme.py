"""A neutral, macOS-inspired panel palette."""

from __future__ import annotations

from string import Template

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication


def is_dark(theme: str) -> bool:
    if theme != "system":
        return theme == "dark"
    app = QApplication.instance()
    return bool(app and app.palette().color(QPalette.ColorRole.Window).lightness() < 128)


def stylesheet(dark: bool) -> str:
    colors = (
        {
            "surface": "#25262b",
            "field": "#34363d",
            "segment": "#303138",
            "selected": "#4a4d57",
            "border": "#555862",
            "text": "#f4f4f6",
            "muted": "#a6a9b2",
            "accent": "#87adff",
        }
        if dark
        else {
            "surface": "#fcfcfd",
            "field": "#f0f1f4",
            "segment": "#edeef1",
            "selected": "#ffffff",
            "border": "#d9dce2",
            "text": "#20232b",
            "muted": "#727782",
            "accent": "#336dca",
        }
    )
    return Template("""
    QFrame#panel {
        background: $surface;
        border: 1px solid $border;
        border-radius: 20px;
    }
    QLabel#title { color: $text; font-size: 18px; font-weight: 650; }
    QLabel#subtitle, QLabel#hint, QLabel#emptyCaption { color: $muted; }
    QLabel#emptyTitle { color: $text; font-size: 18px; font-weight: 600; }
    QLabel#emptyIcon { color: $accent; font-size: 38px; }
    QLineEdit#search {
        background: $field;
        color: $text;
        border: 1px solid transparent;
        border-radius: 12px;
        padding: 11px 14px;
        font-size: 14px;
        selection-background-color: $accent;
    }
    QLineEdit#search:focus { border-color: $accent; }
    QFrame#tabBar {
        background: $segment;
        border-radius: 12px;
    }
    QPushButton[tabButton="true"] {
        color: $muted;
        background: transparent;
        border: none;
        border-radius: 9px;
        padding: 9px 11px;
        font-size: 13px;
        font-weight: 550;
    }
    QPushButton[tabButton="true"]:hover { color: $text; }
    QPushButton[tabButton="true"][active="true"] {
        color: $text;
        background: $selected;
        border: 1px solid $border;
    }
    QComboBox#emojiCategory, QPushButton#loadMore {
        color: $text;
        background: $field;
        border: 1px solid $border;
        border-radius: 9px;
        padding: 6px 10px;
    }
    QListView#emojiGrid {
        background: transparent;
        border: none;
        outline: none;
    }
    QListView#emojiGrid QScrollBar:vertical {
        background: transparent;
        width: 8px;
        margin: 2px 0;
    }
    QListView#emojiGrid QScrollBar::handle:vertical {
        background: $border;
        border-radius: 4px;
        min-height: 20px;
    }
    QListView#emojiGrid QScrollBar::add-line:vertical,
    QListView#emojiGrid QScrollBar::sub-line:vertical {
        height: 0;
    }
    QListView#emojiGrid QScrollBar::add-page:vertical,
    QListView#emojiGrid QScrollBar::sub-page:vertical {
        background: transparent;
    }
    """).substitute(colors)
