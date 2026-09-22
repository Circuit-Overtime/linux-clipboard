# Win Dot Panel

A quick emoji and clipboard panel for Linux. It has a clean, macOS-inspired look and the familiar Windows emoji picker behavior: choose an emoji, keep the panel open, and choose another.

Built for GNOME and KDE Plasma on Wayland or X11.

## What you can do

- Find emoji, kaomoji, and symbols, even without an internet connection.
- Reuse copied text from your clipboard history. Search, pin, or delete entries.
- Insert a character into the field you were using when the app can access it. Otherwise, the app copies it and shows you how to paste it.
- Switch between light and dark appearances with your desktop.

Your clipboard history stays on your computer.

## Install

The Debian package is available for Debian 13 and Ubuntu 26.04. Copy these commands into a terminal to install the [current release](https://github.com/Circuit-Overtime/linux-clipboard/releases/tag/v0.1.0-3):

```bash
curl -fL -o /var/tmp/win-dot-panel_0.1.0-3_all.deb https://github.com/Circuit-Overtime/linux-clipboard/releases/download/v0.1.0-3/win-dot-panel_0.1.0-3_all.deb
chmod 644 /var/tmp/win-dot-panel_0.1.0-3_all.deb
sudo apt install /var/tmp/win-dot-panel_0.1.0-3_all.deb
```

The release page also provides a checksum file if you want to verify the download. For other Linux distributions, see the [developer guide](docs/development.md) for the Python package.

## Open the panel

Run `win-dot-panel toggle` to show or hide it. To start the app automatically when you sign in, run `win-dot-panel install` once.

To open it with **Super + .**, add `win-dot-panel toggle` as a custom keyboard shortcut in your desktop settings. You can also assign **Super + V** to `win-dot-panel toggle-clipboard` to open the Clipboard tab directly. Follow the [GNOME or KDE shortcut guide](docs/shortcuts.md) if you need help.

The panel opens near your pointer. Drag the small handle at the top to move it. Use the tabs to browse or search. Click an emoji or symbol to insert it. On the Clipboard tab, select an entry and choose **Copy** to use it again. Press **Esc** to close the panel.

## Updates and removal

Download and install a newer package from [Releases](https://github.com/Circuit-Overtime/linux-clipboard/releases) when one is available. To stop starting at login, run `win-dot-panel uninstall`. To remove the app, run `sudo apt remove win-dot-panel`. Removing it does not erase your saved clipboard history.

Developing or packaging the app? See the [developer guide](docs/development.md) and [implementation plan](docs/implementation-plan.md).

## License

The app's code is available under the [MIT License](LICENSE). The bundled emoji data retains the [Unicode License v3](src/win_dot_panel/resources/UNICODE-LICENSE.txt).
