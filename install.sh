#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_dir="${XDG_DATA_HOME:-$HOME/.local/share}/screenbridge"
bin_dir="$HOME/.local/bin"
applications_dir="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

mkdir -p "$install_dir" "$bin_dir" "$applications_dir"
cp -R "$project_dir/screenbridge" "$install_dir/"
install -m 0755 "$project_dir/screenbridge-launcher" "$install_dir/screenbridge-launcher"
ln -sfn "$install_dir/screenbridge-launcher" "$bin_dir/screenbridge"

sed "s|@EXEC@|$install_dir/screenbridge-launcher|g" \
    "$project_dir/io.github.screenbridge.app.desktop.in" \
    > "$applications_dir/io.github.screenbridge.app.desktop"
chmod 0644 "$applications_dir/io.github.screenbridge.app.desktop"

echo "ScreenBridge is installed. Open it from your application menu."

