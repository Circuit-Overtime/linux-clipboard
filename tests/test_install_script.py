from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

FINGERPRINT = "1D7CBFA8E3D9599C7CA03B86EEEA89F4C2DB5DE5"


@pytest.mark.parametrize("fingerprint,success", [(FINGERPRINT, True), ("0" * 40, False)])
def test_install_script_checks_key_before_registering_source(tmp_path, fingerprint, success):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    scripts = {
        "sudo": """#!/bin/sh
printf '%s\\n' "$*" >> "$INSTALL_LOG"
if [ "$1" = tee ]; then cat > "$SOURCE_CAPTURE"; fi
""",
        "curl": """#!/bin/sh
while [ "$#" -gt 0 ]; do
    if [ "$1" = -o ]; then shift; printf 'test key' > "$1"; fi
    shift
done
""",
        "gpg": """#!/bin/sh
case " $* " in
    *' --show-keys '*) printf 'fpr:::::::::%s:\\n' "$FAKE_FINGERPRINT" ;;
    *' --dearmor '*)
        while [ "$#" -gt 0 ]; do
            if [ "$1" = -o ]; then shift; printf 'test keyring' > "$1"; fi
            shift
        done ;;
esac
""",
        "dpkg-query": "#!/bin/sh\nprintf 'Installed win-dot-panel 1.0.0-1\\n'\n",
    }
    for name, content in scripts.items():
        path = fake_bin / name
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)

    log = tmp_path / "sudo.log"
    source = tmp_path / "source.list"
    env = dict(
        os.environ,
        PATH=f"{fake_bin}:{os.environ['PATH']}",
        INSTALL_LOG=str(log),
        SOURCE_CAPTURE=str(source),
        FAKE_FINGERPRINT=fingerprint,
    )
    script = Path(__file__).resolve().parents[1] / "web" / "install.sh"
    result = subprocess.run(
        ["bash", str(script)], env=env, capture_output=True, text=True, check=False
    )

    assert (result.returncode == 0) == success
    assert (source.exists()) == success
    if success:
        assert source.read_text() == (
            "deb [signed-by=/etc/apt/keyrings/win-dot-panel.gpg] "
            "https://packages.elixpo.com/apt/ ./\n"
        )
        assert "apt-get install -y win-dot-panel" in log.read_text()
        assert "Installed win-dot-panel 1.0.0-1" in result.stdout
    else:
        assert "fingerprint did not match" in result.stderr
        assert "apt-get install -y win-dot-panel" not in log.read_text()
