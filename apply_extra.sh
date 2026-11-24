#!/bin/sh
# Flatpak invokes this offline with cwd=/app/extra; only that directory is writable.
set -eu
umask 022
work=$(mktemp -d ./unpack.XXXXXX)
trap 'rm -rf "$work"' EXIT HUP INT TERM
archive=$(pwd)/chatgpt.deb
(
    cd "$work"
    ar x "$archive"
    set -- data.tar.*
    [ "$#" -eq 1 ] && [ -f "$1" ] || {
        echo 'Expected exactly one Debian data archive' >&2
        exit 1
    }
    mkdir root
    tar -xf "$1" -C root --no-same-owner --no-same-permissions
)
root=$work/root
test -x "$root/usr/lib/chatgpt/ChatGPT"
test -f "$root/usr/share/applications/chatgpt.desktop"
test -f "$root/usr/share/pixmaps/chatgpt.png"
mkdir -p export/share/applications export/share/icons/hicolor/1024x1024/apps
# Rewrite every action Exec too, and remove host-specific TryExec entries.
sed -e 's|^Exec=.*|Exec=chatgpt %U|' \
    -e 's|^Icon=.*|Icon=com.openai.ChatGPT|' \
    -e '/^TryExec=/d' \
    "$root/usr/share/applications/chatgpt.desktop" \
    > export/share/applications/com.openai.ChatGPT.desktop
cp "$root/usr/share/pixmaps/chatgpt.png" \
    export/share/icons/hicolor/1024x1024/apps/com.openai.ChatGPT.png
mv "$root/usr/lib/chatgpt" ./chatgpt
# No maintainer scripts are executed and no apt configuration is installed.
rm -f chatgpt.deb
