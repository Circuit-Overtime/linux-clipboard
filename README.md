# Linux Dot Panel

A small Linux emoji and clipboard panel for GNOME and KDE Plasma. The panel uses a macOS-inspired visual style and follows the keyboard-first flow of the Windows emoji and clipboard panel.

The project is being built in the order described in [the implementation plan](linux-emoji-clipboard-panel-plan.md). The current runnable slice is the popup prototype; clipboard monitoring and the daemon are upcoming steps.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
linux-dot-panel --help
linux-dot-panel demo
```

The eventual desktop shortcut will run `linux-dot-panel toggle`. GNOME or KDE will own that shortcut; the app will not install a global keyboard hook.

Clipboard history will be stored locally. The application will not use a remote service for its core features.

