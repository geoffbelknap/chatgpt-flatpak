#!/usr/bin/env python3
"""Generate signed-remote installation files using the current GitHub context."""
import base64
import html
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import subprocess
from urllib.parse import urlsplit
import yaml

ROOT = Path(__file__).resolve().parent.parent


def generate(destination, repository, pages_url=None, commits=None):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Expected GitHub owner/repository")
    owner, name = repository.split("/")
    url = (pages_url or f"https://{owner.lower()}.github.io/{name}/").rstrip("/") + "/"
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.netloc or any(c in url for c in "\r\n"):
        raise ValueError("PAGES_URL must be an HTTPS URL")
    dest = Path(destination)
    key = (dest / "repo.gpg").read_bytes()
    if not key:
        raise ValueError("Refusing to publish without a GPG public key")
    encoded = base64.b64encode(key).decode("ascii")
    commit = os.environ.get("GITHUB_SHA")
    run_id = os.environ.get("GITHUB_RUN_ID")
    source_url = f"https://github.com/{repository}"
    guide_url = f"{source_url}/blob/{commit or 'main'}/docs/security.md"
    manifest_bytes = (ROOT / "com.openai.ChatGPT.yml").read_bytes()
    manifest = yaml.safe_load(manifest_bytes)
    packages = [
        {"architectures": s["only-arches"], "url": s["url"],
         "size": s["size"], "sha256": s["sha256"]}
        for module in manifest["modules"] for s in module.get("sources", [])
        if s["type"] == "extra-data"
    ]
    record = {
        "schema_version": 1, "app_id": "com.openai.ChatGPT",
        "source_repository": source_url, "source_commit": commit,
        "workflow_run": f"{source_url}/actions/runs/{run_id}" if run_id else None,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "flatpak_commits": commits or {},
        "signing_fingerprint": (ROOT / "keys/fingerprint.txt").read_text().strip(),
        "upstream_packages": packages,
    }
    (dest / "verification.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    (dest / "com.openai.ChatGPT.flatpakref").write_text(
        "[Flatpak Ref]\nName=com.openai.ChatGPT\nBranch=stable\n"
        f"Title=ChatGPT (Unofficial Flatpak)\nUrl={url}\nIsRuntime=false\n"
        "RuntimeRepo=https://dl.flathub.org/repo/flathub.flatpakrepo\n"
        f"GPGKey={encoded}\n", encoding="utf-8"
    )
    (dest / "chatgpt.flatpakrepo").write_text(
        f"[Flatpak Repo]\nTitle=ChatGPT (Unofficial Flatpak)\nUrl={url}\n"
        f"GPGKey={encoded}\n", encoding="utf-8"
    )
    command = f"flatpak install --user {url}com.openai.ChatGPT.flatpakref"
    (dest / "index.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>ChatGPT Flatpak (Unofficial)</title><h1>ChatGPT Flatpak (Unofficial)</h1>'
        '<p>Unofficial community packaging. Not affiliated with, endorsed by, or supported by OpenAI.</p>'
        '<p>The official application is downloaded directly from OpenAI and checked by SHA256 at installation.</p>'
        '<p><a href="com.openai.ChatGPT.flatpakref">Install ChatGPT</a></p>'
        f'<pre>{html.escape(command)}</pre>'
        f'<p><a href="{html.escape(guide_url, quote=True)}">Verify this package</a> · '
        '<a href="verification.json">Signed build record</a> '
        '(<a href="verification.json.sig">signature</a>)</p>'
        f'<p><a href="https://github.com/{html.escape(repository)}">Source and instructions</a></p></html>\n',
        encoding="utf-8",
    )


if __name__ == "__main__":
    destination = sys.argv[1]
    commits = {
        arch: subprocess.check_output([
            "ostree", f"--repo={destination}", "rev-parse",
            f"app/com.openai.ChatGPT/{arch}/stable",
        ], text=True).strip()
        for arch in ("x86_64", "aarch64")
    }
    generate(destination, os.environ["GITHUB_REPOSITORY"], os.environ.get("PAGES_URL"), commits)
