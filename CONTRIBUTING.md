# Contributing

Changes to the packaging are welcome through pull requests. Describe the problem
and the validation you performed. Application feature requests and account issues
belong with OpenAI; this repository maintains the Flatpak integration.

## Build and test locally

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

Tests exercise compressed Debian extraction without running Debian installation hooks,
desktop rewriting/cleanup, Wayland and argument forwarding, and install metadata
with the embedded trust key. CI validates, builds and installs both architectures. Before
announcing a release, test a clean installation, launch, login persistence, voice,
portal file access and an update on the intended desktop; GUI behavior requires
an interactive session and account.

## Automated checks

Pull requests validate the manifest and scripts, build on native x64 and ARM64
runners, and test extra-data installation. They do not publish packages or receive
the signing key. Dependency updates are proposed through Dependabot and reviewed
before merging.
