"""Updater-removal regression checks; no Android build or real account required."""

import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "TMessagesProj/src/main"


class NoAppUpdaterTests(unittest.TestCase):
    def test_install_permission_is_absent(self):
        manifest = ET.parse(MAIN / "AndroidManifest.xml")
        name = "{http://schemas.android.com/apk/res/android}name"
        tools_node = "{http://schemas.android.com/tools}node"
        permissions = {
            node.get(name) for node in manifest.iter("uses-permission")
            if node.get(tools_node) != "remove"
        }
        self.assertNotIn("android.permission.REQUEST_INSTALL_PACKAGES", permissions)

    def test_updater_implementations_and_installer_calls_are_absent(self):
        removed_classes = (
            "GitHubUpdater", "UpdaterSheet", "UpdateSheet", "UpdateHelper",
            "BlockingUpdateView", "UpdateAppAlertDialog", "UpdateLayout",
        )
        forbidden = re.compile(
            r"\b(?:" + "|".join(removed_classes) + r")\b"
            r"|ACTION_INSTALL_PACKAGE|ACTION_MANAGE_UNKNOWN_APP_SOURCES"
            r"|canRequestPackageInstalls\s*\(|new\s+(?:TLRPC\.)?TL_help_getAppUpdate\s*\("
        )
        for directory in (MAIN / "java", MAIN / "kotlin"):
            for path in directory.rglob("*"):
                if path.suffix not in (".java", ".kt"):
                    continue
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertIsNone(forbidden.search(path.read_text()))

    @unittest.skipUnless(shutil.which("java"), "Java source launcher is required")
    def test_apk_detection_without_blocking_regular_files(self):
        # Execute the actual production helper, not a duplicate of its conditions.
        source = (MAIN / "java/org/telegram/messenger/AndroidUtilities.java").read_text()
        start = source.index("    private static boolean isApkFile(")
        end = source.index("\n    }", start) + len("\n    }")
        helper = source[start:end]
        harness = """
import java.io.File;
import java.util.Locale;
class ApkDetectionCheck {
HELPER
    static void check(boolean expected, File file, String name, String mime) {
        if (isApkFile(file, name, mime) != expected) throw new AssertionError(name);
    }
    public static void main(String[] args) {
        check(true, null, "client.apk", null);
        check(true, null, "CLIENT.APK", "application/octet-stream");
        check(true, new File("cached.apk"), "download", null);
        check(true, null, "download", "application/vnd.android.package-archive");
        check(true, null, null, "APPLICATION/VND.ANDROID.PACKAGE-ARCHIVE");
        check(false, null, null, null);
        check(false, new File("cached.pdf"), "document.pdf", "application/pdf");
        check(false, new File("photo.jpg"), "photo.jpg", "image/jpeg");
        check(false, null, "archive.zip", "application/zip");
        check(false, null, "notes.apk.txt", "text/plain");
    }
}
""".replace("HELPER", helper)
        with tempfile.TemporaryDirectory(prefix="apk-detection-") as directory:
            path = Path(directory) / "ApkDetectionCheck.java"
            path.write_text(harness)
            subprocess.run(["java", str(path)], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
