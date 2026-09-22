from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest


def test_deb_contains_launcher_data_and_dependencies(tmp_path):
    if shutil.which("dpkg-deb") is None:
        pytest.skip("dpkg-deb is unavailable")
    wheel = tmp_path / "linux_dot_panel-0.1.0-py3-none-any.whl"
    with ZipFile(wheel, "w") as archive:
        for name in (
            "linux_dot_panel/__init__.py",
            "linux_dot_panel/cli.py",
            "linux_dot_panel/resources/emoji.json",
            "linux_dot_panel/storage/schema.sql",
        ):
            archive.writestr(name, "")
        archive.writestr(
            "linux_dot_panel-0.1.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: linux-dot-panel\nVersion: 0.1.0\n",
        )
        archive.writestr("linux_dot_panel-0.1.0.dist-info/WHEEL", "Root-Is-Purelib: true\n")

    script = Path(__file__).resolve().parents[1] / "scripts" / "build_deb.py"
    subprocess.run(
        [sys.executable, str(script), str(wheel), "--output-dir", str(tmp_path)], check=True
    )
    package = tmp_path / "linux-dot-panel_0.1.0-1_all.deb"
    contents = subprocess.check_output(["dpkg-deb", "--contents", str(package)], text=True)
    depends = subprocess.check_output(["dpkg-deb", "--field", str(package), "Depends"], text=True)
    assert "./usr/bin/linux-dot-panel" in contents
    assert "./usr/lib/python3/dist-packages/linux_dot_panel/resources/emoji.json" in contents
    assert "drwxr-xr-x root/root" in contents
    assert "-rwxr-xr-x root/root" in contents
    assert "wl-clipboard" in depends
    assert "python3-pyside6.qtwidgets" in depends
