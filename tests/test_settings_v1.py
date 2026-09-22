from __future__ import annotations

import json

import pytest

from win_dot_panel.config import Settings


def test_default_settings():
    settings = Settings()
    assert settings.clipboard_enabled is True
    assert settings.close_after_selection is False
    assert settings.remember_last_tab is True
    assert settings.last_tab == "Emoji"
    assert settings.theme == "system"


def test_load_legacy_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"last_tab": "Kaomoji"}))

    settings = Settings.load(config_file)
    assert settings.last_tab == "Kaomoji"
    # New fields should have defaults
    assert settings.clipboard_enabled is True
    assert settings.close_after_selection is False
    assert settings.remember_last_tab is True


def test_save_and_load_roundtrip(tmp_path):
    config_file = tmp_path / "config.json"

    settings = Settings(
        clipboard_enabled=False,
        close_after_selection=True,
        remember_last_tab=False,
        theme="dark",
    )
    settings.save(config_file)

    loaded = Settings.load(config_file)
    assert loaded.clipboard_enabled is False
    assert loaded.close_after_selection is True
    assert loaded.remember_last_tab is False
    assert loaded.theme == "dark"


def test_validation_rejects_invalid_types():
    with pytest.raises(ValueError, match="clipboard_enabled must be a boolean"):
        settings = Settings(clipboard_enabled="yes")  # type: ignore
        settings.validate()

    with pytest.raises(ValueError, match="close_after_selection must be a boolean"):
        settings = Settings(close_after_selection=1)  # type: ignore
        settings.validate()

    with pytest.raises(ValueError, match="remember_last_tab must be a boolean"):
        settings = Settings(remember_last_tab=None)  # type: ignore
        settings.validate()
