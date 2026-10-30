"""Power-save eligibility and fractional-scroll stabilization from production Java."""
from pathlib import Path
import shutil
import unittest
from test_personal_privacy import method, run_java
JAVA = Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java'

@unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
class GlassPowerAndScrollTests(unittest.TestCase):
    def test_glass_respects_system_saver_even_if_app_follow_system_is_off(self):
        policy=method((JAVA/'org/telegram/messenger/LiteMode.java').read_text(),'    public static boolean isGlassPowerSaverApplied()')
        run_java('''
class PrivacyCheck{
 static boolean app,system,followSystemSaver;
 static boolean isPowerSaverApplied(){return app;}static boolean isSystemPowerSaveMode(){return system;}
 POLICY
 public static void main(String[] args){
  for(boolean follow:new boolean[]{false,true})for(boolean a:new boolean[]{false,true})for(boolean s:new boolean[]{false,true}){
   followSystemSaver=follow;app=a;system=s;
   if(isGlassPowerSaverApplied()!=(a||s))throw new AssertionError("System saver ignored");
  }
 }
}
'''.replace('POLICY',policy))

    def test_shader_releases_in_saver_and_remembers_request_for_restore(self):
        toggle=method((JAVA/'org/telegram/ui/Components/blur3/drawable/BlurredBackgroundDrawableRenderNode.java').read_text(),'    public void setLiquidGlassEffectAllowed(boolean allowed)').replace('org.telegram.messenger.LiteMode','LiteMode')
        run_java('''
class PrivacyCheck{
 boolean liquidGlassRequested,renderNodeInvalidated;LiquidGlassEffect liquidGlassEffect;RenderNode renderNodeFill=new RenderNode();
 void invalidateSelf(){}
 TOGGLE
 public static void main(String[] args){
  var p=new PrivacyCheck();p.setLiquidGlassEffectAllowed(true);
  if(p.liquidGlassEffect==null)throw new AssertionError("Initial glass missing");
  LiteMode.saver=true;p.setLiquidGlassEffectAllowed(p.liquidGlassRequested);
  if(p.liquidGlassEffect!=null||p.renderNodeFill.effect!=null||!p.liquidGlassRequested)throw new AssertionError("Shader not released");
  LiteMode.saver=false;p.setLiquidGlassEffectAllowed(p.liquidGlassRequested);
  if(p.liquidGlassEffect==null)throw new AssertionError("Shader not restored");
  p.setLiquidGlassEffectAllowed(false);LiteMode.saver=true;p.setLiquidGlassEffectAllowed(p.liquidGlassRequested);
  LiteMode.saver=false;p.setLiquidGlassEffectAllowed(p.liquidGlassRequested);
  if(p.liquidGlassEffect!=null)throw new AssertionError("Disabled glass was enabled");
 }
}
class LiteMode{static boolean saver;static boolean isGlassPowerSaverApplied(){return saver;}}
class RenderNode{Object effect;void setRenderEffect(Object e){effect=e;}}
class LiquidGlassEffect{LiquidGlassEffect(RenderNode node){node.effect=this;}}
'''.replace('TOGGLE',toggle))

    def test_fractional_scroll_compensation_is_balanced_for_glass_only(self):
        source=(JAVA/'org/telegram/ui/Components/blur3/DownscaleScrollableNoiseSuppressor.java').read_text()
        start=source.index('        public void onScrolled(float dx, float dy)')
        scroll=source[start:source.index('\n        }',start)+len('\n        }')]
        run_java('''
class PrivacyCheck{
 int scaleX=4,scaleY=4;float scrollX,scrollY;boolean allowNoiseSuppress,stabilizeScroll;
 RenderNode renderNodeOriginalWithOffset=new RenderNode();RenderNode[] renderNodeRestored={new RenderNode()};
 SCROLL
 public static void main(String[] args){
  for(boolean enabled:new boolean[]{false,true}){
   var p=new PrivacyCheck();p.stabilizeScroll=enabled;
   for(int i=0;i<100;i++){
    p.onScrolled(.25f,.5f);
    if(enabled&&(p.renderNodeOriginalWithOffset.x!=p.scrollX||p.renderNodeRestored[0].y!=-p.scrollY))throw new AssertionError("Fractional phase lost");
    if(p.renderNodeOriginalWithOffset.x+p.renderNodeRestored[0].x!=0||p.renderNodeOriginalWithOffset.y+p.renderNodeRestored[0].y!=0)throw new AssertionError("Viewport drift");
    if(!enabled&&(p.renderNodeOriginalWithOffset.x!=0||p.renderNodeRestored[0].y!=0))throw new AssertionError("Legacy capture changed");
   }
  }
 }
}
class RenderNode{float x,y;void setTranslationX(float v){x=v;}void setTranslationY(float v){y=v;}}
'''.replace('SCROLL',scroll))
