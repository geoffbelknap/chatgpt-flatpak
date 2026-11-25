# ChatGPT Flatpak (Unofficial)

Community Flatpak packaging of [OpenAI's official Linux desktop app](https://learn.chatgpt.com/docs/linux/linux-app)
for x86_64 and ARM64. Works with immutable desktops such as Bazzite, Fedora
Silverblue, and Kinoite without layering packages onto the operating system.

**This is an unofficial community package, not affiliated with, endorsed by, or
supported by OpenAI.** The app is proprietary; the packaging is
[MIT licensed](LICENSE).

## Install

Run as your regular user:

```sh
flatpak install --user https://geoffbelknap.github.io/chatgpt-flatpak/com.openai.ChatGPT.flatpakref
```

Open **ChatGPT** from your applications menu, or run:

```sh
flatpak run com.openai.ChatGPT
```

On Wayland, your desktop may ask to approve a global keyboard shortcut. This is
expected. If the requested shortcut conflicts with an existing one, choose another
combination or cancel the request. See [shortcut prompts](docs/troubleshooting.md#global-shortcut-prompts).

## Updates

Use your Flatpak software manager, or run:

```sh
flatpak update --user
```

New OpenAI releases are checked daily and published after both architecture
builds and installation checks pass.

## How it works

Flatpak downloads the official `.deb` directly from OpenAI at installation and
checks its SHA256. This project hosts the Flatpak packaging and signed update
metadata. OpenAI's application binaries stay on OpenAI's servers until you install
them. See [Verify this package](docs/security.md) for the source, build records,
signing fingerprint, and checks you can perform yourself.

The package grants Wayland/X11, GPU, microphone/audio, network, and Downloads
access. Some host integrations may be limited by the sandbox; see
[permissions and troubleshooting](docs/troubleshooting.md).

For normal user-level access to host files and tools, an experimental
[native-access mode](docs/troubleshooting.md#native-access-mode-experimental)
uses Flatpak for installation and updates while running the app outside its sandbox.

For build instructions and checks, see [Contributing](CONTRIBUTING.md).
