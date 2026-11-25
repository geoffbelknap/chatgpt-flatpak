#!/bin/sh
set -eu
export CHROME_DESKTOP=com.openai.ChatGPT.desktop
export ELECTRON_OZONE_PLATFORM_HINT=auto
if [ -n "${WAYLAND_DISPLAY:-}" ]; then
    set -- --enable-features=UseOzonePlatform,WaylandWindowDecorations \
        --ozone-platform-hint=auto --enable-wayland-ime "$@"
fi
if [ "${CHATGPT_NATIVE_ACCESS:-0}" = 1 ]; then
    # This mode is explicitly enabled together with the Flatpak host-command
    # permission. Use this instance's deployment, not a mutable "current" link,
    # so a running app keeps its matching resources across package updates.
    app_path=$(sed -n 's/^app-path=//p' /.flatpak-info)
    case "$app_path" in
        /*) ;;
        *) echo 'Cannot determine the installed ChatGPT deployment' >&2; exit 1 ;;
    esac
    # Keep the existing Flatpak profile while using the host session, toolchain,
    # and normal user permissions. Never export Flatpak's library search path.
    exec flatpak-spawn --host --watch-bus --directory="$HOME" \
        --env="CHROME_DESKTOP=$CHROME_DESKTOP" \
        --env="ELECTRON_OZONE_PLATFORM_HINT=$ELECTRON_OZONE_PLATFORM_HINT" \
        --env="XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-$HOME/.var/app/com.openai.ChatGPT/config}" \
        --env="XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.var/app/com.openai.ChatGPT/data}" \
        --env="XDG_CACHE_HOME=${XDG_CACHE_HOME:-$HOME/.var/app/com.openai.ChatGPT/cache}" \
        "$app_path/extra/chatgpt/ChatGPT" "$@"
fi
exec zypak-wrapper /app/extra/chatgpt/ChatGPT "$@"
