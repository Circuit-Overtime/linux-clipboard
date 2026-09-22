"""Build a Debian 13 package from a verified, pure Python application wheel."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from email.parser import Parser
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

PACKAGE = "linux-dot-panel"
MODULE = "linux_dot_panel"
PYTHON_DIR = Path("usr/lib/python3/dist-packages")
DEPENDENCIES = (
    "python3 (>= 3.10), python3-pyside6.qtwidgets (>= 6.6), "
    "python3-pyside6.qtnetwork (>= 6.6), "
    "python3-gi, gir1.2-atspi-2.0, wl-clipboard"
)


def _wheel_version(wheel: ZipFile) -> str:
    names = wheel.namelist()
    metadata_files = [name for name in names if name.endswith(".dist-info/METADATA")]
    wheel_files = [name for name in names if name.endswith(".dist-info/WHEEL")]
    if len(metadata_files) != 1 or len(wheel_files) != 1:
        raise ValueError("Expected one wheel metadata directory")
    metadata = Parser().parsestr(wheel.read(metadata_files[0]).decode("utf-8"))
    if metadata.get("Name", "").lower().replace("_", "-") != PACKAGE:
        raise ValueError("Wheel package name does not match linux-dot-panel")
    version = metadata.get("Version", "")
    if not re.fullmatch(r"[0-9][A-Za-z0-9.+~]*", version):
        raise ValueError(f"Unsupported Debian package version: {version}")
    wheel_info = wheel.read(wheel_files[0]).decode("utf-8")
    if "Root-Is-Purelib: true" not in wheel_info:
        raise ValueError("Only pure Python wheels are supported")
    return version


def _copy_module(wheel: ZipFile, stage: Path) -> None:
    members = [name for name in wheel.namelist() if name.startswith(f"{MODULE}/")]
    required = {
        f"{MODULE}/__init__.py",
        f"{MODULE}/cli.py",
        f"{MODULE}/resources/emoji.json",
        f"{MODULE}/storage/schema.sql",
    }
    if not required.issubset(members):
        raise ValueError("Wheel is missing required application files")
    for name in members:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or not name.startswith(f"{MODULE}/"):
            raise ValueError(f"Unsafe wheel member: {name}")
        if name.endswith("/"):
            continue
        if path.suffix in (".so", ".pyd"):
            raise ValueError("Compiled wheels are not supported")
        target = stage / PYTHON_DIR / Path(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(wheel.read(name))


def _write_control(stage: Path, version: str, revision: int) -> None:
    control = stage / "DEBIAN" / "control"
    control.parent.mkdir(parents=True)
    control.write_text(
        f"Package: {PACKAGE}\n"
        f"Version: {version}-{revision}\n"
        "Section: utils\n"
        "Priority: optional\n"
        "Architecture: all\n"
        "Maintainer: Local package builder <local@localhost>\n"
        f"Depends: {DEPENDENCIES}\n"
        "Description: Emoji and clipboard panel for Linux\n"
        " A floating emoji, clipboard, kaomoji, and symbols panel for GNOME and KDE.\n",
        encoding="utf-8",
    )


def _set_package_modes(stage: Path) -> None:
    stage.chmod(0o755)
    for path in stage.rglob("*"):
        path.chmod(0o755 if path.is_dir() else 0o644)
    (stage / "usr/bin" / PACKAGE).chmod(0o755)


def build_deb(wheel_path: Path, output_dir: Path, *, revision: int = 1) -> Path:
    if revision < 1:
        raise ValueError("Debian revision must be positive")
    with ZipFile(wheel_path) as wheel:
        version = _wheel_version(wheel)
        destination = output_dir / f"{PACKAGE}_{version}-{revision}_all.deb"
        output_dir.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix="linux-dot-panel-deb-") as temporary:
            stage = Path(temporary)
            _copy_module(wheel, stage)
            launcher = stage / "usr/bin" / PACKAGE
            launcher.parent.mkdir(parents=True)
            launcher.write_text(
                "#!/usr/bin/python3\n"
                "from linux_dot_panel.cli import main\n"
                "raise SystemExit(main())\n",
                encoding="utf-8",
            )
            _write_control(stage, version, revision)
            _set_package_modes(stage)
            subprocess.run(
                ["dpkg-deb", "--build", "--root-owner-group", str(stage), str(destination)],
                check=True,
            )
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path, help="Verified linux-dot-panel .whl file")
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument("--revision", type=int, default=1, help="Debian package revision")
    args = parser.parse_args()
    try:
        path = build_deb(args.wheel, args.output_dir, revision=args.revision)
    except (OSError, ValueError, BadZipFile, subprocess.CalledProcessError) as error:
        print(f"Debian package build failed: {error}", file=sys.stderr)
        return 1
    print(f"Built {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
