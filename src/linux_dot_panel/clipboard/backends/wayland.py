"""One persistent wl-paste watcher for Wayland clipboard changes."""

from __future__ import annotations

import logging
import shutil
import sys

from PySide6.QtCore import QObject, QProcess
from PySide6.QtWidgets import QApplication

LOGGER = logging.getLogger(__name__)


class WaylandClipboardBackend(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.process = QProcess(self)
        self.process.errorOccurred.connect(self._failed)
        self.process.finished.connect(self._finished)

    def start(self) -> bool:
        executable = shutil.which("wl-paste")
        if executable is None:
            LOGGER.warning("Clipboard monitoring needs wl-clipboard on Wayland")
            return False
        self.process.start(
            executable,
            [
                "--type",
                "text",
                "--watch",
                sys.executable,
                "-m",
                "linux_dot_panel.clipboard.watch_event",
            ],
        )
        if not self.process.waitForStarted(500):
            LOGGER.warning(
                "Could not start Wayland clipboard watcher: %s", self.process.errorString()
            )
            return False
        return True

    def stop(self) -> None:
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
                self.process.waitForFinished(1000)

    def get_text(self) -> str:
        return QApplication.clipboard().text()

    def set_text(self, text: str) -> None:
        QApplication.clipboard().setText(text)

    def _failed(self, _error: QProcess.ProcessError) -> None:
        LOGGER.warning("Wayland clipboard watcher failed: %s", self.process.errorString())

    def _finished(self, code: int, _status: QProcess.ExitStatus) -> None:
        if code != 0:
            LOGGER.warning("Wayland clipboard watcher exited with status %d", code)
