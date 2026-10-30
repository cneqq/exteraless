"""Exercise header opt-in and ActionBar override fallback with Java stubs."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java

JAVA = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java'

@unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
class DialogsHeaderGlassTests(unittest.TestCase):
    def test_header_keeps_glass_in_selection_and_preserves_search_and_power_fallback(self):
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
   boolean expected=bits==135||bits==199;
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

    def test_transparent_theme_still_attempts_custom_backdrop(self):
        source=(JAVA/'org/telegram/ui/ActionBar/ActionBar.java').read_text()
        start=source.index('        final boolean customBlurBackground =')
        end=source.index('\n',source.index('        if (blurredBackground && !customBlurBackground',start))
        dispatch=source[start:end]+' fallback++; }'
        run_java('''
class PrivacyCheck{
 boolean blurredBackground=true,enabled;int actionBarColor,fallback,attempts;
 boolean drawBlurBackgroundOverride(Canvas c){attempts++;return enabled;}
 void draw(Canvas canvas){DISPATCH}
 public static void main(String[] args){
  for(int color:new int[]{0,0xff111111})for(boolean enabled:new boolean[]{false,true}){
   var p=new PrivacyCheck();p.actionBarColor=color;p.enabled=enabled;p.draw(new Canvas());
   if(p.attempts!=1||p.fallback!=(!enabled&&color!=0?1:0))throw new AssertionError("Theme color suppressed explicit glass");
  }
 }
}
class Canvas{}class Color{static final int TRANSPARENT=0;}
'''.replace('DISPATCH',dispatch))

    def test_automatic_menu_capture_refreshes_and_preserves_explicit_factories(self):
        source=(JAVA/'org/telegram/ui/ActionBar/ActionBarMenuItem.java').read_text()
        refresh=method(source,'    private void refreshAutomaticSmallGlass()')
        for name in ('org.telegram.ui.Components.blur3.source.BlurredBackgroundSourceBitmap', 'org.telegram.ui.Components.chat.ViewPositionWatcher', 'app.exteraless.appearance.GlassMenuHelper', 'app.freezgram.SmallElementsGlass', 'app.freezgram.LiquidGlassStyle'):
            refresh=refresh.replace(name,name.rsplit('.',1)[1])
        run_java('''
class PrivacyCheck{
 Object popupLayout=new Object(),resourcesProvider,subMenuProvider;
 boolean automaticSmallGlass;BlurredBackgroundSourceBitmap automaticGlassSnapshot;BlurredBackgroundDrawableViewFactory subMenuFactory;
 View root=new ViewGroup();View getRootView(){return root;}
 REFRESH
 public static void main(String[] args){
  var p=new PrivacyCheck();SmallElementsGlass.enabled=true;p.refreshAutomaticSmallGlass();
  if(!p.automaticSmallGlass||GlassMenuHelper.captures!=1)throw new AssertionError("Ordinary menu skipped");
  var first=p.automaticGlassSnapshot;p.refreshAutomaticSmallGlass();
  if(first==p.automaticGlassSnapshot||GlassMenuHelper.captures!=2)throw new AssertionError("Stale menu snapshot");
  SmallElementsGlass.enabled=false;p.refreshAutomaticSmallGlass();
  if(p.automaticSmallGlass||p.subMenuFactory!=null||p.automaticGlassSnapshot!=null||GlassMenuHelper.resets!=1)throw new AssertionError("Style not restored");
  var custom=new BlurredBackgroundDrawableViewFactory(null);p.subMenuFactory=custom;
  SmallElementsGlass.enabled=true;p.refreshAutomaticSmallGlass();
  if(p.subMenuFactory!=custom||GlassMenuHelper.captures!=2)throw new AssertionError("Explicit source replaced");
 }
}
class View{}class ViewGroup extends View{}
class BlurredBackgroundSourceBitmap{}
class BlurredBackgroundDrawableViewFactory{BlurredBackgroundDrawableViewFactory(Object source){}void setSourceRootView(Object watcher,ViewGroup root){}}
class ViewPositionWatcher{ViewPositionWatcher(ViewGroup root){}}
class SmallElementsGlass{static boolean enabled;static boolean isEnabled(){return enabled;}}
class LiquidGlassStyle{static Object surfaceColors(Object r,java.util.function.BooleanSupplier enabled){return null;}}
class GlassMenuHelper{
 static int captures,resets;
 static void captureBlur(Object s,Object f,View v){captures++;}
 static void applyToPopup(Object f,Object r,Object p){}
 static void applyToReusedMenu(Object f,Object s,Object r,Object p,View root,boolean on){resets++;}
}
'''.replace('REFRESH',refresh))
