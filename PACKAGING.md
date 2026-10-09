# Packaging and releases

This document is for maintainers. The public README intentionally stays non-technical.

## Build a Debian package

```bash
./packaging/build-deb.sh --revision 1
```

The package is written to `dist/screenbridge_VERSION-REVISION_all.deb`. The builder validates the desktop and AppStream metadata when their validators are installed.

## Test the package locally

```bash
sudo apt install ./dist/screenbridge_1.0.0-1_all.deb
```

## Publish a release

The release workflow runs for tags beginning with `v`. The tag must match the version in `screenbridge/__init__.py`.

```bash
git tag -a v1.0.0-1 -m "ScreenBridge 1.0 Aurora, Debian revision 1"
git push origin v1.0.0-1
```

GitHub Actions runs the tests, builds the Debian package, creates checksums, and publishes both versioned and stable download assets. The stable asset is used by `scripts/install-release.sh`. If `PACKAGES_DEPLOY_TOKEN` is configured, the release also requests a deployment of `packages.elixpo.com`.

The primary installer is published at `https://packages.elixpo.com/screenbridge/install.sh`. `scripts/install-release.sh` remains a GitHub Releases fallback. The package-site source and APT signing key live in `Circuit-Overtime/linux-clipboard`.

## Package-site automation secret

Create a fine-grained GitHub personal access token with:

- Resource owner: `Circuit-Overtime`
- Repository access: only `linux-clipboard`
- Repository permission: **Contents — Read and write**

Add it to the `Circuit-Overtime/screenbridge` Actions secrets as `PACKAGES_DEPLOY_TOKEN`. It is used only to send the `package-released` repository-dispatch event. Do not copy `APT_SIGNING_KEY` into this repository.
