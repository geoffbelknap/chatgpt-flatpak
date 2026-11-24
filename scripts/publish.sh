#!/bin/sh
set -eu
destination=${1:?Usage: publish.sh DESTINATION INCOMING}
incoming=${2:?Usage: publish.sh DESTINATION INCOMING}
: "${GPG_KEY_ID:?Signing fingerprint required}"
: "${GITHUB_REPOSITORY:?owner/repo required}"
if [ ! -f "$destination/config" ]; then
    ostree --repo="$destination" init --mode=archive-z2
fi
for arch in x86_64 aarch64; do
    staging=$(mktemp -d)
    tar -xf "$incoming/repo-$arch.tar" -C "$staging"
    ref="app/com.openai.ChatGPT/$arch/stable"
    ostree --repo="$destination" pull-local "$staging" "$ref"
    # Signing here keeps private keys out of build jobs and pull requests.
    commit=$(ostree --repo="$destination" rev-parse "$ref")
    ostree --repo="$destination" gpg-sign "$commit" "$GPG_KEY_ID"
    rm -rf "$staging"
done
flatpak build-update-repo --gpg-sign="$GPG_KEY_ID" "$destination"
gpg --batch --export "$GPG_KEY_ID" > "$destination/repo.gpg"
python3 scripts/generate-metadata.py "$destination"
touch "$destination/.nojekyll"
