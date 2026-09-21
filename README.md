# Linux Dot Panel

A small Linux emoji and clipboard panel for GNOME and KDE Plasma. The panel uses a macOS-inspired visual style and follows the keyboard-first flow of the Windows emoji and clipboard panel.

The project is being built in the order described in [the implementation plan](linux-emoji-clipboard-panel-plan.md). The popup, single-instance daemon, and offline emoji picker are available; clipboard monitoring and the other picker pages are upcoming steps.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
linux-dot-panel --help
linux-dot-panel demo
linux-dot-panel toggle
linux-dot-panel status
linux-dot-panel quit
```

The desktop shortcut runs `linux-dot-panel toggle`. GNOME or KDE owns that shortcut; the app does not install a global keyboard hook. See [keyboard shortcut setup](docs/shortcuts.md) for the GNOME and Plasma steps, including the absolute command path needed for a virtual environment. `toggle` starts the daemon when needed, while `linux-dot-panel daemon` can run it in a foreground terminal for troubleshooting.

Clipboard history will be stored locally. The application will not use a remote service for its core features.

The daemon creates its SQLite database at `$XDG_DATA_HOME/linux-dot-panel/panel.db` (or `~/.local/share/linux-dot-panel/panel.db`). Its schema is versioned; an unsupported or incomplete existing database causes an error instead of being replaced. UI preferences currently remain in the XDG config file.

The Emoji tab searches names and English keywords, browses categories, and keeps a recent list. Click an emoji or select it with Enter to copy it and close the panel. The bundled data is generated from [Unicode Emoji 18.0](https://www.unicode.org/Public/18.0.0/emoji/emoji-test.txt) and [Unicode CLDR English annotations](https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-annotations-full/annotations/en/annotations.json). The data is distributed under the [Unicode License v3](src/linux_dot_panel/resources/UNICODE-LICENSE.txt); emoji search works offline.
