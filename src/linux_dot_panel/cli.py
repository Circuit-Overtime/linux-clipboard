"""Command line entry point."""

from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="linux-dot-panel",
        description="Emoji and clipboard panel for Linux",
    )
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("demo", help="Open the popup prototype")
    args = parser.parse_args(argv)

    if args.command == "demo":
        from linux_dot_panel.app import run_demo

        return run_demo()

    parser.print_help()
    return 0
