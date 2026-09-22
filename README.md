# Linux Dot Panel

A small Linux emoji and clipboard panel for GNOME and KDE Plasma. The panel uses a macOS-inspired visual style and follows the keyboard-first flow of the Windows emoji and clipboard panel.

The project is being built in the order described in [the implementation plan](linux-emoji-clipboard-panel-plan.md). The popup, single-instance daemon, offline Emoji, Kaomoji, and Symbols pickers, and text clipboard history are available.

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

## Start on login

Run `linux-dot-panel install` from the Python environment that runs the app. It creates an XDG autostart entry in your user config directory, so GNOME or KDE starts the daemon at the next login. The entry uses the current Python interpreter's absolute path; run `install` again if you move or recreate the environment. `linux-dot-panel uninstall` removes the entry.

For a systemd user service instead, run `linux-dot-panel install --method systemd`. This writes and enables a service under `~/.config/systemd/user` (or `$XDG_CONFIG_HOME/systemd/user`) for `graphical-session.target`; it starts at the next graphical login. Run `uninstall` before switching methods. Neither install method opens the panel automatically; your desktop shortcut still runs `linux-dot-panel toggle`.

## Build a wheel

From an environment with `pip` and `setuptools` installed, build without downloading dependencies:

```bash
python -m pip wheel --no-deps --no-build-isolation --no-index --wheel-dir dist .
python scripts/check-wheel.py dist/linux_dot_panel-*.whl
```

The check verifies that the wheel contains the local datasets, SQL migrations, PySide6 dependency metadata, and `linux-dot-panel` entry point. Install the wheel into a Python environment with `python -m pip install dist/linux_dot_panel-*.whl`; pip handles Python dependencies, while `wl-clipboard` remains a separate system package on Wayland. The wheel does not create an autostart entry until you run `linux-dot-panel install`.

## Build a Debian package

The first `.deb` targets Debian 13 and Ubuntu 26.04, which provide the required PySide6 Qt Widgets and Network packages. After building and checking the wheel, run:

```bash
python scripts/build_deb.py dist/linux_dot_panel-*.whl
dpkg-deb --info dist/linux-dot-panel_*.deb
dpkg-deb --contents dist/linux-dot-panel_*.deb
```

The package installs the app for system Python and declares dependencies on `python3-pyside6.qtwidgets`, `python3-pyside6.qtnetwork`, `python3-gi`, the AT-SPI typelib, and `wl-clipboard`. Install a specific build with `sudo apt install ./dist/linux-dot-panel_0.1.0-3_all.deb` on a compatible Debian or Ubuntu system. Increase the package revision for a changed build of the same app version, then install that new `.deb` as an upgrade. It leaves your clipboard database and user configuration untouched; use `linux-dot-panel install` separately to enable login startup. Other distributions should use the wheel until their system packages are verified.

### Publish and install from GitHub

After committing a release, push a tag such as `v0.1.0-3`. The [release workflow](.github/workflows/release-deb.yml) builds the wheel and `.deb` on GitHub and attaches the package and checksum to a GitHub Release. It does not use your local `dist` directory. The tag's version must match `pyproject.toml`, and its suffix becomes the Debian revision.

```bash
git tag v0.1.0-3
git push origin v0.1.0-3
```

Once the release workflow succeeds, install the published package without an APT repository:

```bash
curl -fL -o /var/tmp/linux-dot-panel_0.1.0-3_all.deb https://github.com/Circuit-Overtime/linux-clipboard/releases/download/v0.1.0-3/linux-dot-panel_0.1.0-3_all.deb
curl -fL -o /var/tmp/SHA256SUMS https://github.com/Circuit-Overtime/linux-clipboard/releases/download/v0.1.0-3/SHA256SUMS
(cd /var/tmp && sha256sum -c SHA256SUMS)
chmod 644 /var/tmp/linux-dot-panel_0.1.0-3_all.deb
sudo apt install /var/tmp/linux-dot-panel_0.1.0-3_all.deb
```

APT downloads dependencies from the configured Ubuntu or Debian repositories. GitHub provides this application's `.deb`; updates are installed by downloading a newer release. Using `/var/tmp` also lets APT's `_apt` user read the file, avoiding the permission notice caused by private home directory permissions.

Clipboard history is stored locally. The application does not use a remote service for its core features.

Clipboard monitoring is event driven. On Wayland, a source checkout can run `sh scripts/install-system-deps.sh` to install the required `wl-clipboard` system package with apt, dnf, or pacman; the daemon then runs `wl-paste --watch`. For a wheel install, install `wl-clipboard` with the system package manager separately because pip cannot install OS packages. If `wl-paste` is unavailable, Qt clipboard notifications provide a partial fallback. On X11, Qt clipboard notifications are used directly. The watcher stores text up to 1 MiB, merges duplicates, respects the configured history limit, and skips content marked sensitive by the source.

The Clipboard tab shows paged previews. Search filters saved text; select a card and press **Copy** or Enter, or double-click it, to copy the full text and close the panel. **Pin**, **Delete**, and **Clear unpinned** manage history. Clearing needs a second click and leaves pinned items in place.

The daemon creates its SQLite database at `$XDG_DATA_HOME/linux-dot-panel/panel.db` (or `~/.local/share/linux-dot-panel/panel.db`). Its schema is versioned; an unsupported or incomplete existing database causes an error instead of being replaced. UI preferences currently remain in the XDG config file.

The Emoji tab searches names and English keywords, browses categories, and keeps a recent list. Click an emoji or select it with Enter to insert it at the previous text cursor when supported, or copy it for manual pasting. The panel stays open for repeated selections. The bundled data is generated from [Unicode Emoji 18.0](https://www.unicode.org/Public/18.0.0/emoji/emoji-test.txt) and [Unicode CLDR English annotations](https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-annotations-full/annotations/en/annotations.json). The data is distributed under the [Unicode License v3](src/linux_dot_panel/resources/UNICODE-LICENSE.txt); emoji search works offline.

The Kaomoji and Symbols tabs also work offline. Browse their categories or search by name, keyword, or character. Click a result or select it with Enter to insert it at the previous text cursor when supported. Otherwise, the selection is copied and the panel shows a paste hint. The panel stays open for repeated selections.

With the default `system` theme, the panel follows light and dark desktop palette changes while it is running. Set `theme` to `light` or `dark` in the XDG config file to keep a fixed appearance.
