#!/bin/sh
set -eu
destination=${1:?Usage: restore-pages.sh DESTINATION}
mkdir -p "$destination"
if git ls-remote --exit-code origin refs/heads/gh-pages > /dev/null; then
    git fetch --depth=1 origin gh-pages
    git archive FETCH_HEAD | tar -xf - -C "$destination"
else
    status=$?
    if [ "$status" -ne 2 ]; then
        echo 'Cannot inspect gh-pages; refusing to reset repository history' >&2
        exit "$status"
    fi
fi
