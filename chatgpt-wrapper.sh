#!/bin/sh
set -eu
export CHROME_DESKTOP=com.openai.ChatGPT.desktop
export ELECTRON_OZONE_PLATFORM_HINT=auto
if [ -n "${WAYLAND_DISPLAY:-}" ]; then
    set -- --enable-features=UseOzonePlatform,WaylandWindowDecorations \
        --ozone-platform-hint=auto --enable-wayland-ime "$@"
fi
exec zypak-wrapper /app/extra/chatgpt/ChatGPT "$@"
