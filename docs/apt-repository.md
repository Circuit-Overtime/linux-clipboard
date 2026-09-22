# Signed APT repository

The product page is published at `https://packages.elixpo.com/`, with stable packages at `https://packages.elixpo.com/apt/`. The release workflow builds a flat APT index from the validated `.deb`, signs its Release file, and deploys it alongside the page through GitHub Pages. Development builds stay on GitHub Releases.

## Quick install

```bash
curl -fsSL -o /var/tmp/win-dot-panel-install.sh https://packages.elixpo.com/install.sh && bash /var/tmp/win-dot-panel-install.sh
```

This checks the repository key fingerprint, registers the signed APT source, and installs the latest stable package. The current signing key fingerprint is `1D7C BFA8 E3D9 599C 7CA0 3B86 EEEA 89F4 C2DB 5DE5`. If `curl` is missing, install it first with `sudo apt install curl`.

## Manual setup

Run these commands if you want to add the APT source yourself:

```bash
sudo apt update
sudo apt install curl gnupg
sudo install -d -m 755 /etc/apt/keyrings
curl -fsSL -o /var/tmp/win-dot-panel-apt.asc \
  https://packages.elixpo.com/apt/keyring.asc
sudo gpg --dearmor --yes -o /etc/apt/keyrings/win-dot-panel.gpg \
  /var/tmp/win-dot-panel-apt.asc
echo 'deb [signed-by=/etc/apt/keyrings/win-dot-panel.gpg] https://packages.elixpo.com/apt/ ./' | \
  sudo tee /etc/apt/sources.list.d/win-dot-panel.list
sudo apt update
sudo apt install win-dot-panel
apt-cache policy win-dot-panel
```

Run the repository setup once. Later stable updates use `sudo apt update` followed by `sudo apt install --only-upgrade win-dot-panel`. The key is scoped to this repository through `signed-by`; it is not added to APT's global trusted keyring.

## One-time maintainer setup

1. In **Repository Settings → Pages**, select **GitHub Actions** as the build and deployment source and set the custom domain to `packages.elixpo.com`.
2. At the DNS provider for `elixpo.com`, add a `CNAME` record with **Name/Host** `packages` and **Target/Value** `circuit-overtime.github.io`. Remove any other `A`, `AAAA`, or `CNAME` records for `packages` that conflict with it. GitHub Actions publishing does not need a `CNAME` file in the repository. Allow time for GitHub's DNS check and HTTPS certificate.
   Optionally verify `elixpo.com` in the **Circuit-Overtime account or organization Pages settings**. GitHub will give you a unique TXT value for `_github-pages-challenge-Circuit-Overtime.elixpo.com`; keep that TXT record after verification.
3. In **Repository Settings → Environments → github-pages**, allow stable tags. Under **Deployment branches and tags**, select **Selected branches and tags** and add a **tag** rule for `v*`. Stable release tags deploy the product page and signed APT repository together.
4. Create a dedicated signing key outside the repository and save it as the Actions secret `APT_SIGNING_KEY`:

   ```bash
   mkdir -p "$HOME/.local/share/win-dot-panel-apt-key"
   chmod 700 "$HOME/.local/share/win-dot-panel-apt-key"
   export GNUPGHOME="$HOME/.local/share/win-dot-panel-apt-key"
   gpg --batch --pinentry-mode loopback --passphrase '' \
     --quick-generate-key 'Win Dot Panel APT Repository' ed25519 sign 2y
   gpg --armor --export-secret-keys | gh secret set APT_SIGNING_KEY \
     -R Circuit-Overtime/linux-clipboard
   gpg --fingerprint
   ```

   Keep a secure backup of that directory. The private key must never be committed to Git.
5. Push to `main` to validate the package and publish a development build. Push a new stable `v<project-version>-<revision>` tag, such as `v1.0.0-1`, to publish that validated package as a GitHub release and deploy the product page and signed repository. Confirm that the homepage, `/apt/InRelease`, `/apt/Packages.gz`, the `.deb`, and `/apt/keyring.asc` are available before relying on APT installation.

The GitHub updater command remains available for development builds.
