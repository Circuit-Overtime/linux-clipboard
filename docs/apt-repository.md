# Signed APT repository

Stable releases can also be published at `https://circuit-overtime.github.io/linux-clipboard/apt/`. The release workflow builds a flat APT index from the validated `.deb`, signs its Release file, and deploys it through GitHub Pages. Development builds stay on GitHub Releases.

## One-time maintainer setup

1. In **Repository Settings → Pages**, select **GitHub Actions** as the build and deployment source.
2. In **Repository Settings → Environments → github-pages**, allow deployment from stable tags. Under **Deployment branches and tags**, select **Selected branches and tags** and add a **tag** rule for `v*`. A default-branch-only rule would block this workflow because stable releases run from tags.
3. Create a dedicated signing key outside the repository and save it as the Actions secret `APT_SIGNING_KEY`:

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
4. Push a new stable `v<project-version>-<revision>` tag. The workflow first runs checks and publishes the GitHub release, then builds and deploys the signed APT repository. Confirm that `apt/InRelease`, `apt/Packages.gz`, the `.deb`, and `apt/keyring.asc` are available on the Pages site before adding the APT instructions to the public install section.

## Install from APT after the first deployment

```bash
sudo install -d -m 755 /etc/apt/keyrings
curl -fsSL -o /var/tmp/win-dot-panel-apt.asc \
  https://circuit-overtime.github.io/linux-clipboard/apt/keyring.asc
sudo gpg --dearmor --yes -o /etc/apt/keyrings/win-dot-panel.gpg \
  /var/tmp/win-dot-panel-apt.asc
echo 'deb [signed-by=/etc/apt/keyrings/win-dot-panel.gpg] https://circuit-overtime.github.io/linux-clipboard/apt/ ./' |
  sudo tee /etc/apt/sources.list.d/win-dot-panel.list
sudo apt update
sudo apt install win-dot-panel
```

Later stable updates use `sudo apt update && sudo apt upgrade`. The key is scoped to this repository through `signed-by`; it is not added to APT's global trusted keyring. The GitHub updater command remains available for development builds.
