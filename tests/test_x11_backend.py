from __future__ import annotations

from PySide6.QtCore import QMimeData
from PySide6.QtWidgets import QApplication

from win_dot_panel.clipboard.backends.x11 import X11ClipboardBackend


def _ensure_app():
    return QApplication.instance() or QApplication([])


def test_start_connects_and_returns_true(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    _ensure_app()
    backend = X11ClipboardBackend()
    assert backend.start() is True


def test_stop_disconnects_safely(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    _ensure_app()
    backend = X11ClipboardBackend()
    backend.start()
    backend.stop()
    # Calling stop again should not raise.
    backend.stop()


def test_changed_emits_text(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    _ensure_app()
    backend = X11ClipboardBackend()
    results: list[tuple[str, bool]] = []
    backend.clipboard_changed.connect(lambda text, sensitive: results.append((text, sensitive)))
    backend.start()
    backend.clipboard.setText("hello x11")
    assert ("hello x11", False) in results


def test_changed_detects_kde_sensitive(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    _ensure_app()
    backend = X11ClipboardBackend()
    results: list[tuple[str, bool]] = []
    backend.clipboard_changed.connect(lambda text, sensitive: results.append((text, sensitive)))
    backend.start()
    mime = QMimeData()
    mime.setText("secret")
    mime.setData("application/x-kde-passwordManagerHint", b"1")
    backend.clipboard.setMimeData(mime)
    assert ("secret", True) in results


def test_changed_ignores_non_text(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    _ensure_app()
    backend = X11ClipboardBackend()
    results: list[tuple[str, bool]] = []
    backend.clipboard_changed.connect(lambda text, sensitive: results.append((text, sensitive)))
    backend.start()
    mime = QMimeData()
    mime.setData("application/octet-stream", b"\x00\x01\x02")
    backend.clipboard.setMimeData(mime)
    # Non-text data should not emit clipboard_changed.
    assert all(text != "" for text, _ in results)


def test_get_set_text(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    _ensure_app()
    backend = X11ClipboardBackend()
    backend.set_text("roundtrip")
    assert backend.get_text() == "roundtrip"
