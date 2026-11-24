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
    if [ "$#" -ne 1 ] || [ ! -f "$1" ]; then
        echo 'Expected exactly one Debian data archive' >&2
        exit 1
    fi
    mkdir root
    tar -xf "$1" -C root --no-same-owner --no-same-permissions
)
root=$work/root
test -x "$root/usr/lib/chatgpt/ChatGPT"
test -f "$root/usr/share/applications/chatgpt.desktop"
test -f "$root/usr/share/pixmaps/chatgpt.png"
mkdir -p export/share/applications export/share/icons/hicolor/1024x1024/apps \
    export/share/icons/hicolor/scalable/apps
# Rewrite every action Exec too, and remove host-specific TryExec entries.
sed -e 's|^Exec=.*|Exec=chatgpt %U|' \
    -e 's|^Icon=.*|Icon=com.openai.ChatGPT|' \
    -e 's|^Name=.*|Name=ChatGPT (Unofficial)|' \
    -e 's|^Comment=.*|Comment=Unofficial community Flatpak packaging of the official ChatGPT app|' \
    -e '/^TryExec=/d' \
    "$root/usr/share/applications/chatgpt.desktop" \
    > export/share/applications/com.openai.ChatGPT.desktop
cp "$root/usr/share/pixmaps/chatgpt.png" \
    export/share/icons/hicolor/1024x1024/apps/com.openai.ChatGPT.png
# Replace the build-time catalog placeholder at its exact export path. Embed the
# original PNG bytes in a self-contained SVG so theme lookup can select the real
# icon at any requested size without an image conversion dependency in the runtime.
{
    printf '%s' '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1024" height="1024" viewBox="0 0 1024 1024"><image width="1024" height="1024" xlink:href="data:image/png;base64,'
    base64 --wrap=0 "$root/usr/share/pixmaps/chatgpt.png"
    printf '%s\n' '"/></svg>'
} > export/share/icons/hicolor/scalable/apps/com.openai.ChatGPT.svg
mv "$root/usr/lib/chatgpt" ./chatgpt
# No maintainer scripts are executed and no apt configuration is installed.
rm -f chatgpt.deb
