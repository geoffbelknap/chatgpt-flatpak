#!/bin/sh
set -eu
: "${RUNNER_TEMP:?GitHub runner temporary directory required}"
keyring=$RUNNER_TEMP/chatgpt-gnupg
if [ -d "$keyring" ]; then
    GNUPGHOME="$keyring" gpgconf --kill all || true
    rm -rf -- "$keyring"
fi
printf 'GNUPGHOME=\n' >> "${GITHUB_ENV:?}"
