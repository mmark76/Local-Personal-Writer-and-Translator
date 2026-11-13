import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile


@unittest.skipUnless(os.name == "nt", "Windows installer")
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.setup = self.root / "setup"
        self.setup.mkdir()
        self.destination = self.root / "destination"
        self.destination.mkdir()
        source = Path(__file__).resolve().parents[1] / "installer" / "Install-Writer.ps1"
        shutil.copy2(source, self.setup / source.name)

    def run_setup(self):
        return subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(self.setup / "Install-Writer.ps1"), "-VerifyDestination", str(self.destination)],
            capture_output=True, text=True, timeout=30,
        )

    def test_installs_without_overwriting_existing_files(self):
        with zipfile.ZipFile(self.setup / "payload.zip", "w") as archive:
            archive.writestr("Writer-Translator/Start Local Writer.bat", "launcher")
            archive.writestr("Writer-Translator/app/server.py", "server")
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        personal = self.destination / "Writer-Translator" / "personal.txt"
        personal.write_text("keep", encoding="utf-8")
        self.assertNotEqual(self.run_setup().returncode, 0)
        self.assertEqual(personal.read_text(encoding="utf-8"), "keep")

    def test_rejects_archive_path_traversal(self):
        with zipfile.ZipFile(self.setup / "payload.zip", "w") as archive:
            archive.writestr("Writer-Translator/../../escape.txt", "bad")
        self.assertNotEqual(self.run_setup().returncode, 0)
        self.assertFalse((self.root / "escape.txt").exists())
        self.assertFalse((self.destination / "Writer-Translator").exists())
