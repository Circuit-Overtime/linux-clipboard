"""Qt application startup."""

from __future__ import annotations

import logging
import sys

from linux_dot_panel.config import Settings
from linux_dot_panel.emoji.importer import ensure_emoji_dataset
from linux_dot_panel.logging_setup import configure_logging
from linux_dot_panel.storage.database import open_database
from linux_dot_panel.storage.repositories.clipboard_repository import ClipboardRepository

LOGGER = logging.getLogger(__name__)


def run_demo() -> int:
    from PySide6.QtWidgets import QApplication

    from linux_dot_panel.ui.popup import PopupPanel

    configure_logging()
    try:
        settings = Settings.load()
    except (OSError, TypeError, ValueError) as error:
        LOGGER.warning("Could not load settings: %s", error)
        settings = Settings()

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Linux Dot Panel")
    database = open_database()
    try:
        panel = PopupPanel(settings, ensure_emoji_dataset(database), ClipboardRepository(database))
        panel.panel_hidden.connect(app.quit)
        panel.show_panel()
        return app.exec()
    finally:
        database.close()
