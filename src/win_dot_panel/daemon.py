"""One Qt process owns the popup and its local IPC socket."""

from __future__ import annotations

import base64
import binascii
import fcntl
import logging
import os
import sqlite3
import sys
from typing import IO

from win_dot_panel.clipboard.capture import MAX_TEXT_BYTES, ClipboardCapture
from win_dot_panel.config import TABS, Settings
from win_dot_panel.emoji.importer import ensure_emoji_dataset
from win_dot_panel.ipc.protocol import COMMANDS, lock_path
from win_dot_panel.logging_setup import configure_logging
from win_dot_panel.storage.database import open_database
from win_dot_panel.storage.migrations import UnsupportedSchemaError
from win_dot_panel.storage.repositories.clipboard_repository import ClipboardRepository
from win_dot_panel.ui.platform import configure_window_platform

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
    configure_window_platform()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from win_dot_panel.clipboard.backends.wayland import WaylandClipboardBackend
    from win_dot_panel.clipboard.backends.x11 import X11ClipboardBackend
    from win_dot_panel.ipc.server import IpcServer
    from win_dot_panel.ui.popup import PopupPanel

    configure_logging()
    lock = _acquire_lock()
    if lock is None:
        LOGGER.info("Daemon is already running")
        return 0

    try:
        database = None
        try:
            database = open_database()
            emoji_repository = ensure_emoji_dataset(database)
        except (OSError, sqlite3.Error, UnsupportedSchemaError, ValueError) as error:
            if database is not None:
                database.close()
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
            app.setApplicationName("Win Dot Panel")
            app.setQuitOnLastWindowClosed(False)
            clipboard_repository = ClipboardRepository(database)
            panel = PopupPanel(settings, emoji_repository, clipboard_repository)
            capture = ClipboardCapture(clipboard_repository, history_limit=settings.history_limit)

            def handle(command: str) -> dict[str, object]:
                if command not in COMMANDS:
                    return {"ok": False, "error": f"Unknown command: {command}"}
                if command == "toggle":
                    panel.hide_panel() if panel.isVisible() else panel.show_panel()
                elif command == "toggle-clipboard":
                    if panel.isVisible() and panel.pages.currentIndex() == TABS.index("Clipboard"):
                        panel.hide_panel()
                    else:
                        panel.select_tab(TABS.index("Clipboard"))
                        panel.show_panel()
                elif command == "show":
                    panel.show_panel()
                elif command == "hide":
                    panel.hide_panel()
                elif command == "quit":
                    QTimer.singleShot(50, app.quit)
                return {
                    "ok": True,
                    "visible": panel.isVisible(),
                    "tab": TABS[panel.pages.currentIndex()],
                }

            def handle_clipboard_event(request: dict[str, object]) -> dict[str, object]:
                encoded = request.get("data")
                if not isinstance(encoded, str):
                    raise TypeError("Missing clipboard data")
                try:
                    data = base64.b64decode(encoded, validate=True)
                    if len(data) > MAX_TEXT_BYTES:
                        raise ValueError("Clipboard data too large")
                    text = data.decode("utf-8")
                except (binascii.Error, UnicodeDecodeError, ValueError) as error:
                    raise ValueError("Invalid clipboard data") from error
                return {"ok": True, "stored": capture.capture(text)}

            server = IpcServer(handle, handle_clipboard_event)
            server.start()
            app.aboutToQuit.connect(server.stop)
            if os.environ.get("XDG_SESSION_TYPE") == "wayland" or app.platformName() == "wayland":
                wayland_backend = WaylandClipboardBackend()
                if wayland_backend.start():
                    backend = wayland_backend
                else:
                    backend = X11ClipboardBackend()
                    backend.clipboard_changed.connect(
                        lambda text, sensitive: capture.capture(text, sensitive=sensitive)
                    )
                    backend.start()
            else:
                backend = X11ClipboardBackend()
                backend.clipboard_changed.connect(
                    lambda text, sensitive: capture.capture(text, sensitive=sensitive)
                )
                backend.start()
            app.aboutToQuit.connect(backend.stop)
            LOGGER.info("Daemon started")
            return app.exec()
        finally:
            database.close()
    finally:
        lock.close()
