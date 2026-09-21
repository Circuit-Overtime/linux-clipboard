from __future__ import annotations

import json

import pytest

from linux_dot_panel.config import Settings


def test_settings_round_trip(tmp_path):
    path = tmp_path / "config" / "config.json"
    settings = Settings(last_tab="Symbols", theme="dark", history_limit=50)

    settings.save(path)

    assert Settings.load(path) == settings


@pytest.mark.parametrize("value", [0, -1, True, "500"])
def test_invalid_history_limit_is_rejected(tmp_path, value):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"history_limit": value}), encoding="utf-8")

    with pytest.raises(ValueError, match="history_limit"):
        Settings.load(path)
