# Linux Dot Panel

A small Linux emoji and clipboard panel for GNOME and KDE Plasma. The panel uses a macOS-inspired visual style and follows the keyboard-first flow of the Windows emoji and clipboard panel.

The project is being built in the order described in [the implementation plan](linux-emoji-clipboard-panel-plan.md). The popup and its single-instance daemon are available; clipboard monitoring and picker data are upcoming steps.

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
