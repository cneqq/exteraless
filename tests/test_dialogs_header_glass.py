"""Exercise header opt-in and ActionBar override fallback with Java stubs."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java

JAVA = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java'

@unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
class DialogsHeaderGlassTests(unittest.TestCase):
    def test_header_is_independent_and_keeps_search_action_mode_and_power_fallback(self):
        gate = method((JAVA/'org/telegram/ui/DialogsActivity.java').read_text(), '    private boolean isDialogsHeaderGlassEnabled()')
        gate = gate.replace('app.exteraless.appearance.AppearanceConfig', 'AppearanceConfig')
        run_java('''
class PrivacyCheck {
 Object dialogsHeaderGlassDrawable; boolean inPreviewMode; float searchAnimationProgress,progressToActionMode;
 GATE
 public static void main(String[] args){
  var p=new PrivacyCheck();
  for(int bits=0;bits<256;bits++){
   AppearanceConfig.opt=(bits&1)!=0;Build.VERSION.SDK_INT=(bits&2)!=0?33:32;
   SharedConfig.blur=(bits&4)!=0;LiteMode.saver=(bits&8)!=0;p.inPreviewMode=(bits&16)!=0;
   p.searchAnimationProgress=(bits&32)!=0?.5f:0;p.progressToActionMode=(bits&64)!=0?1:0;
   p.dialogsHeaderGlassDrawable=(bits&128)!=0?new Object():null;
   boolean expected=bits==135;
   if(p.isDialogsHeaderGlassEnabled()!=expected)throw new AssertionError("Wrong header fallback: "+bits);
  }
 }
}
class AppearanceConfig{static boolean opt;static boolean dialogsHeaderGlass(){return opt;}}
class Build{static class VERSION{static int SDK_INT;}}
class SharedConfig{static boolean blur;static boolean chatBlurEnabled(){return blur;}}
class LiteMode{static boolean saver;static boolean isGlassPowerSaverApplied(){return saver;}}
'''.replace('GATE',gate))

    def test_override_only_consumes_background_when_it_can_draw(self):
        draw = method((JAVA/'org/telegram/ui/ActionBar/ActionBar.java').read_text(), '    private boolean drawBlurBackgroundOverride(Canvas canvas)')
        run_java('''
class PrivacyCheck{
 Drawable blurBackgroundOverride;java.util.function.BooleanSupplier blurBackgroundOverrideEnabled;
 int getMeasuredWidth(){return 400;}int getMeasuredHeight(){return 80;}
 DRAW
 public static void main(String[] args){
  var p=new PrivacyCheck();var c=new Canvas();
  if(p.drawBlurBackgroundOverride(c))throw new AssertionError("Missing material consumed background");
  var d=p.blurBackgroundOverride=new Drawable();
  for(boolean enabled:new boolean[]{false,true})for(boolean hardware:new boolean[]{false,true}){
   p.blurBackgroundOverrideEnabled=()->enabled;c.hardware=hardware;d.draws=0;
   if(p.drawBlurBackgroundOverride(c)!=(enabled&&hardware)||d.draws!=(enabled&&hardware?1:0))throw new AssertionError("Fallback lost");
  }
  if(d.width!=400||d.height!=80)throw new AssertionError("Header bounds changed");
 }
}
class Canvas{boolean hardware=true;boolean isHardwareAccelerated(){return hardware;}}
class Drawable{int width,height,draws;void setBounds(int l,int t,int r,int b){width=r-l;height=b-t;}void draw(Canvas c){draws++;}}
'''.replace('DRAW',draw))

    def test_ordinary_popup_opt_in_preserves_custom_backgrounds(self):
        gate = method((JAVA/'org/telegram/ui/Components/ItemOptions.java').read_text(), '    private boolean useSmallGlassForMenu()')
        run_java('''
class PrivacyCheck{
 boolean customMenuBackground;Object scrimView;
 GATE
 public static void main(String[] args){
  var p=new PrivacyCheck();
  for(boolean custom:new boolean[]{false,true})for(boolean anchor:new boolean[]{false,true})for(boolean enabled:new boolean[]{false,true}){
   p.customMenuBackground=custom;p.scrimView=anchor?new Object():null;SmallElementsGlass.enabled=enabled;
   if(p.useSmallGlassForMenu()!=(!custom&&anchor&&enabled))throw new AssertionError("Custom background replaced or unanchored capture enabled");
  }
 }
}
class SmallElementsGlass{static boolean enabled;static boolean isEnabled(){return enabled;}}
'''.replace('GATE',gate).replace('app.freezgram.SmallElementsGlass','SmallElementsGlass'))
