from __future__ import annotations

import subprocess

import pytest

from win_dot_panel import __version__, cli


def test_version_option_prints_source_version(capsys):
    with pytest.raises(SystemExit) as result:
        cli.main(["--version"])

    assert result.value.code == 0
    assert capsys.readouterr().out == f"win-dot-panel {__version__}\n"


def test_system_package_version_includes_debian_revision(monkeypatch, capsys):
    monkeypatch.setattr(cli, "__file__", "/usr/lib/python3/dist-packages/win_dot_panel/cli.py")

    def dpkg_query(command, **_kwargs):
        assert command == ["dpkg-query", "-W", "-f=${Version}", "win-dot-panel"]
        return subprocess.CompletedProcess(command, 0, "1.0.0-1")

    monkeypatch.setattr(cli.subprocess, "run", dpkg_query)

    with pytest.raises(SystemExit) as result:
        cli.main(["--version"])

    assert result.value.code == 0
    assert capsys.readouterr().out == "win-dot-panel 1.0.0-1\n"
