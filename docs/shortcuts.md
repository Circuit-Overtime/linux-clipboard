# Keyboard shortcut setup

Linux Dot Panel uses the desktop's shortcut settings. The shortcut runs one small command, `linux-dot-panel toggle`, which contacts the existing daemon or starts it when needed. The app does not register a global keyboard hook.

## Choose the command

For an installed executable available to the desktop session, use:

```text
linux-dot-panel toggle
```

For a development install inside this repository's `.venv`, find the executable's absolute path while the environment is active:

```bash
readlink -f "$(command -v linux-dot-panel)"
```

Add ` toggle` to the printed path. For example, enter `/home/you/linux-clipboard/.venv/bin/linux-dot-panel toggle` in the shortcut editor. Use the actual printed path; desktop shortcut launchers may not have the PATH from your activated terminal.

## GNOME

1. Open **Settings → Keyboard → View and Customize Shortcuts → Custom Shortcuts**.
2. Add a shortcut named **Emoji & Clipboard Panel**.
3. Enter the command chosen above.
4. Record **Super + .** and save. If the desktop reports a conflict, choose another combination such as **Super + ;**.

GNOME's [custom shortcut instructions](https://help.gnome.org/gnome-help/keyboard-shortcuts-set.html) describe the name, command, and key recording fields.

## KDE Plasma

1. Open **System Settings → Shortcuts** (under **Keyboard** on some versions).
2. In Plasma 6, choose **Add New → Command or Script**. In older Plasma releases, look for **Custom Shortcuts**.
3. Enter the command chosen above and assign **Meta + .**. KDE calls the Windows/Super key **Meta**.
4. Apply the change. If the combination is already assigned, choose **Meta + ;** or another free combination.

See the [KDE Shortcuts module](https://docs.kde.org/stable_kf6/en/plasma-desktop/kcontrol/keys/) and the [Plasma 6 command shortcut example](https://discuss.kde.org/t/personalized-keyboard-shortcuts-gone-after-update-to-plasma-6-how-to-put-them-back/13126/4).

## Check the shortcut

1. Run `linux-dot-panel quit` to stop any existing daemon.
2. Press the shortcut once. The panel should appear with search focused; this also tests cold start.
3. Press the shortcut again. The same panel should hide. Press it once more to reopen, then press **Esc** to close.
4. In a terminal, run `linux-dot-panel status`; it should print `running`.
5. Run `linux-dot-panel quit` when done.

The shortcut command should use the same executable as the terminal commands. If the terminal command works but the shortcut does not, use its absolute path as shown above.
