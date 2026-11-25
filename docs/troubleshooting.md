# Permissions and troubleshooting

The app has Wayland/X11, IPC, GPU, PulseAudio (including microphone), network,
Downloads read/write access, notifications, tray integration, screensaver and
Secret Service access. Other files should be selected through a desktop portal.
The standard `org.freedesktop.portal.Desktop` interface is allowed by Flatpak;
the requested GlobalShortcuts bus name is also listed, but app support and the
desktop portal backend determine whether shortcuts work. A running Secret
Service provider, such as GNOME Keyring or compatible KWallet, is needed for
encrypted login persistence. The wrapper does not force a plaintext password store.

## Global shortcut prompts

On Wayland, ChatGPT can request a global shortcut through the desktop portal.
KDE may show a **Global Shortcuts Requested** dialog. A label such as
`electron-accelerator-…` is an internal Electron shortcut identifier.

A warning beside the requested combination can indicate an existing binding.
For example, KDE may already use **Meta+Alt+P** to move keyboard focus between
panels. Choose an unused combination and accept, or cancel to decline the
shortcut request. The permission covers the specific global shortcut. Existing
bindings can be reviewed in KDE's shortcut settings.

## Wayland and XWayland

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

## Local files and host tools

The default launcher runs inside Flatpak. It exposes Downloads and portal-selected
files, while commands run against the Flatpak runtime. Granting additional folders
does not make the host's installed tools available inside that runtime.

For a selected project folder, use Flatseal or a directory-specific filesystem
override. For native user-level access, use the mode below.

## Native-access mode (experimental)

This runs OpenAI's unmodified application on the host as your normal user, using
Flatpak as the verified installation and update mechanism. The application and
its child processes are **outside the Flatpak sandbox**, with normal user access
to host files, commands, devices, and desktop services. It does not grant root
privileges. OpenAI's own application approval controls still apply.

After updating the package, fully quit ChatGPT before enabling this mode:

```sh
flatpak override --user --talk-name=org.freedesktop.Flatpak \
  --env=CHATGPT_NATIVE_ACCESS=1 com.openai.ChatGPT
flatpak run com.openai.ChatGPT
```

The host-command permission permits unsandboxed execution as your user. Enable
it only if you trust the application with the same access as its native package.
The launcher uses the exact installed deployment for its binary and resources,
and keeps the existing profile under `~/.var/app/com.openai.ChatGPT/` so switching
modes does not intentionally switch accounts. Host tools and the app's use of
`~/.codex` can interact with your native CLI configuration and work data.

This mode needs the native application's system libraries on the host. It does
not install them or layer packages onto the immutable OS. Library availability
was checked on Bazzite; other systems may report missing libraries. Interactive
login, browser integration, and local agent behavior still need testing in this
mode. It does not enable features absent from OpenAI's Linux application.

To return to the default sandbox, quit ChatGPT and run:

```sh
flatpak override --user --no-talk-name=org.freedesktop.Flatpak \
  --unset-env=CHATGPT_NATIVE_ACCESS com.openai.ChatGPT
```

In either mode, use `flatpak update` for packaged releases. The launcher does not
patch upstream application files or disable Electron's own sandbox.
