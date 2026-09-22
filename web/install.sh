#!/usr/bin/env bash
set -euo pipefail

repository_url="https://packages.elixpo.com/apt/"
key_url="${repository_url}keyring.asc"
expected_fingerprint="1D7CBFA8E3D9599C7CA03B86EEEA89F4C2DB5DE5"
keyring_path="/etc/apt/keyrings/win-dot-panel.gpg"
source_path="/etc/apt/sources.list.d/win-dot-panel.list"

if ! command -v apt-get >/dev/null 2>&1; then
    printf 'Win Dot Panel APT installation requires Debian or Ubuntu.\n' >&2
    exit 1
fi
if ! command -v curl >/dev/null 2>&1; then
    printf 'Install curl first with: sudo apt install curl\n' >&2
    exit 1
fi
if (( EUID == 0 )); then
    privileged=()
elif command -v sudo >/dev/null 2>&1; then
    privileged=(sudo)
else
    printf 'Run this script as root or install sudo first.\n' >&2
    exit 1
fi

"${privileged[@]}" apt-get update
"${privileged[@]}" apt-get install -y --no-install-recommends gnupg

temporary_dir=$(mktemp -d)
trap 'rm -rf "$temporary_dir"' EXIT
curl -fsSL "$key_url" -o "$temporary_dir/keyring.asc"

fingerprints=$(gpg --batch --show-keys --with-colons "$temporary_dir/keyring.asc" |
    awk -F: '$1 == "fpr" { print $10 }')
if [[ "$fingerprints" != "$expected_fingerprint" ]]; then
    printf 'APT signing key fingerprint did not match the published key.\n' >&2
    exit 1
fi

gpg --batch --dearmor -o "$temporary_dir/keyring.gpg" "$temporary_dir/keyring.asc"
"${privileged[@]}" install -d -m 755 /etc/apt/keyrings
"${privileged[@]}" install -m 644 "$temporary_dir/keyring.gpg" "$keyring_path"
printf 'deb [signed-by=%s] %s ./\n' "$keyring_path" "$repository_url" |
    "${privileged[@]}" tee "$source_path" >/dev/null
"${privileged[@]}" chmod 644 "$source_path"

"${privileged[@]}" apt-get update
"${privileged[@]}" apt-get install -y win-dot-panel
dpkg-query -W -f='Installed win-dot-panel ${Version}\n' win-dot-panel
