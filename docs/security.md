# Verify this package

This is **unofficial community packaging** of OpenAI's Linux ChatGPT app. It is
not affiliated with, endorsed by, or supported by OpenAI.

These checks help establish where the software came from and whether its bytes
match the published package. They cannot prove that software is free of malware,
backdoors, or vulnerabilities. No independent security audit is claimed.

## What you can inspect

- **The upstream application:** OpenAI links its Linux packages from the
  [official Linux app documentation](https://learn.chatgpt.com/docs/linux/linux-app).
  The Flatpak downloads its `.deb` directly from `persistent.oaistatic.com` and
  verifies the pinned size and SHA256 before extraction. GitHub hosts the wrapper,
  metadata, and open-source supporting components; it does not redistribute the
  OpenAI application or its icon.
- **The packaging code:** The [manifest](../com.openai.ChatGPT.yml) specifies the
  download URLs, checksums, dependencies, and permissions. The
  [extraction script](../apply_extra.sh) unpacks the app locally without running
  Debian installation hooks. The [launcher](../chatgpt-wrapper.sh) starts it
  through Zypak. The upstream application files are not patched by these scripts.
- **The release pipeline:** The [build workflow](../.github/workflows/build-and-publish.yml)
  builds and installs on native x64 and ARM64 runners before signing a release.
  Public [Actions logs](https://github.com/geoffbelknap/chatgpt-flatpak/actions/workflows/build-and-publish.yml)
  show the results. The [updater](../.github/workflows/update-checker.yml) is public too.
- **The release record:** [verification.json](https://geoffbelknap.github.io/chatgpt-flatpak/verification.json)
  records the source commit, workflow run, manifest checksum, signing fingerprint,
  both Flatpak commit IDs, and each upstream package URL, size, and SHA256. Its
  [detached signature](https://geoffbelknap.github.io/chatgpt-flatpak/verification.json.sig)
  authenticates that record using the project's signing key. This is a project
  build record, not an independent audit or a GitHub artifact attestation.

The signed record is updated with each release. Flatpak verifies its own signed
repository metadata automatically; manually checking the record is optional.

## Check the signing identity

The public key is committed in [repository-signing-key.pub](../keys/repository-signing-key.pub).
Its full fingerprint is:

```text
7E69D33E8B62E2A60B88E5FDB3B0349696F30CF1
```

With GnuPG installed, these commands download the public key and release record
into a temporary directory. They do not run downloaded scripts or change your
normal GnuPG keyring:

```sh
verification_dir=$(mktemp -d)
chmod 700 "$verification_dir"
curl -fsSL https://raw.githubusercontent.com/geoffbelknap/chatgpt-flatpak/main/keys/repository-signing-key.pub \
  -o "$verification_dir/public-key.asc"
gpg --homedir "$verification_dir" --show-keys --with-fingerprint "$verification_dir/public-key.asc"
```

Compare the displayed full fingerprint with the one above before importing:

```sh
gpg --homedir "$verification_dir" --import "$verification_dir/public-key.asc"
curl -fsSL https://geoffbelknap.github.io/chatgpt-flatpak/verification.json \
  -o "$verification_dir/verification.json"
curl -fsSL https://geoffbelknap.github.io/chatgpt-flatpak/verification.json.sig \
  -o "$verification_dir/verification.json.sig"
gpg --homedir "$verification_dir" --verify \
  "$verification_dir/verification.json.sig" "$verification_dir/verification.json"
```

Expect a **Good signature** from the fingerprint above. GnuPG may warn that the
key is not certified by another trusted key; compare its fingerprint yourself.
Follow the record's source commit and workflow links to inspect that release.
Compare its manifest SHA256 with the manifest at that exact commit, and its
upstream URLs and hashes with that manifest. The latest files on `main` may have
changed since a release was built.

To compare your installed release with the record, check its architecture and
commit ID against the matching entry under `flatpak_commits`:

```sh
flatpak info --user --show-arch com.openai.ChatGPT
flatpak info --user --show-commit com.openai.ChatGPT
```

The live record describes the latest release. If your installed commit differs,
check for an update before comparing again.

The public key identifies this project's signing authority, not OpenAI. A valid
signature means that authority signed the data, not that the data is harmless.
You still need to trust this project's GitHub account and automation. A compromised
account could replace both code and the public key shown on its website.

## Inspect installed permissions

```sh
flatpak info --user --show-permissions com.openai.ChatGPT
```

The package grants network, display, GPU, microphone/audio, Downloads access, and
selected desktop D-Bus interfaces, including Secret Service for login storage.
See [permissions and troubleshooting](troubleshooting.md) for details. A Flatpak
sandbox reduces host access; it does not make an application inherently safe.

The optional [native-access mode](troubleshooting.md#native-access-mode-experimental)
launches the application outside Flatpak, with normal user-level host access.
In that mode Flatpak provides verified delivery and updates, not application
isolation. Its host-command permission is intentionally absent from the default
manifest and must be explicitly enabled by the user.

## Current verification limits

The updater currently reads apt metadata over HTTPS without checking OpenAI's
apt Release signature. Checksums pin downloaded bytes, but our present automation
does not independently authenticate those checksums with OpenAI's signing key.
That verification is an outstanding security improvement.

Installation checks cover download verification, extraction, Zypak availability,
and library dependencies. They do not certify login, voice, GUI behavior, or
the safety of OpenAI's proprietary application and its server-side behavior.

For suspected tampering, stop using the package and contact the repository owner
through the GitHub profile linked from the project. Do not post credentials or
private keys in public issues.
