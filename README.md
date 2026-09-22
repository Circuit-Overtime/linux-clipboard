# Win Dot Panel

A quick emoji and clipboard panel for Linux. It has a clean, macOS-inspired look and the familiar Windows emoji picker behavior: choose an emoji, keep the panel open, and choose another.

Built for GNOME and KDE Plasma on Wayland or X11.

## What you can do

- Find emoji, kaomoji, and symbols, even without an internet connection.
- Reuse copied text and screenshots from your clipboard history. Search, pin, or delete entries.
- Insert a character into the field you were using when the app can access it. Otherwise, the app copies it and shows you how to paste it.
- Switch between light and dark appearances with your desktop.

Your clipboard history stays on your computer.

## Install

The Debian package is available for Debian 13 and Ubuntu 26.04. Add the signed APT repository once, then install with your normal package manager:

```bash
sudo install -d -m 755 /etc/apt/keyrings
curl -fsSL -o /var/tmp/win-dot-panel-apt.asc \
  https://packages.elixpo.com/apt/keyring.asc
sudo gpg --dearmor --yes -o /etc/apt/keyrings/win-dot-panel.gpg \
  /var/tmp/win-dot-panel-apt.asc
echo 'deb [signed-by=/etc/apt/keyrings/win-dot-panel.gpg] https://packages.elixpo.com/apt/ ./' | \
  sudo tee /etc/apt/sources.list.d/win-dot-panel.list
sudo apt update
sudo apt install win-dot-panel
```

The same steps are on [packages.elixpo.com](https://packages.elixpo.com/). If you prefer a standalone package, get the latest stable `.deb` from [GitHub Releases](https://github.com/Circuit-Overtime/linux-clipboard/releases/latest). For other Linux distributions, see the [developer guide](docs/development.md).

After installation, APT prints the suggested shortcut commands and a link to the setup guide. You can also open Win Dot Panel from your app menu before setting the shortcuts.

## Open the panel

Run `win-dot-panel toggle` to show or hide it. To start the app automatically when you sign in, run `win-dot-panel install` once.

To open it with **Super + .**, add `/usr/bin/win-dot-panel toggle` as a custom keyboard shortcut in your desktop settings. Assign **Super + V** to `/usr/bin/win-dot-panel toggle-clipboard` to open the Clipboard tab directly. Follow the [GNOME or KDE shortcut guide](docs/shortcuts.md) if you need help. Run `/usr/bin/win-dot-panel install` once to record copies while the panel is closed; the shortcut also starts the app if it is not already running.

The panel opens near your pointer. Drag the small handle at the top to move it. Use the tabs to browse or search. Click an emoji or symbol to insert it. On the Clipboard tab, select an entry and choose **Copy** to use it again. Press **Esc** to close the panel.

The **Open Source** tab links to the repository, issues, and documentation.

## Update

With the APT repository configured, run:

```bash
sudo apt update
sudo apt install --only-upgrade win-dot-panel
/usr/bin/win-dot-panel quit
```

The last command closes any older background process; the next shortcut press starts the updated app. A message saying the daemon is not running is harmless. Normal system upgrades also include new stable versions. To try a development build from GitHub Releases instead, run `/usr/bin/win-dot-panel update --channel main`.

If you installed the older `0.1.0-3` package manually, these APT setup steps also switch you to repository updates when the next stable version is published. Check `apt-cache policy win-dot-panel` to see the installed and available versions.

## Remove

To stop starting at login, run `win-dot-panel uninstall`. To remove the app, run `sudo apt remove win-dot-panel`. Removing it does not erase your saved clipboard history.

Developing or packaging the app? See the [developer guide](docs/development.md) and [implementation plan](docs/implementation-plan.md).

## License

The app's code is available under the [MIT License](LICENSE). The bundled emoji data retains the [Unicode License v3](src/win_dot_panel/resources/UNICODE-LICENSE.txt).
