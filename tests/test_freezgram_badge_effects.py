"""Exercise badge redraw scheduling without an Android runtime or Telegram session."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import run_java


class BadgeEffectsTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_style_choice_persists_and_refreshes_existing_badges(self):
        path = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java/app/freezgram/badges/BadgeStyleConfig.java'
        source=path.read_text()
        source=source[source.index('public final class'):].replace('public final class','final class',1)
        run_java('''import java.util.ArrayList;import java.util.WeakHashMap;
class PrivacyCheck {
 public static void main(String[] args) throws Exception {
  if(BadgeStyleConfig.getStyle()!=BadgeStyleConfig.SPARKLES)throw new AssertionError("Wrong default");
  Drawable existing=new Drawable();BadgeStyleConfig.register(existing);
  for(int style:new int[]{BadgeStyleConfig.PLAIN,BadgeStyleConfig.SEAL,BadgeStyleConfig.SPARKLES}){
   int before=existing.invalidations;BadgeStyleConfig.setStyle(style);
   if(existing.invalidations!=before+1)throw new AssertionError("Existing badge did not refresh");
   var field=BadgeStyleConfig.class.getDeclaredField("style");field.setAccessible(true);field.setInt(null,-1);
   if(BadgeStyleConfig.getStyle()!=style)throw new AssertionError("Style not persisted");
  }
  boolean rejected=false;
  try{BadgeStyleConfig.setStyle(99);}catch(IllegalArgumentException e){rejected=true;}
  if(!rejected)throw new AssertionError("Invalid style accepted");
 }
}
class Drawable{int invalidations;public void invalidateSelf(){invalidations++;}}
class Context{
 static final int MODE_PRIVATE=0;final Prefs prefs=new Prefs();
 Prefs getSharedPreferences(String name,int mode){return prefs;}
}
class Prefs{
 int value;int getInt(String key,int fallback){return value;}
 Prefs edit(){return this;}Prefs putInt(String key,int value){this.value=value;return this;}void apply(){}
}
class ApplicationLoader{static Context applicationContext=new Context();}
''' + source)

    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_sparkles_only_schedule_while_host_is_visible_and_animations_enabled(self):
        path = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java/app/freezgram/badges/FreezgramBadgeDrawable.java'
        source = path.read_text()
        source = source[source.index('public final class'):].replace('public final class', 'final class', 1)
        run_java('''
class PrivacyCheck {
  static void check(boolean value){if(!value)throw new AssertionError("Animation lifecycle");}
  public static void main(String[] args){
    Drawable seal=new Drawable();
    Drawable plane=new Drawable();
    BadgeStyleConfig.style=BadgeStyleConfig.SEAL;
    FreezgramBadgeDrawable badge=new FreezgramBadgeDrawable(seal,plane);
    badge.setBounds(0,0,32,28);
    Canvas canvas=new Canvas();
    badge.draw(canvas);check(badge.scheduled==0);
    View view=new View();badge.setCallback(view);
    badge.draw(canvas);check(badge.scheduled==1);
    int before=badge.scheduled;badge.frame.run();check(badge.scheduled==before);
    view.shown=false;badge.draw(canvas);check(badge.scheduled==before);
    view.shown=true;view.attached=false;badge.draw(canvas);check(badge.scheduled==before);
    view.attached=true;view.window=4;badge.draw(canvas);check(badge.scheduled==before);
    view.window=0;SharedConfig.enabled=false;badge.draw(canvas);check(badge.scheduled==before);
    SharedConfig.enabled=true;LiteMode.enabled=false;badge.draw(canvas);check(badge.scheduled==before);
    LiteMode.enabled=true;badge.setAlpha(0);badge.draw(canvas);check(badge.scheduled==before);
    badge.setAlpha(255);badge.draw(canvas);check(badge.scheduled==before+1);
    check(canvas.depth==0);check(badge.getIntrinsicWidth()==32&&badge.getIntrinsicHeight()==28);
    AndroidUtilities.density=3;
    badge.setBounds(0,0,96,84);badge.draw(canvas);
    check(seal.getBounds().width()==72&&seal.getBounds().height()==72);
    check(badge.getIntrinsicWidth()==96&&badge.getIntrinsicHeight()==84&&canvas.depth==0);
    BadgeStyleConfig.style=BadgeStyleConfig.PLAIN;
    before=badge.scheduled;badge.draw(canvas);check(badge.scheduled==before);
    check(plane.getBounds().width()==78);
    BadgeStyleConfig.style=BadgeStyleConfig.SPARKLES;
    badge.draw(canvas);check(badge.scheduled==before+1);check(plane.getBounds().width()==66);
  }
}
class Rect {
  int left,top,right,bottom;
  boolean isEmpty(){return width()<=0||height()<=0;}
  int width(){return right-left;} int height(){return bottom-top;}
}
class Drawable {
  interface Callback {}
  Callback callback; Rect bounds=new Rect(); int scheduled; Runnable frame;
  void setCallback(Callback c){callback=c;} Callback getCallback(){return callback;}
  boolean isVisible(){return true;} Rect getBounds(){return bounds;}
  void setBounds(int l,int t,int r,int b){bounds.left=l;bounds.top=t;bounds.right=r;bounds.bottom=b;}
  void invalidateSelf(){} void unscheduleSelf(Runnable r){frame=null;}
  void scheduleSelf(Runnable r,long when){scheduled++;frame=r;}
  public void draw(Canvas c){} public int getIntrinsicWidth(){return 0;} public int getIntrinsicHeight(){return 0;}
  public void setAlpha(int alpha){} public void setColorFilter(ColorFilter filter){} public int getOpacity(){return 0;}
}
class Canvas {
  int depth; int save(){return depth++;} void restoreToCount(int count){depth=count;}
  void translate(float x,float y){} void scale(float x,float y){} void drawPath(Path p,Paint paint){}
}
class Paint {
  static int ANTI_ALIAS_FLAG=1;Paint(int flags){} void setColor(int c){} void setAlpha(int a){} void setColorFilter(ColorFilter f){}
}
class Path {void moveTo(float x,float y){}void lineTo(float x,float y){}void close(){}}
class ColorFilter {} class PixelFormat {static int TRANSLUCENT=-3;}
class SystemClock {static long uptimeMillis(){return 1000;}}
class View implements Drawable.Callback {
  static int VISIBLE=0;boolean attached=true,shown=true;int window;
  boolean isAttachedToWindow(){return attached;}boolean isShown(){return shown;}int getWindowVisibility(){return window;}
}
class AndroidUtilities {static int density=1;static int dp(int value){return value*density;}}
class SharedConfig {static boolean enabled=true;static boolean animationsEnabled(){return enabled;}}
class LiteMode {static int FLAG_ANIMATED_EMOJI_CHAT_NOT_PREMIUM=4096;static boolean enabled=true;static boolean isEnabled(int flag){return enabled;}}
class BadgeStyleConfig {
 static int SPARKLES=0,PLAIN=1,SEAL=2,style;
 static int getStyle(){return style;}static void register(Drawable d){}
}
''' + source)


if __name__ == '__main__':
    unittest.main()
