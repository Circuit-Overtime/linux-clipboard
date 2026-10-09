# Packaging and releases

This document is for maintainers. The public README intentionally stays non-technical.

## Build a Debian package

```bash
./packaging/build-deb.sh
```

The package is written to `dist/screenbridge_VERSION_all.deb`. The builder validates the desktop and AppStream metadata when their validators are installed.

## Test the package locally

```bash
sudo apt install ./dist/screenbridge_1.0.0_all.deb
```

## Publish a release

The release workflow runs for tags beginning with `v`. The tag must match the version in `screenbridge/__init__.py`.

```bash
git tag -a v1.0.0 -m "ScreenBridge 1.0 Aurora"
git push origin v1.0.0
```

GitHub Actions runs the tests, builds the Debian package, creates a checksum, and publishes both versioned and stable download assets. The stable asset is used by `scripts/install-release.sh`.

The default public repository is `Circuit-Overtime/screenbridge`. Set `SCREENBRIDGE_REPOSITORY=owner/repository` when running the installer if the project moves.
