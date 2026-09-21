"""Insert text through the desktop accessibility interface when available."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


class TextInserter:
    def __init__(self) -> None:
        self.target = None
        try:
            import gi

            gi.require_version("Atspi", "2.0")
            from gi.repository import Atspi
        except (ImportError, ValueError):
            self.atspi = None
        else:
            self.atspi = Atspi

    def capture_focused_field(self) -> None:
        """Remember the editable field before the panel takes keyboard focus."""
        self.target = None
        if self.atspi is None:
            return
        try:
            remaining = [2000]
            for index in range(self.atspi.get_desktop_count()):
                self.target = self._find_focused_editable(self.atspi.get_desktop(index), remaining)
                if self.target is not None:
                    return
        except Exception:
            LOGGER.debug("Could not inspect the focused text field", exc_info=True)

    def _find_focused_editable(self, node: object, remaining: list[int]) -> object | None:
        if remaining[0] <= 0:
            return None
        remaining[0] -= 1
        try:
            if (
                node.get_state_set().contains(self.atspi.StateType.FOCUSED)
                and node.is_editable_text()
                and node.get_role() != self.atspi.Role.PASSWORD_TEXT
            ):
                return node
            count = min(node.get_child_count(), 200)
            for index in range(count):
                child = node.get_child_at_index(index)
                if child is not None:
                    found = self._find_focused_editable(child, remaining)
                    if found is not None:
                        return found
        except Exception:
            LOGGER.debug("Could not inspect an accessible widget", exc_info=True)
        return None

    def insert(self, value: str) -> bool:
        if self.target is None:
            return False
        try:
            text = self.target.get_text_iface()
            editable = self.target.get_editable_text_iface()
            if text is None or editable is None:
                return False
            offset = text.get_caret_offset()
            if offset < 0:
                return False
            if not editable.insert_text(offset, value, len(value.encode("utf-8"))):
                return False
            text.set_caret_offset(offset + len(value))
            return True
        except Exception:
            LOGGER.debug("Could not insert into the focused text field", exc_info=True)
            return False
