"""Policies and snapshot lifetime for small app surfaces, with no real app data."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java

SOURCE = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java/app/freezgram/SmallElementsGlass.java'

@unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
class SmallGlassTests(unittest.TestCase):
    def test_unsupported_devices_and_disabled_policy_keep_ordinary_surfaces(self):
        gate = method(SOURCE.read_text(), '    public static boolean isEnabled()')
        run_java('''
class PrivacyCheck {
 GATE
 public static void main(String[] args){
  for(int sdk:new int[]{24,31,32,33,36})for(boolean opt:new boolean[]{false,true})
  for(boolean blur:new boolean[]{false,true})for(boolean saver:new boolean[]{false,true}){
   Build.VERSION.SDK_INT=sdk;AppearanceConfig.opt=opt;SharedConfig.blur=blur;LiteMode.saver=saver;
   if(isEnabled()!=(sdk>=33&&opt&&blur&&!saver))throw new AssertionError("Unsafe glass activation");
  }
 }
}
class Build{static class VERSION{static int SDK_INT;}}
class AppearanceConfig{static boolean opt;static boolean smallElementsGlass(){return opt;}}
class SharedConfig{static boolean blur;static boolean chatBlurEnabled(){return blur;}}
class LiteMode{static boolean saver;static boolean isPowerSaverApplied(){return saver;}}
'''.replace('GATE', gate))

    def test_snapshot_bridge_updates_when_bitmap_or_settings_change(self):
        source=SOURCE.read_text()
        start=source.index('    private static final class SnapshotSource')
        end=source.index('    /** One in-memory',start)
        nested=source[start:end]
        run_java('''
class PrivacyCheck {
 NESTED
 public static void main(String[] args){
  var input=new BlurredBackgroundSourceBitmap();var bridge=new SnapshotSource(input);var c=new Canvas();
  bridge.draw(c,0,0,100,50);bridge.draw(c,0,0,100,50);
  if(input.calls!=1)throw new AssertionError("Repeated static capture");
  input.bitmap=new Bitmap();bridge.draw(c,0,0,100,50);
  if(input.calls!=2)throw new AssertionError("New menu image ignored");
  LiquidGlassStyle.rev++;bridge.draw(c,0,0,100,50);
  if(input.calls!=3)throw new AssertionError("Shared optics ignored");
  bridge.draw(c,0,0,200,50);
  if(input.calls!=4)throw new AssertionError("Resized capture ignored");
 }
}
class Canvas{}class Bitmap{}
interface BlurredBackgroundSource{void draw(Canvas c,float l,float t,float r,float b);}
class BlurredBackgroundSourceBitmap implements BlurredBackgroundSource{
 Bitmap bitmap=new Bitmap();int calls;Bitmap getBitmap(){return bitmap;}
 public void draw(Canvas c,float l,float t,float r,float b){calls++;}
}
class BlurredBackgroundSourceRenderNode implements BlurredBackgroundSource{
 int w,h;boolean recorded;BlurredBackgroundSourceRenderNode(BlurredBackgroundSource fallback){}
 boolean needUpdateDisplayList(int width,int height){return !recorded||w!=width||h!=height;}
 Canvas beginRecording(int width,int height){w=width;h=height;return new Canvas();}void endRecording(){recorded=true;}
 void setBlur(float radius,Object effect){}public void draw(Canvas c,float l,float t,float r,float b){}
}
class LiquidGlassStyle{static int rev;static int revision(){return rev;}static int blurRadiusDp(){return 6;}static boolean enhanceColors(){return true;}}
class AndroidUtilities{static int dp(int n){return n;}static float dpf2(int n){return n;}}
class RenderNodeEffects{static Object getSaturationX3RenderEffect(){return null;}}
'''.replace('NESTED',nested).replace('org.telegram.messenger.utils.RenderNodeEffects','RenderNodeEffects'))

    def test_notice_release_drops_capture_and_render_references(self):
        release = method(SOURCE.read_text(), '        public void release()')
        # method() is scoped to four spaces; the selected function is eight spaces deep.
        release=release[:release.index('\n        }')+len('\n        }')]
        run_java('''
class PrivacyCheck{
 Object glass=new Object(),bitmap=new Object(),capturedRoot=new Object();Source bitmapSource=new Source();
 RELEASE
 public static void main(String[] args){
  var p=new PrivacyCheck();p.release();p.release();
  if(p.glass!=null||p.bitmap!=null||p.capturedRoot!=null||p.bitmapSource.value!=null)throw new AssertionError("Capture retained");
 }
}
class Source{Object value=new Object();void setBitmap(Object o){value=o;}}
'''.replace('RELEASE',release))
