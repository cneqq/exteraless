"""Exercise opt-in flags and bitmap capture with synthetic Android objects."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java

JAVA = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java'


@unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
class WallpaperDebugTests(unittest.TestCase):
    def test_local_viewport_covers_window_and_restores_shared_drawable(self):
        source = (JAVA / 'app/freezgram/WallpaperViewport.java').read_text()
        source = source[source.index('public final class'):].replace('public final class', 'final class', 1)
        run_java('''
class PrivacyCheck {
  public static void main(String[] args) {
    for (int[] size : new int[][]{{60,80},{1800,600},{600,2400},{-1,-1}}) {
      Drawable drawable = new Drawable(size[0],size[1]);
      Canvas canvas = new Canvas();
      WallpaperViewport.draw(canvas,drawable,1080,2400);
      if (drawable.drawn.left != 0 || drawable.drawn.top != 0 ||
          drawable.drawn.right < 1080 || drawable.drawn.bottom < 2400)
        throw new AssertionError("Uncovered viewport");
      if (Math.abs(canvas.tx*2 + drawable.drawn.right - 1080) > .01 ||
          Math.abs(canvas.ty*2 + drawable.drawn.bottom - 2400) > .01)
        throw new AssertionError("Wallpaper not centered");
      checkRestored(drawable,canvas);
    }
    Drawable broken = new Drawable(60,80); broken.fail=true;
    Canvas canvas = new Canvas();
    try { WallpaperViewport.draw(canvas,broken,1080,2400); throw new AssertionError("Exception swallowed"); }
    catch (IllegalStateException expected) { checkRestored(broken,canvas); }
    MotionBackgroundDrawable motion = new MotionBackgroundDrawable();
    WallpaperViewport.draw(new Canvas(),motion,1080,2400);
    if (!motion.local) throw new AssertionError("Motion translation not isolated");
  }
  static void checkRestored(Drawable d, Canvas c) {
    Rect b=d.getBounds();
    if(b.left!=7 || b.top!=9 || b.right!=127 || b.bottom!=169 || c.depth!=0)
      throw new AssertionError("Leaked drawable bounds or canvas state");
  }
}
class Rect {
  int left,top,right,bottom;
  Rect(int l,int t,int r,int b){left=l;top=t;right=r;bottom=b;}
  Rect(Rect r){this(r.left,r.top,r.right,r.bottom);}
}
class Canvas {
  int depth; float tx,ty;
  int save(){return depth++;}
  void clipRect(int l,int t,int r,int b){}
  void translate(float x,float y){tx=x;ty=y;}
  void restoreToCount(int count){depth=count;}
}
class Drawable {
  int width,height; boolean fail; Rect bounds=new Rect(7,9,127,169),drawn;
  Drawable(int w,int h){width=w;height=h;}
  int getIntrinsicWidth(){return width;} int getIntrinsicHeight(){return height;}
  Rect getBounds(){return bounds;}
  void setBounds(int l,int t,int r,int b){bounds=new Rect(l,t,r,b);}
  void setBounds(Rect rect){bounds=new Rect(rect);}
  void draw(Canvas canvas){drawn=new Rect(bounds);if(fail)throw new IllegalStateException();}
}
class MotionBackgroundDrawable extends Drawable {
  boolean local;
  MotionBackgroundDrawable(){super(60,80);}
  void drawInLocalCoordinates(Canvas canvas){local=true;draw(canvas);}
}
''' + source)

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
