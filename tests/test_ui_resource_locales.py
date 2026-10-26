"""Guard against AAPT stripping regional translations of the selected languages."""
import ast
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AAPT2 = os.environ.get('AAPT2_BIN') or shutil.which('aapt2')


def resource_locales():
    gradle = (ROOT / 'TMessagesProj/build.gradle').read_text()
    languages = ast.literal_eval(re.search(r'def bundledUiLanguages = (\[[^\n]+\])', gradle)[1])
    regions = ast.literal_eval(re.search(r'def bundledUiResourceLocales = bundledUiLanguages \+ (\[[^\n]+\])', gradle)[1])
    return languages, regions


class UiResourceLocaleTests(unittest.TestCase):
    def test_every_selected_regional_resource_directory_is_retained(self):
        languages, regions = resource_locales()
        for path in (ROOT / 'TMessagesProj/src/main/res').glob('values-*'):
            match = re.fullmatch(r'values-([a-z]{2})-r([A-Z]{2})', path.name)
            if match and match[1] in languages:
                self.assertIn(path.name[len('values-'):], regions, path.name)

    @unittest.skipUnless(AAPT2, 'Set AAPT2_BIN to run the real resource-compiler regression')
    def test_real_aapt_keeps_russian_and_ukrainian_settings(self):
        languages, regions = resource_locales()
        with tempfile.TemporaryDirectory(prefix='ui-locales-') as directory:
            root = Path(directory)
            for name, text in [('values', 'General'), ('values-ru-rRU', 'Основные'), ('values-uk-rUA', 'Основні')]:
                path = root / 'res' / name
                path.mkdir(parents=True)
                (path / 'strings.xml').write_text('<resources><string name="section">' + text + '</string></resources>')
            manifest = root / 'AndroidManifest.xml'
            manifest.write_text('<manifest package="org.example.localecheck"><application /></manifest>')
            compiled = root / 'compiled.zip'
            apk = root / 'test.apk'
            subprocess.run([AAPT2, 'compile', '--dir', str(root / 'res'), '-o', str(compiled)], check=True, capture_output=True)
            subprocess.run([AAPT2, 'link', '--manifest', str(manifest), '-c', ','.join(languages + regions), '-o', str(apk), str(compiled)], check=True, capture_output=True)
            configs = subprocess.check_output([AAPT2, 'dump', 'configurations', str(apk)], text=True).splitlines()
            self.assertIn('ru-rRU', configs)
            self.assertIn('uk-rUA', configs)
            values = subprocess.check_output([AAPT2, 'dump', 'resources', str(apk)], text=True)
            self.assertIn('Основные', values)
            self.assertIn('Основні', values)


if __name__ == '__main__':
    unittest.main()
