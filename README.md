# Linux Dot Panel

A small Linux emoji and clipboard panel for GNOME and KDE Plasma. The panel uses a macOS-inspired visual style and follows the keyboard-first flow of the Windows emoji and clipboard panel.

The project is being built in the order described in [the implementation plan](linux-emoji-clipboard-panel-plan.md). The popup, single-instance daemon, offline emoji picker, and text clipboard history are available. Kaomoji and Symbols are upcoming steps.

Selecting an emoji keeps the panel open. When PyGObject and the AT-SPI typelib are available, the panel inserts the emoji into the text field that was focused when it opened. Apps that do not expose an editable accessibility field fall back to copying the emoji; the panel shows a paste hint. On Ubuntu, `python3-gi` and `gir1.2-atspi-2.0` provide the system components. The Python environment running the daemon must also be able to import `gi` (for example, a venv created with `--system-site-packages`, or the optional `insert` dependency). Restart the daemon after changing its Python environment.

## Development

```bash
sh scripts/install-system-deps.sh  # Wayland system dependency
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

Clipboard history is stored locally. The application does not use a remote service for its core features.

Clipboard monitoring is event driven. On Wayland, a source checkout can run `sh scripts/install-system-deps.sh` to install the required `wl-clipboard` system package with apt, dnf, or pacman; the daemon then runs `wl-paste --watch`. For a wheel install, install `wl-clipboard` with the system package manager separately because pip cannot install OS packages. If `wl-paste` is unavailable, Qt clipboard notifications provide a partial fallback. On X11, Qt clipboard notifications are used directly. The watcher stores text up to 1 MiB, merges duplicates, respects the configured history limit, and skips content marked sensitive by the source.

The Clipboard tab shows paged previews. Search filters saved text; select a card and press **Copy** or Enter, or double-click it, to copy the full text and close the panel. **Pin**, **Delete**, and **Clear unpinned** manage history. Clearing needs a second click and leaves pinned items in place.

The daemon creates its SQLite database at `$XDG_DATA_HOME/linux-dot-panel/panel.db` (or `~/.local/share/linux-dot-panel/panel.db`). Its schema is versioned; an unsupported or incomplete existing database causes an error instead of being replaced. UI preferences currently remain in the XDG config file.

The Emoji tab searches names and English keywords, browses categories, and keeps a recent list. Click an emoji or select it with Enter to insert it at the previous text cursor when supported, or copy it for manual pasting. The panel stays open for repeated selections. The bundled data is generated from [Unicode Emoji 18.0](https://www.unicode.org/Public/18.0.0/emoji/emoji-test.txt) and [Unicode CLDR English annotations](https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-annotations-full/annotations/en/annotations.json). The data is distributed under the [Unicode License v3](src/linux_dot_panel/resources/UNICODE-LICENSE.txt); emoji search works offline.
