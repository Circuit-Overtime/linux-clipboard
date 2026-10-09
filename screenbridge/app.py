"""ScreenBridge command-line entry point and GTK application."""

from __future__ import annotations

import argparse
import sys

from .audio import AudioError, AudioRouter, Device


def _device_by_default(devices: list[Device], default_name: str) -> int:
    for index, device in enumerate(devices):
        if device.name == default_name:
            return index
    return 0


def run_gui() -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        from gi.repository import Gio, GLib, Gtk
    except (ImportError, ValueError) as exc:
        print("GTK 4 is required. Install it with: sudo apt install python3-gi gir1.2-gtk-4.0", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 2

    class ScreenBridgeApplication(Gtk.Application):
        def __init__(self) -> None:
            super().__init__(application_id="io.github.screenbridge.app", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
            self.router = AudioRouter()
            self.window: Gtk.ApplicationWindow | None = None
            self.outputs: list[Device] = []
            self.microphones: list[Device] = []

        def do_activate(self) -> None:
            if self.window is not None:
                self.window.present()
                return

            self.window = Gtk.ApplicationWindow(application=self)
            self.window.set_title("ScreenBridge")
            self.window.set_default_size(560, 470)

            root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
            root.set_margin_top(28)
            root.set_margin_bottom(28)
            root.set_margin_start(28)
            root.set_margin_end(28)
            self.window.set_child(root)

            title = Gtk.Label(label="Share your computer audio")
            title.add_css_class("title-1")
            title.set_xalign(0)
            root.append(title)

            intro = Gtk.Label(
                label="ScreenBridge creates a virtual audio input while keeping sound playing through your speakers or headphones."
            )
            intro.set_wrap(True)
            intro.set_xalign(0)
            root.append(intro)

            grid = Gtk.Grid(column_spacing=16, row_spacing=12)
            root.append(grid)
            output_label = Gtk.Label(label="Play through")
            output_label.set_xalign(0)
            grid.attach(output_label, 0, 0, 1, 1)
            self.output_dropdown = Gtk.DropDown()
            self.output_dropdown.set_hexpand(True)
            grid.attach(self.output_dropdown, 1, 0, 1, 1)

            mic_label = Gtk.Label(label="Microphone")
            mic_label.set_xalign(0)
            grid.attach(mic_label, 0, 1, 1, 1)
            self.mic_dropdown = Gtk.DropDown()
            self.mic_dropdown.set_hexpand(True)
            grid.attach(self.mic_dropdown, 1, 1, 1, 1)

            mix_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            mix_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            mix_title = Gtk.Label(label="Also create a combined input")
            mix_title.set_xalign(0)
            mix_detail = Gtk.Label(label="Useful for apps that allow only one microphone device")
            mix_detail.add_css_class("dim-label")
            mix_detail.set_xalign(0)
            mix_detail.set_wrap(True)
            mix_text.append(mix_title)
            mix_text.append(mix_detail)
            mix_text.set_hexpand(True)
            self.mix_switch = Gtk.Switch()
            self.mix_switch.set_valign(Gtk.Align.CENTER)
            mix_row.append(mix_text)
            mix_row.append(self.mix_switch)
            root.append(mix_row)

            self.status = Gtk.Label()
            self.status.set_xalign(0)
            self.status.set_wrap(True)
            root.append(self.status)

            self.action = Gtk.Button()
            self.action.add_css_class("suggested-action")
            self.action.add_css_class("pill")
            self.action.set_size_request(-1, 48)
            self.action.connect("clicked", self.on_action)
            root.append(self.action)

            hint = Gtk.Label(
                label="After starting, choose “Screen Share Audio” as an input in your app. Your normal microphone remains available separately."
            )
            hint.add_css_class("dim-label")
            hint.set_wrap(True)
            hint.set_xalign(0)
            root.append(hint)

            self.refresh()
            self.window.present()

        def set_error(self, message: str) -> None:
            self.status.set_markup(f'<span foreground="red">{GLib.markup_escape_text(message)}</span>')

        def refresh(self) -> None:
            try:
                self.router.ensure_available()
                state = self.router.active_state()
                info = self.router.pactl.info()
                self.outputs = self.router.outputs()
                self.microphones = self.router.microphones()
                self.output_dropdown.set_model(Gtk.StringList.new([d.description for d in self.outputs]))
                self.mic_dropdown.set_model(Gtk.StringList.new([d.description for d in self.microphones]))
                selected_output = state.output if state else info.get("Default Sink", "")
                selected_microphone = state.microphone if state else info.get("Default Source", "")
                self.output_dropdown.set_selected(_device_by_default(self.outputs, selected_output))
                self.mic_dropdown.set_selected(_device_by_default(self.microphones, selected_microphone))
                active = state is not None
                self.output_dropdown.set_sensitive(not active)
                self.mic_dropdown.set_sensitive(not active)
                self.mix_switch.set_sensitive(not active)
                self.action.set_label("Stop sharing audio" if active else "Start sharing audio")
                if active:
                    self.status.set_text("Active — system audio is available as “Screen Share Audio”.")
                    self.mix_switch.set_active(state.mixed)
                    self.action.remove_css_class("suggested-action")
                    self.action.add_css_class("destructive-action")
                else:
                    self.status.set_text("Ready")
                    self.action.remove_css_class("destructive-action")
                    self.action.add_css_class("suggested-action")
                self.action.set_sensitive(active or bool(self.outputs and self.microphones))
            except AudioError as exc:
                self.set_error(str(exc))
                self.action.set_sensitive(False)

        def on_action(self, _button: Gtk.Button) -> None:
            self.action.set_sensitive(False)
            while GLib.MainContext.default().iteration(False):
                pass
            try:
                if self.router.active_state() is not None:
                    self.router.stop()
                else:
                    output_index = self.output_dropdown.get_selected()
                    mic_index = self.mic_dropdown.get_selected()
                    if output_index >= len(self.outputs) or mic_index >= len(self.microphones):
                        raise AudioError("Choose an output and a microphone first.")
                    self.router.start(
                        self.outputs[output_index].name,
                        self.microphones[mic_index].name,
                        self.mix_switch.get_active(),
                    )
                self.refresh()
            except AudioError as exc:
                self.set_error(str(exc))
                self.action.set_sensitive(True)

    return ScreenBridgeApplication().run([])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Easy Ubuntu system-audio sharing")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list", help="list playback devices and microphones")
    start = subparsers.add_parser("start", help="start an audio sharing session")
    start.add_argument("--output", required=True, help="pactl sink name")
    start.add_argument("--microphone", required=True, help="pactl source name")
    start.add_argument("--mix-microphone", action="store_true", help="also create a combined input")
    subparsers.add_parser("stop", help="stop the active session and restore audio")
    subparsers.add_parser("status", help="show session status")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command is None:
        return run_gui()

    router = AudioRouter()
    try:
        router.ensure_available()
        if args.command == "list":
            print("Outputs:")
            for device in router.outputs():
                print(f"  {device.name}\t{device.description}")
            print("Microphones:")
            for device in router.microphones():
                print(f"  {device.name}\t{device.description}")
        elif args.command == "start":
            router.start(args.output, args.microphone, args.mix_microphone)
            print("ScreenBridge audio sharing started.")
        elif args.command == "stop":
            router.stop()
            print("ScreenBridge audio sharing stopped.")
        elif args.command == "status":
            state = router.active_state()
            print("active" if state else "inactive")
        return 0
    except AudioError as exc:
        print(f"screenbridge: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
