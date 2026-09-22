#!/usr/bin/env bash
set -euo pipefail

package=$(realpath "$1")
site=$(realpath -m "$2")
repository="$site/apt"
mkdir -p "$repository"
cp "$package" "$repository/"
touch "$site/.nojekyll"

cd "$repository"
dpkg-scanpackages . /dev/null > Packages
gzip -n -9 -c Packages > Packages.gz
apt-ftparchive \
  -o 'APT::FTPArchive::Release::Origin=Circuit Overtime' \
  -o 'APT::FTPArchive::Release::Label=Win Dot Panel' \
  -o 'APT::FTPArchive::Release::Suite=stable' \
  -o 'APT::FTPArchive::Release::Codename=stable' \
  -o 'APT::FTPArchive::Release::Description=Win Dot Panel stable packages' \
  release . > Release

fingerprint=$(gpg --batch --with-colons --list-secret-keys | awk -F: '$1 == "fpr" {print $10; exit}')
if [[ -z "$fingerprint" ]]; then
  echo 'No APT signing key is available' >&2
  exit 1
fi
gpg --batch --yes --armor --export "$fingerprint" > keyring.asc
gpg --batch --yes --local-user "$fingerprint" --clearsign --output InRelease Release
gpg --batch --yes --local-user "$fingerprint" --armor --detach-sign --output Release.gpg Release
