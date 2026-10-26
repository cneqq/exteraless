"""Exercise launcher upgrades with the real controller and a fake PackageManager."""
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'TMessagesProj/src/main'


class LauncherIconTests(unittest.TestCase):
    def test_only_freezgram_icons_are_offered(self):
        source = (MAIN / 'java/org/telegram/ui/LauncherIconController.java').read_text()
        choices = re.findall(r'^        ([A-Z_]+)\("', source, re.M)
        self.assertEqual(choices, ['EXTERALESS', 'FREEZGRAM_WHITE', 'FREEZGRAM_MONO_DARK'])

    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_legacy_upgrades_and_current_choices_keep_one_launcher_entry(self):
        source = (MAIN / 'java/org/telegram/ui/LauncherIconController.java').read_text()
        source = source[source.index('public class LauncherIconController'):].replace(
            'public class LauncherIconController', 'class LauncherIconController', 1)
        ns = '{http://schemas.android.com/apk/res/android}'
        aliases = ET.parse(MAIN / 'AndroidManifest.xml').getroot().find('application').findall('activity-alias')
        aliases = [a for a in aliases if any(c.get(ns + 'name') == 'android.intent.category.LAUNCHER' for c in a.findall('./intent-filter/category'))]
        names = [a.get(ns + 'name') for a in aliases]
        default = next(a.get(ns + 'name') for a in aliases if a.get(ns + 'enabled') == 'true')
        r_groups = {}
        for group, name in re.findall(r'R\.(\w+)\.(\w+)', source):
            r_groups.setdefault(group, set()).add(name)
        resources = 'class R {' + ''.join(
            'static class ' + group + ' {' + ''.join('static int ' + name + '=0;' for name in sorted(values)) + '}'
            for group, values in r_groups.items()) + '}'
        harness = '''import java.util.*;
class LauncherUpgradeCheck {
  static void check(boolean value) { if (!value) throw new AssertionError("Launcher invariant"); }
  static void verify(String expected) {
    PackageManager pm=ApplicationLoader.applicationContext.pm;
    check(pm.active()==1 && pm.enabled(expected));
    int writes=pm.writes;
    LauncherIconController.tryFixLauncherIconIfNeeded();
    check(pm.active()==1 && pm.enabled(expected) && pm.writes==writes);
  }
  public static void main(String[] args) {
    ApplicationLoader.applicationContext=new Context();
    LauncherIconController.tryFixLauncherIconIfNeeded();
    verify(PackageManager.DEFAULT_ICON);
    Set<String> current=new HashSet<>();
    for (var icon:LauncherIconController.LauncherIcon.values()) current.add(icon.getComponentName(new Context()).name);
    for (String old:PackageManager.NAMES) {
      if (current.contains(old)) continue;
      Context ctx=new Context(); ApplicationLoader.applicationContext=ctx;
      ctx.pm.states.put(PackageManager.DEFAULT_ICON,2);ctx.pm.states.put(old,1);
      LauncherIconController.tryFixLauncherIconIfNeeded();
      verify(PackageManager.DEFAULT_ICON);
    }
    for (var icon:LauncherIconController.LauncherIcon.values()) {
      Context ctx=new Context();ApplicationLoader.applicationContext=ctx;
      ctx.pm.states.put(PackageManager.DEFAULT_ICON,2);
      String selected=icon.getComponentName(ctx).name;ctx.pm.states.put(selected,1);
      LauncherIconController.tryFixLauncherIconIfNeeded();verify(selected);
      for (var next:LauncherIconController.LauncherIcon.values()) {
        LauncherIconController.setIcon(next);verify(next.getComponentName(ctx).name);
      }
    }
  }
}
class ComponentName {
  String name; ComponentName(String pkg,String name) { this.name=name; }
}
class Context {
  PackageManager pm=new PackageManager();
  PackageManager getPackageManager(){return pm;}
  String getPackageName(){return "test.freezgram";}
}
class ApplicationLoader { static Context applicationContext=new Context(); }
class PackageManager {
  static int COMPONENT_ENABLED_STATE_DEFAULT=0,COMPONENT_ENABLED_STATE_ENABLED=1,COMPONENT_ENABLED_STATE_DISABLED=2,DONT_KILL_APP=1;
  static String DEFAULT_ICON="DEFAULT_NAME";
  static List<String> NAMES=List.of(ALIAS_NAMES);
  Map<String,Integer> states=new HashMap<>();int writes;
  int getComponentEnabledSetting(ComponentName name){return states.getOrDefault(name.name,0);}
  boolean enabled(String name){int value=states.getOrDefault(name,0);return value==1 || value==0 && name.equals(DEFAULT_ICON);}
  int active(){return (int)NAMES.stream().filter(this::enabled).count();}
  void setComponentEnabledSetting(ComponentName name,int state,int flags){
    if(!NAMES.contains(name.name))throw new AssertionError("Unknown alias");
    states.put(name.name,state);writes++;
    if(active()==0)throw new AssertionError("All launcher entries disabled during switch");
  }
}
'''.replace('DEFAULT_NAME', default).replace('ALIAS_NAMES', ','.join('"' + n + '"' for n in names))
        with tempfile.TemporaryDirectory(prefix='launcher-upgrades-') as directory:
            path = Path(directory) / 'LauncherUpgradeCheck.java'
            path.write_text(harness + resources + source)
            result = subprocess.run(['java', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr[:2000])


if __name__ == '__main__':
    unittest.main()
