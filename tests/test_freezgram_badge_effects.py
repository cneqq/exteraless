"""Exercise badge redraw scheduling without an Android runtime or Telegram session."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import run_java


class BadgeEffectsTests(unittest.TestCase):
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
    FreezgramBadgeDrawable badge=new FreezgramBadgeDrawable(seal);
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
''' + source)


if __name__ == '__main__':
    unittest.main()
