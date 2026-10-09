#!/usr/bin/env bash
set -euo pipefail

repository="${SCREENBRIDGE_REPOSITORY:-Circuit-Overtime/screenbridge}"
release_url="https://github.com/$repository/releases/latest/download"
download_dir="$(mktemp -d -t screenbridge-install.XXXXXXXX)"

cleanup() {
    if [[ "$download_dir" == /tmp/screenbridge-install.* && -d "$download_dir" ]]; then
        rm -rf -- "$download_dir"
    fi
}
trap cleanup EXIT

echo "Downloading ScreenBridge…"
curl --fail --location --silent --show-error \
    "$release_url/screenbridge_all.deb" \
    --output "$download_dir/screenbridge_all.deb"
curl --fail --location --silent --show-error \
    "$release_url/screenbridge_all.deb.sha256" \
    --output "$download_dir/screenbridge_all.deb.sha256"

(
    cd "$download_dir"
    sha256sum --check screenbridge_all.deb.sha256
)

echo "Installing ScreenBridge…"
sudo apt-get install -y "$download_dir/screenbridge_all.deb"
echo "Done. Open ScreenBridge from your applications menu."
