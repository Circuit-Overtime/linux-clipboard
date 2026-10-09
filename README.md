# ScreenBridge

ScreenBridge makes Ubuntu system audio available as a virtual input without hiding or replacing the real microphone. It works with PipeWire's PulseAudio compatibility server and with PulseAudio itself.

## What it creates

- **Screen Share Audio** — computer audio only. Your real microphone remains a separate device.
- **Screen Share Audio + Microphone** — optional combined input for conferencing apps that accept only one input device.

Linux browsers do not currently provide a universal Windows-style “share system audio” track for every screen or window. ScreenBridge handles the Linux audio routing, but the receiving application still decides how many audio inputs it can send:

- In OBS, recording tools, and apps supporting multiple inputs, use **Screen Share Audio** and the real microphone as separate sources.
- In Google Meet, Discord, and similar one-input apps, enable the combined input and select **Screen Share Audio + Microphone** as the microphone.
- Chromium can often share audio directly when sharing a browser tab. That is usually preferable for tab-only sharing.

## Requirements

- Ubuntu 22.04 or newer
- PipeWire or PulseAudio
- `pactl` (`sudo apt install pulseaudio-utils`)
- GTK 4 Python bindings (`sudo apt install python3-gi gir1.2-gtk-4.0`)

## Run from the project

```bash
chmod +x run-screenbridge install.sh screenbridge-launcher
./run-screenbridge
```

Choose where audio should continue playing, choose the microphone, optionally enable the combined input, and press **Start sharing audio**. Then select the new input in the screen-sharing application.

Stop the session from ScreenBridge when finished. It restores the prior default output and removes the temporary devices.

## Install for the current user

```bash
chmod +x install.sh screenbridge-launcher
./install.sh
```

ScreenBridge then appears in the Ubuntu application menu. The install does not require `sudo`.

## Command line

```bash
./run-screenbridge list
./run-screenbridge start --output SINK_NAME --microphone SOURCE_NAME --mix-microphone
./run-screenbridge status
./run-screenbridge stop
```

Session metadata is kept in `~/.local/state/screenbridge/session.json`, allowing the next launch to clean up routes after an application crash.

