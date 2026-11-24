import importlib.util
import hashlib
import json
import os
from pathlib import Path
from unittest.mock import patch
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("metadata", ROOT / "scripts/generate-metadata.py")
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


class PackagingTests(unittest.TestCase):
    def test_wrapper_preserves_arguments_and_selects_wayland(self):
        with tempfile.TemporaryDirectory() as tmp:
            mock = Path(tmp) / "zypak-wrapper"
            mock.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
            mock.chmod(0o755)
            env = {**os.environ, "PATH": f"{tmp}:{os.environ['PATH']}"}
            for wayland in ("", "wayland-0"):
                env["WAYLAND_DISPLAY"] = wayland
                result = subprocess.check_output(
                    [str(ROOT / "chatgpt-wrapper.sh"), "--ozone-platform=x11", "file with spaces"],
                    env=env, text=True,
                ).splitlines()
                self.assertEqual(result[0], "/app/extra/chatgpt/ChatGPT")
                self.assertEqual(result[-2:], ["--ozone-platform=x11", "file with spaces"])
                self.assertEqual("--enable-wayland-ime" in result, bool(wayland))

    def test_extracts_deb_and_does_not_run_maintainer_scripts(self):
        for compression in ("xz", "gz"):
            with self.subTest(compression=compression), tempfile.TemporaryDirectory() as tmp:
                cwd = Path(tmp)
                payload = cwd / "fixture"
                app = payload / "usr/lib/chatgpt/ChatGPT"
                desktop = payload / "usr/share/applications/chatgpt.desktop"
                icon = payload / "usr/share/pixmaps/chatgpt.png"
                for path in (app, desktop, icon):
                    path.parent.mkdir(parents=True, exist_ok=True)
                app.write_text("#!/bin/sh\nexit 0\n")
                app.chmod(0o755)
                desktop.write_text("[Desktop Entry]\nName=ChatGPT\nExec=/usr/bin/chatgpt %U\nIcon=chatgpt\nTryExec=/usr/bin/chatgpt\n")
                icon.write_bytes(b"fixture icon")
                (cwd / "debian-binary").write_text("2.0\n")
                control = cwd / "control"
                control.mkdir()
                (control / "postinst").write_text(f"#!/bin/sh\ntouch {cwd}/EXECUTED\n")
                subprocess.run(["tar", "-cJf", str(cwd / "control.tar.xz"), "-C", str(control), "."], check=True)
                data = f"data.tar.{compression}"
                flag = "-cJf" if compression == "xz" else "-czf"
                subprocess.run(["tar", flag, str(cwd / data), "-C", str(payload), "."], check=True)
                subprocess.run(["ar", "rc", "chatgpt.deb", "debian-binary", "control.tar.xz", data], cwd=cwd, check=True)
                subprocess.run([str(ROOT / "apply_extra.sh")], cwd=cwd, check=True)
                self.assertTrue((cwd / "chatgpt/ChatGPT").is_file())
                self.assertFalse((cwd / "chatgpt.deb").exists())
                self.assertFalse((cwd / "EXECUTED").exists())
                self.assertEqual(list(cwd.glob("unpack.*")), [])
                exported = (cwd / "export/share/applications/com.openai.ChatGPT.desktop").read_text()
                self.assertIn("Exec=chatgpt %U", exported)
                self.assertIn("Icon=com.openai.ChatGPT", exported)
                self.assertIn("Name=ChatGPT (Unofficial)", exported)
                self.assertNotIn("TryExec", exported)

    def test_metadata_has_real_url_and_embedded_trust_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            (dest / "repo.gpg").write_bytes(b"test-public-key")
            metadata.generate(dest, "Example/chatgpt-flatpak")
            ref = (dest / "com.openai.ChatGPT.flatpakref").read_text()
            self.assertIn("Url=https://example.github.io/chatgpt-flatpak/", ref)
            self.assertIn("Branch=stable", ref)
            self.assertIn("GPGKey=dGVzdC1wdWJsaWMta2V5", ref)
            metadata.generate(dest, "Example/chatgpt-flatpak", "https://apps.example.com/")
            self.assertIn("Url=https://apps.example.com/", (dest / "com.openai.ChatGPT.flatpakref").read_text())

    def test_metadata_rejects_missing_key_or_insecure_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                metadata.generate(tmp, "Example/repo")
            (Path(tmp) / "repo.gpg").write_bytes(b"key")
            with self.assertRaises(ValueError):
                metadata.generate(tmp, "Example/repo", "http://example.com/")

    def test_release_record_links_to_exact_source_and_ci_run(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "GITHUB_SHA": "a" * 40, "GITHUB_RUN_ID": "12345"
        }):
            dest = Path(tmp)
            (dest / "repo.gpg").write_bytes(b"test-public-key")
            commits = {"x86_64": "b" * 64, "aarch64": "c" * 64}
            metadata.generate(dest, "geoffbelknap/chatgpt-flatpak", commits=commits)
            record = json.loads((dest / "verification.json").read_text())
            self.assertEqual(record["source_commit"], "a" * 40)
            self.assertEqual(record["flatpak_commits"], commits)
            self.assertEqual(record["workflow_run"],
                             "https://github.com/geoffbelknap/chatgpt-flatpak/actions/runs/12345")
            self.assertEqual(record["manifest_sha256"],
                             hashlib.sha256((ROOT / "com.openai.ChatGPT.yml").read_bytes()).hexdigest())
            self.assertEqual({p["architectures"][0] for p in record["upstream_packages"]},
                             {"x86_64", "aarch64"})
            self.assertEqual(record["signing_fingerprint"], (ROOT / "keys/fingerprint.txt").read_text().strip())
            page = (dest / "index.html").read_text()
            self.assertIn("Unofficial", page)
            self.assertIn("Not affiliated with, endorsed by, or supported by OpenAI.", page)
            self.assertIn(f"/blob/{'a' * 40}/docs/security.md", page)
            self.assertIn("verification.json.sig", page)


if __name__ == "__main__":
    unittest.main()
