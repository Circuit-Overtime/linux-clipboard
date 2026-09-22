"""Small, local settings store using XDG paths."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

TABS = ("Emoji", "Clipboard", "Kaomoji", "Symbols", "Open Source")


def config_path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "win-dot-panel" / "config.json"


@dataclass(slots=True)
class Settings:
    last_tab: str = "Emoji"
    theme: str = "system"
    history_limit: int = 500

    @classmethod
    def load(cls, path: Path | None = None) -> Settings:
        target = path or config_path()
        if not target.exists():
            return cls()
        data = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise TypeError("Configuration must be a JSON object")
        settings = cls(
            last_tab=data.get("last_tab", "Emoji"),
            theme=data.get("theme", "system"),
            history_limit=data.get("history_limit", 500),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if self.last_tab not in TABS:
            raise ValueError(f"Unknown tab: {self.last_tab}")
        if self.theme not in ("system", "light", "dark"):
            raise ValueError(f"Unknown theme: {self.theme}")
        if type(self.history_limit) is not int or self.history_limit < 1:
            raise ValueError("history_limit must be a positive integer")

    def save(self, path: Path | None = None) -> None:
        self.validate()
        target = path or config_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")
        temporary.replace(target)
