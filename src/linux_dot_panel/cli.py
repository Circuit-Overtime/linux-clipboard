"""Command line entry point."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time

from linux_dot_panel.ipc.client import send_command


def _start_daemon() -> None:
    process = subprocess.Popen(
        [sys.executable, "-m", "linux_dot_panel", "daemon"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        try:
            send_command("status", timeout=0.1)
            return
        except OSError:
            if process.poll() not in (None, 0):
                raise RuntimeError(
                    "Daemon exited during startup; run `linux-dot-panel daemon` for details"
                ) from None
            time.sleep(0.05)
    raise RuntimeError(
        "Daemon did not start within 3 seconds; run `linux-dot-panel daemon` for details"
    )


def _run_command(command: str) -> int:
    if command == "toggle":
        try:
            response = send_command(command)
        except OSError:
            try:
                _start_daemon()
                response = send_command("show")
            except (OSError, RuntimeError) as error:
                print(error, file=sys.stderr)
                return 1
    else:
        try:
            response = send_command(command)
        except OSError:
            if command == "status":
                print("stopped")
                return 1
            print("Daemon is not running", file=sys.stderr)
            return 1

    if not response["ok"]:
        print(response.get("error", "Daemon rejected command"), file=sys.stderr)
        return 1
    if command == "status":
        print("running")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="linux-dot-panel",
        description="Emoji and clipboard panel for Linux",
    )
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("demo", help="Open the popup prototype")
    commands.add_parser("daemon", help="Run the background daemon")
    install_command = commands.add_parser("install", help="Start the daemon on login")
    install_command.add_argument(
        "--method", choices=("xdg", "systemd"), default="xdg", help="Session startup method"
    )
    commands.add_parser("uninstall", help="Remove session autostart")
    for command in ("toggle", "show", "hide", "status", "quit"):
        commands.add_parser(command, help=f"Send {command} to the daemon")
    args = parser.parse_args(argv)

    if args.command == "demo":
        from linux_dot_panel.app import run_demo

        return run_demo()
    if args.command == "daemon":
        from linux_dot_panel.daemon import run_daemon

        return run_daemon()
    if args.command in ("install", "uninstall"):
        from linux_dot_panel.desktop.autostart import install, uninstall

        try:
            if args.command == "install":
                print(f"Autostart installed: {install(args.method)}")
            else:
                removed = uninstall()
                print("Autostart removed" if removed else "Autostart was not installed")
        except (OSError, ValueError) as error:
            print(error, file=sys.stderr)
            return 1
        return 0
    if args.command in ("toggle", "show", "hide", "status", "quit"):
        return _run_command(args.command)

    parser.print_help()
    return 0
