#!/bin/sh
set -eu
: "${GPG_PRIVATE_KEY:?Set the GPG_PRIVATE_KEY Actions secret}"
: "${GPG_KEY_ID:?Set the GPG_KEY_ID Actions variable to the signing fingerprint}"
expected=$(tr -d '\r\n' < keys/fingerprint.txt)
if [ "$GPG_KEY_ID" != "$expected" ]; then
    echo 'Signing fingerprint does not match the committed public identity' >&2
    exit 1
fi
export GNUPGHOME="${RUNNER_TEMP:?}/chatgpt-gnupg"
mkdir -p "$GNUPGHOME"
chmod 700 "$GNUPGHOME"
printf '%s\n' "$GPG_PRIVATE_KEY" | gpg --batch --import
gpg --batch --list-secret-keys "$GPG_KEY_ID" > /dev/null
printf 'GNUPGHOME=%s\n' "$GNUPGHOME" >> "${GITHUB_ENV:?}"
