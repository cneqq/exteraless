"""Distribution contracts for the fully plugin-free edition."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "TMessagesProj/src/main/java"


def test_plugin_runtime_sources_are_absent():
    for path in (
        JAVA / "app/exteraless/plugins",
        JAVA / "com/exteragram/messenger/plugins",
        ROOT / "TMessagesProj/src/main/python",
    ):
        assert not any(p.is_file() for p in path.rglob("*")), f"Plugin runtime remains: {path.relative_to(ROOT)}"


def test_app_has_no_plugin_runtime_or_ui_entry_points():
    forbidden = re.compile(r"app\.exteraless\.plugins|com\.chaquo\.python|MainMenuItem\.PLUGINS|TOGGLE_SAFE_MODE")
    hits = []
    for path in JAVA.rglob("*.java"):
        if forbidden.search(path.read_text(encoding="utf-8", errors="replace")):
            hits.append(str(path.relative_to(ROOT)))
    assert not hits, "Plugin entry points remain: " + ", ".join(hits)


def test_build_has_no_plugin_engine_dependencies():
    text = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in (
        "build.gradle", "settings.gradle", "TMessagesProj/build.gradle", ".gitmodules"))
    for token in ("com.chaquo.python", "com.aliucord:Aliuhook", "org.mvel:mvel2", "com.linkedin.dexmaker", "TMessagesProj/chaquopy"):
        assert token not in text, f"Plugin build dependency remains: {token}"


def test_personal_build_uses_the_same_stable_package_as_main():
    workflow = (ROOT / '.github/workflows/personal-apk.yml').read_text(encoding='utf-8')
    gradle = (ROOT / 'TMessagesProj/build.gradle').read_text(encoding='utf-8')
    assert re.search(r'^\s+PERSONAL_APPLICATION_ID: com\.freezgram\.app\s*$', workflow, re.M)
    assert "expected_package = 'com.freezgram.app'" in workflow
    assert "System.getenv('PERSONAL_APPLICATION_ID')" in gradle


def test_manifest_and_shortcuts_have_no_plugin_entry_points():
    manifest = (ROOT / "TMessagesProj/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
    shortcuts = (ROOT / "TMessagesProj/src/main/res/xml/shortcuts.xml").read_text(encoding="utf-8")
    for suffix in (".plugin", ".elyx", ".eaf"):
        assert suffix not in manifest
    assert "quick_safe_mode" not in shortcuts


@pytest.mark.skipif(not shutil.which('java'), reason='Java source launcher required')
def test_saved_plugin_menu_layout_keeps_navigation_usable_without_rewriting_preferences():
    sources = []
    for name in ('MainMenuItem', 'MainMenuLayout'):
        source = (JAVA / f'app/exteraless/drawer/{name}.java').read_text(encoding='utf-8')
        source = re.sub(r'^package [^;]+;\s*', '', source)
        source = re.sub(r'^import (?:app\.|org\.)[^;]+;\s*', '', source, flags=re.M)
        source = source.replace(f'public enum {name}', f'enum {name}')
        source = source.replace(f'public final class {name}', f'final class {name}')
        sources.append(source)
    imports = 'import java.util.*;\n'
    sources = [re.sub(r'^import [^;]+;\s*', '', source, flags=re.M) for source in sources]
    harness = '''
class MenuCheck {
 static void check(boolean value) { if(!value) throw new AssertionError("Menu migration invariant"); }
 public static void main(String[] args) {
  check(MainMenuItem.getById(102)==null);
  for(boolean bottomHidden:new boolean[]{false,true}) {
   MainTabsLayout.hidden=bottomHidden;
   for(String raw:new String[]{"102;", "-1,102,-1;", "102;6,8"}) {
    AppearanceConfig.mainMenuLayout.raw=raw;
    check(MainMenuLayout.getLayout().equals(MainMenuLayout.getDefaultLayout()));
    check(!MainMenuLayout.getHiddenItems().contains(102));
    check(AppearanceConfig.mainMenuLayout.raw.equals(raw));
   }
  }
  MainTabsLayout.hidden=false;
  AppearanceConfig.mainMenuLayout.raw="11,102,8;102,6";
  check(MainMenuLayout.getLayout().equals(Arrays.asList(11,8)));
  check(MainMenuLayout.getHiddenItems().contains(6));
  check(!MainMenuLayout.getHiddenItems().contains(102));
  check(AppearanceConfig.mainMenuLayout.writes==0);
 }
}
class AppearanceConfig {
 static final Item mainMenuLayout=new Item();
 static void ensureLoaded() {}
 static class Item {
  String raw=""; int writes;
  String String(){return raw;}
  void setConfigString(String value){raw=value;writes++;}
 }
}
class MainTabsLayout {static boolean hidden;static boolean isBottomNavigationHidden(){return hidden;}}
'''
    with tempfile.TemporaryDirectory(prefix='freezgram-menu-') as directory:
        source = Path(directory) / 'MenuCheck.java'
        source.write_text(imports + harness + '\n'.join(sources), encoding='utf-8')
        subprocess.run(['java', str(source)], check=True, capture_output=True, text=True)
