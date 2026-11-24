#!/usr/bin/env python3
"""Generate signed-remote installation files using the current GitHub context."""
import base64
import html
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


def generate(destination, repository, pages_url=None):
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
    (dest / "com.openai.ChatGPT.flatpakref").write_text(
        "[Flatpak Ref]\nName=com.openai.ChatGPT\nBranch=stable\n"
        f"Title=ChatGPT (community Flatpak)\nUrl={url}\nIsRuntime=false\n"
        "RuntimeRepo=https://dl.flathub.org/repo/flathub.flatpakrepo\n"
        f"GPGKey={encoded}\n", encoding="utf-8"
    )
    (dest / "chatgpt.flatpakrepo").write_text(
        f"[Flatpak Repo]\nTitle=ChatGPT (community Flatpak)\nUrl={url}\n"
        f"GPGKey={encoded}\n", encoding="utf-8"
    )
    command = f"flatpak install --user {url}com.openai.ChatGPT.flatpakref"
    (dest / "index.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>ChatGPT community Flatpak</title><h1>ChatGPT community Flatpak</h1>'
        '<p>Official app downloaded from OpenAI at install time. Packaging is community maintained.</p>'
        '<p><a href="com.openai.ChatGPT.flatpakref">Install ChatGPT</a></p>'
        f'<pre>{html.escape(command)}</pre>'
        f'<p><a href="https://github.com/{html.escape(repository)}">Source and instructions</a></p></html>\n',
        encoding="utf-8",
    )


if __name__ == "__main__":
    generate(sys.argv[1], os.environ["GITHUB_REPOSITORY"], os.environ.get("PAGES_URL"))
