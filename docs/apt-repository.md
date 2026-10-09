# Signed multi-package APT repository

The package catalog is published at `https://packages.elixpo.com/`, with Win Dot Panel at `/win-dot-panel/`, ScreenBridge at `/screenbridge/`, and stable packages at `/apt/`. The deployment workflow downloads the latest verified release from both application repositories, builds one signed APT index, and deploys the site atomically through GitHub Pages. Development builds stay on GitHub Releases.

## Quick install

```bash
curl -fsSL -o /var/tmp/win-dot-panel-install.sh \
  https://packages.elixpo.com/win-dot-panel/install.sh && \
bash /var/tmp/win-dot-panel-install.sh
```

This checks the repository key fingerprint, registers the signed APT source, and installs the latest stable package. The current signing key fingerprint is `1D7C BFA8 E3D9 599C 7CA0 3B86 EEEA 89F4 C2DB 5DE5`.

## Manual setup

```bash
sudo apt update
sudo apt install curl gnupg
sudo install -d -m 755 /etc/apt/keyrings
curl -fsSL -o /var/tmp/elixpo-packages.asc \
  https://packages.elixpo.com/apt/keyring.asc
sudo gpg --dearmor --yes -o /etc/apt/keyrings/elixpo-packages.gpg \
  /var/tmp/elixpo-packages.asc
echo 'deb [signed-by=/etc/apt/keyrings/elixpo-packages.gpg] https://packages.elixpo.com/apt/ ./' | \
  sudo tee /etc/apt/sources.list.d/elixpo-packages.list
sudo apt update
sudo apt install win-dot-panel
```

The same source can install `screenbridge`; do not register the repository a second time. Existing installations using `win-dot-panel.list` remain valid, and a new product installer migrates that source to the generic filename.

## Publishing architecture

- `Circuit-Overtime/linux-clipboard` owns GitHub Pages, the custom domain, the product-page sources, and `APT_SIGNING_KEY`.
- Stable package binaries come from the latest GitHub Releases in `linux-clipboard` and `screenbridge`.
- `.github/workflows/deploy-packages.yml` verifies both releases, builds the shared index, signs it, and deploys one Pages artifact.
- ScreenBridge requests a rebuild through a `package-released` repository dispatch after publishing a stable release.
- The signing key is never shared with an application repository.

## One-time maintainer setup

1. Keep GitHub Pages on **GitHub Actions** with the custom domain `packages.elixpo.com`.
2. Keep the existing `packages` CNAME pointing at `circuit-overtime.github.io` and retain the domain-verification TXT record.
3. In **Environments → github-pages**, allow stable `v*` tags and the `main` branch. Win Dot Panel tags deploy directly; ScreenBridge dispatches run from `main`.
4. Keep the existing `APT_SIGNING_KEY` secret in `Circuit-Overtime/linux-clipboard` and maintain an offline backup of its private key.
5. Add `PACKAGES_DEPLOY_TOKEN` to `Circuit-Overtime/screenbridge`. Use a fine-grained token scoped only to dispatching workflows in `Circuit-Overtime/linux-clipboard`; it does not need the signing key.
6. Run **Deploy packages.elixpo.com** manually once after these changes land. Confirm both package records before announcing the ScreenBridge route.

## Release process

1. Publish application releases with tags matching `v<upstream-version>-<Debian-revision>`.
2. Let the application workflow upload its versioned `.deb` and `SHA256SUMS`.
3. The package-site workflow downloads the latest release from both projects, verifies checksums and package identities, then signs and deploys the combined repository.
4. Confirm `/win-dot-panel/`, `/screenbridge/`, both installers, `/apt/InRelease`, `/apt/Packages.gz`, and both files under `/apt/pool/`.

The GitHub updater remains available for Win Dot Panel development builds.
