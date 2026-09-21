from __future__ import annotations

import os
import socket
import subprocess
import sys
import time

import pytest

from linux_dot_panel.ipc.protocol import decode_message, encode_message


def test_ipc_message_round_trip():
    payload = {"command": "toggle"}
    assert decode_message(encode_message(payload)) == payload


def test_cli_reaches_daemon_over_unix_socket(tmp_path):
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    with socket.socket(socket.AF_UNIX) as probe:
        try:
            probe.bind(str(runtime / "probe.sock"))
        except PermissionError:
            pytest.skip("This environment does not permit Unix socket binding")
    env = dict(
        os.environ,
        XDG_RUNTIME_DIR=str(runtime),
        XDG_STATE_HOME=str(tmp_path / "state"),
        XDG_CONFIG_HOME=str(tmp_path / "config"),
        QT_QPA_PLATFORM="offscreen",
    )
    command = [sys.executable, "-m", "linux_dot_panel"]
    daemon = subprocess.Popen([*command, "daemon"], env=env)

    def cli(action: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [*command, action], env=env, capture_output=True, text=True, timeout=5, check=False
        )

    try:
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            status = cli("status")
            if status.returncode == 0:
                break
            if daemon.poll() is not None:
                raise AssertionError(f"Daemon exited with {daemon.returncode}")
            time.sleep(0.05)
        else:
            raise AssertionError("Daemon did not create its socket")

        for action in ("show", "hide", "toggle", "quit"):
            result = cli(action)
            assert result.returncode == 0, (action, result.stderr)
        assert daemon.wait(timeout=3) == 0

        # A shortcut must also work when the daemon was not already running.
        result = cli("toggle")
        assert result.returncode == 0, result.stderr
        assert cli("status").returncode == 0
        assert cli("quit").returncode == 0
    finally:
        if daemon.poll() is None:
            daemon.terminate()
            daemon.wait(timeout=3)
        if cli("status").returncode == 0:
            cli("quit")
