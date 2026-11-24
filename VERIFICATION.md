# Verification performed on 2026-11-24

- Downloaded both versioned OpenAI 26.1120.50957 Debian packages and computed
  SHA256 locally. Both match the official apt indexes and manifest pins.
- Built and exported the x86_64 Flatpak using the actual Freedesktop SDK and
  Electron2 BaseApp 26.08. The extraction ar executable links only to libc;
  it does not require SDK-only libbfd or libiberty shared libraries.
- Installed that build in an isolated temporary Flatpak installation. Flatpak
  downloaded and verified extra-data and successfully ran the extraction hook.
  The installed main binary, desktop export, icon, Zypak and archive cleanup
  were checked. The main executable has no missing runtime library dependencies.
- Extracted the real ARM64 package with the same hook and confirmed its main
  executable is AArch64. A native ARM64 build/run was not performed locally;
  the GitHub workflow builds and installs it on a native ARM64 runner.
- Exercised publication with the real x64 repository and a synthetic ARM ref
  fixture: merge, repeated publication, app/summary signing, AppStream generation,
  `.flatpakref` generation, public-key export and signature verification passed.
  The fixture tests publishing logic, not ARM execution. Disposable test keys
  and generated repositories are outside the source deliverable.
- Actionlint 1.7.12, ShellCheck, YAML parsing, desktop-file-validate,
  AppStream XML validation and all four Python test cases passed.

Expected metadata notices: the icon is not available at build/export time,
because it comes from the user's extra-data installation. AppStream reports an
informational short-description notice; the desktop validator notes that the
upstream Utility/Development categories can appear in multiple menu sections.

GitHub-hosted workflow execution, Pages deployment and a native ARM64 build
have not been run from this workspace. Interactive GUI/login/voice/portal
behavior requires desktop and account testing. Running the raw Electron binary
outside Zypak is not a supported launch path; the installed entry point is
`/app/bin/chatgpt`, which invokes `zypak-wrapper`.
