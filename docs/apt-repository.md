# Signed APT repository

The product page is published at `https://packages.elixpo.com/`, with stable packages at `https://packages.elixpo.com/apt/`. The release workflow builds a flat APT index from the validated `.deb`, signs its Release file, and deploys it alongside the page through GitHub Pages. Development builds stay on GitHub Releases.

## One-time maintainer setup

1. In **Repository Settings → Pages**, select **GitHub Actions** as the build and deployment source and set the custom domain to `packages.elixpo.com`.
2. At the DNS provider for `elixpo.com`, add a `CNAME` record with **Name/Host** `packages` and **Target/Value** `circuit-overtime.github.io`. Remove any other `A`, `AAAA`, or `CNAME` records for `packages` that conflict with it. GitHub Actions publishing does not need a `CNAME` file in the repository. Allow time for GitHub's DNS check and HTTPS certificate.
   Optionally verify `elixpo.com` in the **Circuit-Overtime account or organization Pages settings**. GitHub will give you a unique TXT value for `_github-pages-challenge-Circuit-Overtime.elixpo.com`; keep that TXT record after verification.
3. In **Repository Settings → Environments → github-pages**, allow deployment from `main` and stable tags. Under **Deployment branches and tags**, select **Selected branches and tags** and add a **branch** rule for `main` and a **tag** rule for `v*`. The page is deployed from main; stable releases are deployed from tags.
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
5. Push to `main` to deploy the product page. Once the signing key exists, the workflow also publishes the latest stable package to APT. Push a new stable `v<project-version>-<revision>` tag to publish that validated package as a GitHub release and update the signed repository. Confirm that the homepage, `/apt/InRelease`, `/apt/Packages.gz`, the `.deb`, and `/apt/keyring.asc` are available before relying on APT installation.

## Install from APT after the first deployment

```bash
sudo install -d -m 755 /etc/apt/keyrings
curl -fsSL -o /var/tmp/win-dot-panel-apt.asc \
  https://packages.elixpo.com/apt/keyring.asc
sudo gpg --dearmor --yes -o /etc/apt/keyrings/win-dot-panel.gpg \
  /var/tmp/win-dot-panel-apt.asc
echo 'deb [signed-by=/etc/apt/keyrings/win-dot-panel.gpg] https://packages.elixpo.com/apt/ ./' |
  sudo tee /etc/apt/sources.list.d/win-dot-panel.list
sudo apt update
sudo apt install win-dot-panel
```

Later stable updates use `sudo apt update && sudo apt upgrade`. The key is scoped to this repository through `signed-by`; it is not added to APT's global trusted keyring. The GitHub updater command remains available for development builds.
