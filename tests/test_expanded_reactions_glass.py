"""Expanded emoji reactions inherit the compact reaction panel's glass material."""
import shutil,unittest
from pathlib import Path
from test_personal_privacy import method,run_java
JAVA=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java'
@unittest.skipUnless(shutil.which('java'),'Java source launcher required')
class ExpandedGlassTests(unittest.TestCase):
 def test_expanded_surface_refreshes_glass_and_retains_fallback(self):
  source=(JAVA/'org/telegram/ui/Components/Reactions/CustomEmojiReactionsWindow.java').read_text()
  draw=method(source,'    private boolean drawSharedGlass(').replace('app.freezgram.SmallElementsGlass','SmallElementsGlass').replace('app.freezgram.LiquidGlassStyle','LiquidGlassStyle')
  run_java('''
class PrivacyCheck{
 boolean usesSharedGlass;Drawable blurredBackgroundDrawable=new Drawable();RectF drawingRect=new RectF();
 DRAW
 public static void main(String[] args){
  for(boolean shared:new boolean[]{false,true})for(boolean hardware:new boolean[]{false,true})for(boolean enabled:new boolean[]{false,true}){
   var p=new PrivacyCheck();var c=new Canvas();c.hardware=hardware;p.usesSharedGlass=shared;SmallElementsGlass.enabled=enabled;
   boolean expected=shared&&hardware&&enabled;
   if(p.drawSharedGlass(c,18)!=expected||p.blurredBackgroundDrawable.draws!=(expected?1:0))throw new AssertionError("Expanded glass fallback gate");
   if(expected&&(p.blurredBackgroundDrawable.radius!=18||p.blurredBackgroundDrawable.alpha!=255||p.blurredBackgroundDrawable.updates!=1||!p.blurredBackgroundDrawable.configured))throw new AssertionError("Expanded panel optics/geometry missing");
  }
  var p=new PrivacyCheck();p.blurredBackgroundDrawable=null;p.usesSharedGlass=true;
  if(p.drawSharedGlass(new Canvas(),18))throw new AssertionError("Null material has no fallback");
 }
}
class Canvas{boolean hardware;boolean isHardwareAccelerated(){return hardware;}}class Rect{}class RectF{void roundOut(Rect r){}}
class AndroidUtilities{static Rect rectTmp2=new Rect();}
class Drawable{int draws,updates,alpha;float radius;boolean configured;void setBounds(Rect r){}void setRadius(float r){radius=r;}void setAlpha(int a){alpha=a;}void updateColors(){updates++;}void draw(Canvas c){draws++;}}
class SmallElementsGlass{static boolean enabled;static boolean isEnabled(){return enabled;}}
class LiquidGlassStyle{static void configure(Drawable d){d.configured=true;}}
'''.replace('DRAW',draw))

 def test_expansion_prefers_shared_glass_factory_over_legacy(self):
  source=(JAVA/'org/telegram/ui/Components/ReactionsContainerLayout.java').read_text()
  a=source.index('        if (glassBackgroundFactory != null && app.freezgram.SmallElementsGlass.isEnabled())',source.index('    private void showCustomEmojiReactionDialog()'))
  b=source.index('        reactionsWindow.setLongPressEnabled',a)
  branch=source[a:b].replace('app.freezgram.SmallElementsGlass','SmallElementsGlass')
  run_java('''
class PrivacyCheck{
 Object glassBackgroundFactory,glassBackgroundColorProvider=new Object(),backgroundFactory,backgroundColorProvider=new Object();Window reactionsWindow=new Window();
 void open(){BRANCH}
 public static void main(String[] args){
  for(boolean glass:new boolean[]{false,true})for(boolean legacy:new boolean[]{false,true})for(boolean enabled:new boolean[]{false,true}){
   var p=new PrivacyCheck();if(glass)p.glassBackgroundFactory=new Object();if(legacy)p.backgroundFactory=new Object();SmallElementsGlass.enabled=enabled;p.open();
   int expected=glass&&enabled?2:legacy?1:0;
   if(p.reactionsWindow.kind!=expected)throw new AssertionError("Expanded picker lost shared glass factory");
  }
 }
}
class Window{int kind;void setGlassBackgroundFactory(Object f,Object c){kind=2;}void setBackgroundFactory(Object f,Object c){kind=1;}}
class SmallElementsGlass{static boolean enabled;static boolean isEnabled(){return enabled;}}
'''.replace('BRANCH',branch))
