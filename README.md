# ChatGPT Flatpak

Community packaging of **OpenAI's official Linux desktop application**, for x86_64
and aarch64. This project is independent of OpenAI. The application is proprietary;
the packaging code is MIT licensed. The manifest uses matching Freedesktop and
Electron2 BaseApp **26.08** branches, with Zypak for Electron subprocess sandboxing.

## Install

After the repository owner completes the publishing setup below:

```sh
flatpak install --user https://geoffbelknap.github.io/chatgpt-flatpak/com.openai.ChatGPT.flatpakref
```

Fork maintainers should replace the owner and repository in that URL. The published
home page shows the exact command for each deployment. The `.flatpakref` automatically selects your
architecture, imports the repository public key, and offers the Flathub runtime.
Review the remote and permission prompts, then launch from the applications menu:

```sh
flatpak run com.openai.ChatGPT
flatpak update --user
```

Bazzite, Fedora Silverblue and Kinoite need no `rpm-ostree` layering or changes to
the immutable operating system. Install as your regular user, not with `sudo`.
Discover and other Flatpak-aware stores can discover updates from the installed
remote. Bazaar support depends on its version and configuration; the commands
above work independently of a store's UI. Store listings may show a generic icon
before installation because the upstream icon is downloaded only on install.

## Trust and redistribution

The hosted OSTree repository contains the wrapper, extraction tool, metadata, and
open-source Electron BaseApp libraries. **No OpenAI application binary, `.deb`, or
OpenAI icon is redistributed through GitHub, Actions artifacts, or GitHub Pages.**

On installation or an app update, Flatpak:

1. Reads the versioned HTTPS URL, byte size, and SHA256 from the signed repository.
2. Downloads the `.deb` directly from `persistent.oaistatic.com`, OpenAI's official
   CDN. Flatpak verifies its size and SHA256 before extraction.
3. Runs `/app/bin/apply_extra` offline in a restricted installation sandbox.
   The script extracts `data.tar.*` with `ar` and `tar`, moves the application into
   `/app/extra/chatgpt`, and exports its desktop entry and icon through
   `/app/extra/export/share/`. Debian maintainer scripts are never executed.
4. Removes the downloaded archive and temporary extraction files. The resulting
   application and exports stay on that user's machine.

SHA256 verifies that the downloaded bytes match the package pinned by the
maintainer; it is not an OpenAI digital signature. You trust OpenAI's HTTPS
repository/CDN, the packaging repository and its maintainers, GitHub Actions, and
the repository signing key. The external data checker's Debian backend retrieves
apt metadata over HTTPS but does **not** validate apt Release signatures. Automatic
updates retain this trust model; do not describe them as apt-signature verified.
OpenAI's application terms continue to apply.

The initial pins are real, downloaded and SHA256 checked against the official apt
indexes: **26.1120.50957**, amd64 and arm64. No checksum or size placeholder needs
to be filled in. OpenAI's mutable `deb/latest/` URLs can lag the apt index, so the
manifest intentionally uses immutable versioned `pool/` URLs.

Upstream references:

- [Official Linux app and download links](https://learn.chatgpt.com/docs/linux/linux-app)
- [Official apt repository](https://persistent.oaistatic.com/codex-app-prod/linux/deb/dists/stable/Release)
- [External data checker documentation](https://github.com/flathub-infra/flatpak-external-data-checker)
- [Flatpak build action](https://github.com/flatpak/flatpak-github-actions)

## Publish your fork

1. Create a public GitHub repository from these files with default branch `main`.
   Enable Actions, including scheduled workflows for forks. In **Settings →
   Actions → General → Workflow permissions**, enable read/write permissions.
   Organization policies must allow the workflows' `contents: write`,
   `actions: write`, `pages: write`, and `id-token: write` scopes. Direct pushes
   to `main` must be allowed for the update bot; if branch protection blocks them,
   change the update workflow to your organization's approved PR process.
2. Create a **dedicated, unencrypted CI signing key** in an isolated local keyring:

   ```sh
   export GNUPGHOME="$(mktemp -d)"
   chmod 700 "$GNUPGHOME"
   gpg --batch --passphrase '' --quick-generate-key \
     'ChatGPT Flatpak Repository <flatpak@example.com>' rsa4096 sign 0
   gpg --list-secret-keys --keyid-format long
   gpg --armor --export-secret-keys YOUR_FULL_FINGERPRINT > repository-signing-key.asc
   ```

   In the `github-pages` environment, add the complete armored private key as the
   Actions **secret** `GPG_PRIVATE_KEY`. Add the full fingerprint as the environment
   **variable** `GPG_KEY_ID`. Replace `keys/fingerprint.txt` with that fingerprint and
   `keys/repository-signing-key.pub` with its armored public key before pushing. Back up the key securely and remove the local export when done.
   Keep this key stable across deployments; existing clients pin its public key.
   Publishing deliberately fails if either setting is missing. No unsigned
   fallback or `--no-gpg-verify` is used for the published remote.
3. In **Settings → Pages → Build and deployment**, select **GitHub Actions**.
   The workflow also mirrors the complete repository to a `gh-pages` branch, but
   uses explicit Pages artifact deployment: commits made with `GITHUB_TOKEN` do
   not trigger branch-based Pages builds. Allow the `github-pages` environment
   to deploy from `main`, and ensure protection rules allow unattended publishing
   if you want automatic updates.
4. Optionally set the Actions variable `PAGES_URL` for a custom HTTPS domain or a
   user/organization Pages repository (for example `https://OWNER.github.io/`).
   Normal project repositories need no URL configuration: the workflow generates
   `https://<owner>.github.io/<repo>/` from `GITHUB_REPOSITORY`. A custom domain
   also requires the usual GitHub Pages DNS/domain setup.
5. Run **Build and publish** from the Actions tab. Both native runner builds must
   pass before publishing. After Pages deployment, download
   `com.openai.ChatGPT.flatpakref` from the published site and test installation.

Do not rotate the signing key casually. Distribute a new public key to existing
clients using a documented migration before removing the old key. Protect `main`
and the Actions secrets from untrusted changes. Pull requests build and validate
without publishing or receiving signing credentials.

## Automatic updates and hosting

`update-checker.yml` runs daily at **06:00 UTC** and on manual dispatch. The
official external-data-checker container reads both architecture-specific
`debian-repo` entries, updates URLs, sizes and SHA256s, validates the result,
and commits to `main`. It then explicitly dispatches `build-and-publish.yml`:
`GITHUB_TOKEN` pushes alone do not start another workflow. Manual `main` pushes
also trigger builds normally. The updater dispatches even without a diff, so a
previous dispatch failure recovers on the next run.

The build workflow uses native x64 and ARM64 GitHub runners and the official
`flatpak/flatpak-github-actions/flatpak-builder` action. It produces two OSTree
repositories without embedding the proprietary payload. Each runner then performs
a local installation to verify the upstream download, checksum, extraction,
Zypak availability and main executable dependencies. That installed payload is
not uploaded in build artifacts. Publishing restores
the previous `gh-pages` snapshot, imports both architecture refs, signs app
commits and summary metadata, and writes a `.flatpakref`, `.flatpakrepo`, public
key and install page at the Pages root.

Old OSTree objects are retained so clients using a cached summary can still fetch
that version. The branch is force-replaced to avoid keeping repeated Git histories
of the same OSTree objects; the OSTree history itself is preserved. Monitor GitHub
Pages storage and bandwidth limits. For long-lived/high-traffic deployments,
move the same signed OSTree repository to suitable object/static hosting and set
`PAGES_URL`. Retention/pruning needs a deliberate grace period for cached clients.
Private forks may need a different ARM runner label or paid runner access.

Actions are pinned to full commit hashes, and the official checker container is
pinned to an image digest. Dependabot proposes weekly Action updates. Review
checker image updates separately and update its digest deliberately.

## Signing-key protection and recovery

The production public key is in [keys/repository-signing-key.pub](keys/repository-signing-key.pub)
and its fingerprint is in [keys/fingerprint.txt](keys/fingerprint.txt). The private
key is an environment secret in `github-pages`, whose deployment policy allows
only `main`. The default workflow token is read-only; publishing and updater
jobs request their necessary write scopes explicitly. Signing happens in the
publishing job, and its temporary keyring is removed immediately afterward,
including on failure. No build or pull-request job receives the signing secret.

For the initial maintainer setup, recovery copies of the private key and its
revocation certificate were stored in the maintainer's desktop Secret Service
keyring, outside this repository. They are labeled **ChatGPT Flatpak repository
signing key recovery** and **ChatGPT Flatpak signing key revocation certificate**.
Back these up separately in a password manager or encrypted offline storage;
the local keyring alone is not an independent disaster-recovery backup.
Never paste recovery material into issues, chat, logs, or commits.

Anyone able to change trusted publishing code can potentially access the key
while the job runs. Limit write access, protect your GitHub account with a
passkey or 2FA, and review workflow/script changes. The current setup permits
unattended releases without a required human deployment approval.

## Permissions and limitations

The app has Wayland/X11, IPC, GPU, PulseAudio (including microphone), network,
Downloads read/write access, notifications, tray integration, screensaver and
Secret Service access. Other files should be selected through a desktop portal.
The standard `org.freedesktop.portal.Desktop` interface is allowed by Flatpak;
the requested GlobalShortcuts bus name is also listed, but app support and the
desktop portal backend determine whether shortcuts work. A running Secret
Service provider, such as GNOME Keyring or compatible KWallet, is needed for
encrypted login persistence. The wrapper does not force a plaintext password store.

Wayland sessions receive the requested Ozone and IME flags; explicit user flags
are forwarded after the defaults. OpenAI documents native Wayland as
experimental. For troubleshooting, try:

```sh
flatpak run com.openai.ChatGPT --ozone-platform=x11
```

The default X11 socket is a fallback socket, so it may not be exposed when a
Wayland socket is available. To force XWayland for a single run:

```sh
flatpak run --nosocket=wayland --socket=x11 com.openai.ChatGPT --ozone-platform=x11
```

Flatpak changes the app's view of the host. Host command execution, local coding
toolchains, browser extensions/native messaging, global shortcuts, screen capture
and other agent/desktop integrations may require upstream portal support and are
not guaranteed by this package. No host-execution escape or broad home-directory
permission is included. Files in Downloads are available directly; app data lives
under `~/.var/app/com.openai.ChatGPT/`. The in-app updater cannot replace the
read-only application; use `flatpak update` for packaged releases.

## Local development and verification

On a workstation with Flatpak and flatpak-builder (or the Flathub Builder app):

```sh
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak-builder --user --install-deps-from=flathub --force-clean \
  --repo=repo build com.openai.ChatGPT.yml
```

If using `org.flatpak.Builder`, replace `flatpak-builder` with
`flatpak run org.flatpak.Builder`. Do not use `--disable-sandbox` or Electron's
`--no-sandbox`. The `ar` module builds GNU binutils from pinned sources, since `ar`
is present in the SDK but not guaranteed in the installed runtime. Only the ar
executable is installed; libbfd/libiberty are linked statically.

For an explicitly local, unsigned development repository only:

```sh
flatpak remote-add --user --no-gpg-verify chatgpt-dev "$(pwd)/repo"
flatpak install --user chatgpt-dev com.openai.ChatGPT
flatpak run com.openai.ChatGPT
```

The installation downloads roughly 500 MB from OpenAI, then extracts roughly
1.5 GB; allow additional temporary disk space. A package install is the point at
which the real extra-data hook runs; a successful builder export alone does not
prove extraction or GUI/login/voice behavior.

Offline checks (Python 3, PyYAML, binutils, tar, ShellCheck and desktop-file-utils):

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
shellcheck apply_extra.sh chatgpt-wrapper.sh scripts/*.sh
desktop-file-validate com.openai.ChatGPT.desktop
```

Tests exercise compressed Debian extraction without maintainer execution,
desktop rewriting/cleanup, Wayland and argument forwarding, and install metadata
with the embedded trust key. CI validates, builds and installs both architectures. Before
announcing a release, test a clean installation, launch, login persistence, voice,
portal file access and an update on the intended desktop; GUI behavior requires
an interactive session and account.
