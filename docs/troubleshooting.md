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

Flatpak changes the app's view of the host. Host command execution, local coding
toolchains, browser extensions/native messaging, global shortcuts, screen capture
and other agent/desktop integrations may require upstream portal support and are
not guaranteed by this package. No host-execution escape or broad home-directory
permission is included. Files in Downloads are available directly; app data lives
under `~/.var/app/com.openai.ChatGPT/`. The in-app updater cannot replace the
read-only application; use `flatpak update` for packaged releases.
