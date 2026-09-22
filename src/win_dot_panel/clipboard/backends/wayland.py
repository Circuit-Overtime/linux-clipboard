"""One persistent wl-paste watcher for Wayland clipboard changes."""

from __future__ import annotations

import logging
import shutil
import sys

from PySide6.QtCore import QObject, QProcess, Signal
from PySide6.QtWidgets import QApplication

LOGGER = logging.getLogger(__name__)

from win_dot_panel.clipboard.backends.x11 import X11ClipboardBackend


class WaylandClipboardBackend(QObject):
    clipboard_changed = Signal(str, bool)
    image_changed = Signal(bytes, str, bool)

    def __init__(self) -> None:
        super().__init__()
        self.process = QProcess(self)
        self.fallback = X11ClipboardBackend()
        self.fallback.clipboard_changed.connect(self.clipboard_changed)
        self.fallback.image_changed.connect(self.image_changed)
        self._using_fallback = False
        self._stopping = False
        self.process.errorOccurred.connect(self._failed)
        self.process.finished.connect(self._finished)

    def start(self) -> bool:
        executable = shutil.which("wl-paste")
        if executable is None:
            LOGGER.warning("Wayland clipboard monitoring needs the wl-clipboard system package")
            self._enable_fallback()
            return True
        self.process.start(
            executable,
            [
                "--watch",
                sys.executable,
                "-m",
                "win_dot_panel.clipboard.watch_event",
            ],
        )
        if not self.process.waitForStarted(500):
            LOGGER.warning(
                "Could not start Wayland clipboard watcher: %s", self.process.errorString()
            )
            self._enable_fallback()
        return True

    def stop(self) -> None:
        self._stopping = True
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
                self.process.waitForFinished(1000)
        if self._using_fallback:
            self.fallback.stop()

    def _enable_fallback(self) -> None:
        if not self._using_fallback and not self._stopping:
            LOGGER.warning("Using Qt clipboard monitoring because wl-paste watch is unavailable")
            self._using_fallback = True
            self.fallback.start()

    def get_text(self) -> str:
        return QApplication.clipboard().text()

    def set_text(self, text: str) -> None:
        QApplication.clipboard().setText(text)

    def _failed(self, _error: QProcess.ProcessError) -> None:
        LOGGER.warning("Wayland clipboard watcher failed: %s", self.process.errorString())
        self._enable_fallback()

    def _finished(self, code: int, _status: QProcess.ExitStatus) -> None:
        if code != 0 and not self._stopping:
            LOGGER.warning("Wayland clipboard watcher exited with status %d", code)
        self._enable_fallback()
