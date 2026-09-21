"""One Qt process owns the popup and its local IPC socket."""

from __future__ import annotations

import fcntl
import logging
import os
import sqlite3
import sys
from typing import IO

from linux_dot_panel.config import Settings
from linux_dot_panel.ipc.protocol import COMMANDS, lock_path
from linux_dot_panel.logging_setup import configure_logging
from linux_dot_panel.storage.database import open_database
from linux_dot_panel.storage.migrations import UnsupportedSchemaError

LOGGER = logging.getLogger(__name__)


def _acquire_lock() -> IO[str] | None:
    path = lock_path()
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    handle = os.fdopen(descriptor, "r+")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        return None
    return handle


def run_daemon() -> int:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from linux_dot_panel.ipc.server import IpcServer
    from linux_dot_panel.ui.popup import PopupPanel

    configure_logging()
    lock = _acquire_lock()
    if lock is None:
        LOGGER.info("Daemon is already running")
        return 0

    try:
        try:
            database = open_database()
        except (OSError, sqlite3.Error, UnsupportedSchemaError) as error:
            LOGGER.error("Could not open database: %s", error)
            print(f"Could not open database: {error}", file=sys.stderr)
            return 1

        try:
            try:
                settings = Settings.load()
            except (OSError, TypeError, ValueError) as error:
                LOGGER.warning("Could not load settings: %s", error)
                settings = Settings()

            app = QApplication.instance() or QApplication(sys.argv)
            app.setApplicationName("Linux Dot Panel")
            app.setQuitOnLastWindowClosed(False)
            panel = PopupPanel(settings)

            def handle(command: str) -> dict[str, object]:
                if command not in COMMANDS:
                    return {"ok": False, "error": f"Unknown command: {command}"}
                if command == "toggle":
                    panel.hide_panel() if panel.isVisible() else panel.show_panel()
                elif command == "show":
                    panel.show_panel()
                elif command == "hide":
                    panel.hide_panel()
                elif command == "quit":
                    QTimer.singleShot(50, app.quit)
                return {"ok": True, "visible": panel.isVisible()}

            server = IpcServer(handle)
            server.start()
            app.aboutToQuit.connect(server.stop)
            LOGGER.info("Daemon started")
            return app.exec()
        finally:
            database.close()
    finally:
        lock.close()
