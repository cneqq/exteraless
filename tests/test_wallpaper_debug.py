"""Exercise opt-in flags and bitmap capture with synthetic Android objects."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java

JAVA = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java'


@unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
class WallpaperDebugTests(unittest.TestCase):
    def test_flags_are_independent_persistent_and_resettable(self):
        source = (JAVA / 'app/freezgram/WallpaperDebugConfig.java').read_text()
        source = source[source.index('public final class'):].replace('public final class', 'final class', 1)
        run_java('''import java.util.*;
class PrivacyCheck {
  public static void main(String[] args) throws Exception {
    for (int option : WallpaperDebugConfig.OPTIONS)
      if (WallpaperDebugConfig.enabled(option)) throw new AssertionError("Default changed");
    for (int option : WallpaperDebugConfig.OPTIONS) {
      WallpaperDebugConfig.toggle(option);
      for (int other : WallpaperDebugConfig.OPTIONS)
        if (WallpaperDebugConfig.enabled(other) != (option == other))
          throw new AssertionError("Flags interfere");
      var field = WallpaperDebugConfig.class.getDeclaredField("flags");
      field.setAccessible(true); field.setInt(null, -1);
      if (!WallpaperDebugConfig.enabled(option)) throw new AssertionError("Not persisted");
      WallpaperDebugConfig.toggle(option);
      if (WallpaperDebugConfig.enabled(option)) throw new AssertionError("Cannot disable");
    }
    for (int option : WallpaperDebugConfig.OPTIONS) WallpaperDebugConfig.toggle(option);
    WallpaperDebugConfig.reset();
    for (int option : WallpaperDebugConfig.OPTIONS)
      if (WallpaperDebugConfig.enabled(option)) throw new AssertionError("Reset failed");
  }
}
class Context {
  static final int MODE_PRIVATE = 0;
  final Map<String,Prefs> stores = new HashMap<>();
  Prefs getSharedPreferences(String name,int mode) { return stores.computeIfAbsent(name,k->new Prefs()); }
}
class Prefs {
  final Map<String,Integer> values = new HashMap<>();
  int getInt(String key,int fallback) { return values.getOrDefault(key,fallback); }
  Prefs edit() { return this; }
  Prefs putInt(String key,int value) { values.put(key,value); return this; }
  void apply() {}
}
class ApplicationLoader { static Context applicationContext = new Context(); }
''' + source)

    def test_bitmap_dimensions_only_change_when_enabled(self):
        source = (JAVA / 'org/telegram/ui/Components/blur3/source/BlurredBackgroundSourceBitmap.java').read_text()
        capture = method(source, '    public Canvas beginRecording(int width, int height, float scale)')
        run_java('''
class PrivacyCheck {
  Bitmap bitmapInternal;
  CAPTURE
  public static void main(String[] args) {
    PrivacyCheck check = new PrivacyCheck();
    Canvas original = check.beginRecording(120,160,1);
    if (original.bitmap.w != 120 || original.bitmap.h != 120) throw new AssertionError("Baseline changed");
    WallpaperDebugConfig.fix = true;
    Canvas fixed = check.beginRecording(120,160,1);
    if (fixed.bitmap.w != 120 || fixed.bitmap.h != 160) throw new AssertionError("Wrong proportions");
    if (check.beginRecording(120,160,1).bitmap != fixed.bitmap || !fixed.bitmap.cleared)
      throw new AssertionError("Matching buffer not cleared and reused");
    Canvas scaled = check.beginRecording(120,160,2);
    if (scaled.bitmap.w != 60 || scaled.bitmap.h != 80 || scaled.sx != 2 || scaled.sy != 2)
      throw new AssertionError("Wrong scale");
    WallpaperDebugConfig.fix = false;
    if (check.beginRecording(120,160,1).bitmap.h != 120) throw new AssertionError("Cannot return to baseline");
  }
}
class WallpaperDebugConfig {
  static int BITMAP_SIZE=1; static boolean fix;
  static boolean enabled(int option) { return fix; }
}
class Bitmap {
  enum Config { ARGB_8888 }
  int w,h; boolean cleared;
  static Bitmap createBitmap(int w,int h,Config config) { Bitmap b=new Bitmap(); b.w=w;b.h=h;return b; }
  int getWidth(){return w;} int getHeight(){return h;} boolean isRecycled(){return false;}
  void eraseColor(int color){cleared=true;}
}
class Canvas {
  Bitmap bitmap; float sx,sy;
  Canvas(Bitmap bitmap){this.bitmap=bitmap;}
  void scale(float x,float y){sx=x;sy=y;}
}
'''.replace('CAPTURE', capture))


if __name__ == '__main__':
    unittest.main()
