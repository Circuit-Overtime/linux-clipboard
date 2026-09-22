"""Event-driven X11 clipboard tracking through Qt."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication


class X11ClipboardBackend(QObject):
    clipboard_changed = Signal(str, bool)

    def __init__(self) -> None:
        super().__init__()
        self.clipboard = QApplication.clipboard()

    def start(self) -> bool:
        self.clipboard.dataChanged.connect(self._changed)
        return True

    def stop(self) -> None:
        try:
            self.clipboard.dataChanged.disconnect(self._changed)
        except (RuntimeError, TypeError):
            pass

    def get_text(self) -> str:
        return self.clipboard.text()

    def set_text(self, text: str) -> None:
        self.clipboard.setText(text)

    def _changed(self) -> None:
        mime = self.clipboard.mimeData()
        if mime is None or not mime.hasText():
            return
        sensitive = mime.hasFormat("application/x-kde-passwordManagerHint")
        self.clipboard_changed.emit(mime.text(), sensitive)
