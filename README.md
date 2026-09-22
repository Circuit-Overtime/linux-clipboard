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

The Debian package is available for Debian 13 and Ubuntu 26.04. Copy these commands into a terminal to install the [current release](https://github.com/Circuit-Overtime/linux-clipboard/releases/tag/v0.1.0-3):

```bash
curl -fL -o /var/tmp/win-dot-panel_0.1.0-3_all.deb https://github.com/Circuit-Overtime/linux-clipboard/releases/download/v0.1.0-3/win-dot-panel_0.1.0-3_all.deb
chmod 644 /var/tmp/win-dot-panel_0.1.0-3_all.deb
sudo apt install /var/tmp/win-dot-panel_0.1.0-3_all.deb
```

You can also install the Python wheel directly using pip (requires pipx or a virtual environment on modern distros):

```bash
pip install https://github.com/Circuit-Overtime/linux-clipboard/releases/download/v0.1.0-3/win_dot_panel-0.1.0-py3-none-any.whl
```

The release page also provides a checksum file if you want to verify the download. For other Linux distributions, see the [developer guide](docs/development.md) for the Python package.

## Open the panel

Run `win-dot-panel toggle` to show or hide it. To start the app automatically when you sign in, run `win-dot-panel install` once. By default, this creates an XDG autostart entry. You can also install it as a systemd user service instead by running `win-dot-panel install --method systemd`.

To open it with **Super + .**, add `win-dot-panel toggle` as a custom keyboard shortcut in your desktop settings. You can also assign **Super + V** to `win-dot-panel toggle-clipboard` to open the Clipboard tab directly. Follow the [GNOME or KDE shortcut guide](docs/shortcuts.md) if you need help. Run `win-dot-panel install` once to record copies while the panel is closed; the shortcut also starts the app if it is not already running.

The panel opens near your pointer. Drag the small handle at the top to move it. Use the tabs to browse or search. Click an emoji or symbol to insert it. On the Clipboard tab, select an entry and choose **Copy** to use it again. Press **Esc** to close the panel.

## Configuration

Settings are saved in `~/.config/win-dot-panel/config.json`. You can modify it manually (restart the daemon to apply changes):

```json
{
  "theme": "system",
  "history_limit": 500,
  "clipboard_enabled": true,
  "close_after_selection": false,
  "remember_last_tab": true
}
```

## Update

After a new stable release is published, run:

```bash
/usr/bin/win-dot-panel update
```

The updater downloads the package from GitHub, checks its SHA-256 checksum, asks APT to install it, and restarts the app on your next shortcut press. To try the newest development build instead, run `/usr/bin/win-dot-panel update --channel main`.

The current `0.1.0-3` package does not yet have the updater. For this first update, or whenever you prefer to install a GitHub release yourself, use these commands. They select the newest published release, including development builds, and require the GitHub CLI (`gh`):

```bash
tag=$(gh release list -R Circuit-Overtime/linux-clipboard \
  --limit 1 --json tagName --jq '.[0].tagName')
gh release download "$tag" -R Circuit-Overtime/linux-clipboard \
  -p 'win-dot-panel_*_all.deb' -O /var/tmp/win-dot-panel.deb --clobber
chmod 644 /var/tmp/win-dot-panel.deb
sudo apt install --allow-downgrades /var/tmp/win-dot-panel.deb
/usr/bin/win-dot-panel quit
```

The last command stops any older background process. If it says the daemon is not running, the install is still complete.

APT cannot discover new packages from a GitHub Releases page by itself. Other apps make `sudo apt update && sudo apt upgrade` work by publishing a signed APT repository. We are preparing one at [packages.elixpo.com](https://packages.elixpo.com/). **Check that the site's APT status says it is live before using these commands.** Then add it once with:

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

Then update stable releases with `sudo apt update && sudo apt upgrade`. See the [APT repository setup guide](docs/apt-repository.md) for the maintainer steps needed before this works.

## Remove

To stop starting at login, run `win-dot-panel uninstall`. To remove the app, run `sudo apt remove win-dot-panel`. Removing it does not erase your saved clipboard history.

Developing or packaging the app? See the [developer guide](docs/development.md) and [implementation plan](docs/implementation-plan.md).

## License

The app's code is available under the [MIT License](LICENSE). The bundled emoji data retains the [Unicode License v3](src/win_dot_panel/resources/UNICODE-LICENSE.txt).
