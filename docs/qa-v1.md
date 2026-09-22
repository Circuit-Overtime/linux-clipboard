# V1 Release QA Checklist

This document tracks the quality assurance checks for the V1 release, covering both X11 and Wayland backends, shortcuts, multi-monitor behavior, and settings.

> **Note on Environment:** Development and automated testing occurred on Windows. Live session tests (GNOME/KDE, Wayland/X11, shortcuts, and systemd) are marked as **Untested in this environment** and require verification on a native Linux installation.

## Core Features
- [ ] **Emoji Insertion:** Select an emoji, kaomoji, or symbol. It should insert into the focused window or copy to the clipboard if insertion is unavailable.
- [ ] **Close After Selection:** When `close_after_selection` is true in `config.json`, the panel should hide immediately after selecting an item.
- [ ] **Remember Last Tab:** When `remember_last_tab` is true, closing and reopening the panel should restore the last active tab. When false, it should default to Emoji (or the previously saved tab).

## Clipboard History (Wayland & X11)
- [ ] **Wayland Backend:** Verify that copying text in a Wayland session populates the Clipboard tab. *(Untested in this environment)*
- [ ] **X11 Backend:** Verify that copying text in an X11 session (or Xwayland app) populates the Clipboard tab. *(Untested in this environment)*
- [ ] **Privacy/Sensitive Data:** Verify that copying from a password manager (like KDE Wallet/KeePassXC) does NOT store the text in history (checks for `application/x-kde-passwordManagerHint`). *(Untested in this environment)*
- [ ] **Clipboard Toggle Setting:** Setting `clipboard_enabled` to false in `config.json` and restarting the daemon should stop new items from being collected.
- [ ] **Pin and Delete:** Verify pinning an item prevents it from being cleared by "Clear unpinned". Verify deleting removes it immediately.

## Shortcuts and Positioning
- [ ] **Super + . (Toggle):** Opens the panel, focuses search. Pressing again hides it. *(Untested in this environment)*
- [ ] **Super + V (Toggle Clipboard):** Opens the panel directly to the Clipboard tab, or switches to it if already open. Pressing again hides it. *(Untested in this environment)*
- [ ] **Positioning:** The panel should open near the mouse cursor and remain fully visible within the screen bounds.
- [ ] **Multi-monitor:** The panel should correctly identify the screen the cursor is currently on and position itself there. *(Untested in this environment)*

## Startup and Packaging
- [ ] **XDG Autostart:** `win-dot-panel install` successfully adds the `.desktop` file to `~/.config/autostart`. *(Untested in this environment)*
- [ ] **Systemd Autostart:** `win-dot-panel install --method systemd` successfully registers and starts the user service. *(Untested in this environment)*
- [ ] **Wheel Installation:** `pip install win_dot_panel-0.2.0-py3-none-any.whl` installs correctly with entry points and all data files.

## Themes
- [ ] **Light/Dark Mode:** Changing the system theme or manually setting `theme` to "light" or "dark" in `config.json` correctly updates the UI colors in real-time.
- [ ] **Empty States:** The new 3-label empty states for Emoji and Clipboard tabs render correctly with both light and dark themes.
