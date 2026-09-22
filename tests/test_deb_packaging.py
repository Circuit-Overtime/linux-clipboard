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
    wheel = tmp_path / "win_dot_panel-0.1.0-py3-none-any.whl"
    with ZipFile(wheel, "w") as archive:
        for name in (
            "win_dot_panel/__init__.py",
            "win_dot_panel/cli.py",
            "win_dot_panel/resources/emoji.json",
            "win_dot_panel/resources/UNICODE-LICENSE.txt",
            "win_dot_panel/storage/schema.sql",
        ):
            archive.writestr(
                name,
                "UNICODE LICENSE V3\nCopyright Unicode, Inc.\n"
                if name.endswith("UNICODE-LICENSE.txt")
                else "",
            )
        archive.writestr(
            "win_dot_panel-0.1.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: win-dot-panel\nVersion: 0.1.0\n",
        )
        archive.writestr("win_dot_panel-0.1.0.dist-info/WHEEL", "Root-Is-Purelib: true\n")

    script = Path(__file__).resolve().parents[1] / "scripts" / "build_deb.py"
    subprocess.run(
        [
            sys.executable,
            str(script),
            str(wheel),
            "--output-dir",
            str(tmp_path),
            "--revision",
            "2",
        ],
        check=True,
    )
    package = tmp_path / "win-dot-panel_0.1.0-2_all.deb"
    contents = subprocess.check_output(["dpkg-deb", "--contents", str(package)], text=True)
    depends = subprocess.check_output(["dpkg-deb", "--field", str(package), "Depends"], text=True)
    assert "./usr/bin/win-dot-panel" in contents
    assert "./usr/lib/python3/dist-packages/win_dot_panel/resources/emoji.json" in contents
    assert "./usr/share/doc/win-dot-panel/copyright" in contents
    assert "drwxr-xr-x root/root" in contents
    assert "-rwxr-xr-x root/root" in contents
    assert "wl-clipboard" in depends
    assert "python3-pyside6.qtwidgets" in depends
    assert "python3-pyside6.qtnetwork" in depends
    unpacked = tmp_path / "unpacked"
    subprocess.run(["dpkg-deb", "--extract", str(package), str(unpacked)], check=True)
    copyright_text = (unpacked / "usr/share/doc/win-dot-panel/copyright").read_text()
    assert "MIT License" in copyright_text
    assert "UNICODE LICENSE V3\nCopyright Unicode, Inc." in copyright_text

    subprocess.run(
        [
            sys.executable,
            str(script),
            str(wheel),
            "--output-dir",
            str(tmp_path),
            "--snapshot-run",
            "42",
        ],
        check=True,
    )
    snapshot = tmp_path / "win-dot-panel_0.1.0~main.42-1_all.deb"
    assert snapshot.exists()
    version = subprocess.check_output(["dpkg-deb", "--field", str(snapshot), "Version"], text=True)
    assert version.strip() == "0.1.0~main.42-1"
