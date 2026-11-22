import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import unittest


RENDERER = Path(__file__).resolve().parents[1] / "launchd/render_plist.py"


class LaunchAgentTemplateTests(unittest.TestCase):
    def test_installs_plist_with_checkout_home_and_custom_label(self):
        with tempfile.TemporaryDirectory(prefix="Brain & Notes ") as directory:
            home = Path(directory)
            label = "example.brain-sync"
            destination = home / f"{label}.plist"
            destination.write_bytes(b"old plist")
            subprocess.run([sys.executable, str(RENDERER), str(destination)], cwd=home,
                           env={**os.environ, "HOME": str(home)}, check=True, capture_output=True)
            agent = plistlib.loads(destination.read_bytes())
            self.assertEqual(agent["Label"], label)
            self.assertEqual(agent["ProgramArguments"], [str(RENDERER.parents[1] / "bin/brain"), "sync"])
            self.assertEqual(agent["StandardOutPath"], str(home / "Library/Logs/brain-sync.log"))
            self.assertEqual(agent["StandardErrorPath"], agent["StandardOutPath"])
            self.assertEqual(agent["StartCalendarInterval"], [{"Minute": minute} for minute in (0, 15, 30, 45)])

    def test_invalid_template_preserves_preexisting_plist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            renderer = root / RENDERER.name
            shutil.copyfile(RENDERER, renderer)
            (root / "com.vladilen.brain-sync.plist").write_bytes(b"invalid template")
            destination = root / "example.brain-sync.plist"
            original = plistlib.dumps({"Label": "example.brain-sync"})
            destination.write_bytes(original)
            result = subprocess.run([sys.executable, str(renderer), str(destination)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(destination.read_bytes(), original)
