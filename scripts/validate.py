#!/usr/bin/env python3
"""Offline checks for publication-critical manifest properties and YAML syntax."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
import yaml

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL_ROOT = "https://persistent.oaistatic.com/codex-app-prod/linux/deb"


def validate():
    manifest = yaml.safe_load((ROOT / "com.openai.ChatGPT.yml").read_text())
    assert manifest["app-id"] == "com.openai.ChatGPT"
    assert manifest["runtime-version"] == manifest["base-version"]
    assert manifest["default-branch"] == "stable"
    sources = [s for m in manifest["modules"] for s in m.get("sources", [])]
    extra = [s for s in sources if s["type"] == "extra-data"]
    assert len(extra) == 2
    assert {tuple(s["only-arches"]) for s in extra} == {("x86_64",), ("aarch64",)}
    for source in sources:
        if "path" in source:
            assert (ROOT / source["path"]).is_file(), source["path"]
        if "url" in source:
            assert urlsplit(source["url"]).scheme == "https"
        if source["type"] != "extra-data":
            assert not source.get("url", "").endswith(".deb"), "Binary must be extra-data"
    for source in extra:
        assert source["filename"] == "chatgpt.deb"
        assert source["url"].startswith(OFFICIAL_ROOT + "/pool/")
        assert re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
        assert source["sha256"] != "0" * 64
        assert isinstance(source["size"], int) and source["size"] > 1_000_000
        assert source["x-checker-data"] == {
            "type": "debian-repo", "package-name": "chatgpt", "root": OFFICIAL_ROOT,
            "dist": "stable", "component": "main",
        }
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        # BaseLoader preserves the GitHub Actions `on` key (YAML 1.2).
        workflow = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        assert "on" in workflow and "jobs" in workflow, path
    for path in [ROOT / "apply_extra.sh", ROOT / "chatgpt-wrapper.sh", *ROOT.glob("scripts/*.sh")]:
        assert path.stat().st_mode & 0o111, f"Not executable: {path}"
    ET.parse(ROOT / "com.openai.ChatGPT.metainfo.xml")
    print("Manifest, workflows, source pins, XML and executable modes validated")


if __name__ == "__main__":
    validate()
