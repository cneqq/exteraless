"""Exercise the actual navigation glass policy and color fallback with Android stubs."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java


class IosGlassTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_disabling_glass_releases_effect_and_repeated_updates_are_idempotent(self):
        path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/org/telegram/ui/Components/blur3/drawable/BlurredBackgroundDrawableRenderNode.java'
        toggle=method(path.read_text(), '    public void setLiquidGlassEffectAllowed(boolean allowed)')
        run_java('''
class PrivacyCheck{
 LiquidGlassEffect liquidGlassEffect;RenderNode renderNodeFill=new RenderNode();boolean renderNodeInvalidated;int invalidations;
 void invalidateSelf(){invalidations++;}
 TOGGLE
 public static void main(String[] args){
  PrivacyCheck node=new PrivacyCheck();node.setLiquidGlassEffectAllowed(true);
  if(node.renderNodeFill.effect==null||node.invalidations!=1||!node.renderNodeInvalidated)throw new AssertionError();
  node.setLiquidGlassEffectAllowed(true);if(node.invalidations!=1)throw new AssertionError("Shader recreated");
  node.setLiquidGlassEffectAllowed(false);
  if(node.renderNodeFill.effect!=null||node.liquidGlassEffect!=null||node.invalidations!=2)throw new AssertionError("Shader not released");
  node.setLiquidGlassEffectAllowed(false);if(node.invalidations!=2)throw new AssertionError("Unnecessary invalidation");
 }
}
class RenderNode{Object effect;void setRenderEffect(Object effect){this.effect=effect;}}
class LiquidGlassEffect{LiquidGlassEffect(RenderNode node){node.setRenderEffect(new Object());}}
'''.replace('TOGGLE',toggle))

    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_glass_requires_ios_opt_in_supported_android_and_no_power_saver(self):
        path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/app/freezgram/IosLiquidGlassNavigation.java'
        source=path.read_text()
        source=source[source.index('public final class'):].replace('public final class','final class',1)
        run_java('''
class PrivacyCheck {
 public static void main(String[] args){
  for(int sdk:new int[]{24,31,32,33,36})for(boolean ios:new boolean[]{false,true})
  for(boolean enabled:new boolean[]{false,true})for(boolean blur:new boolean[]{false,true})
  for(boolean saver:new boolean[]{false,true}){
   Build.VERSION.SDK_INT=sdk;MainTabsUiHelper.ios=ios;AppearanceConfig.glass=enabled;
   SharedConfig.blur=blur;LiteMode.saver=saver;
   if(IosLiquidGlassNavigation.isRequested()!=(ios&&enabled))throw new AssertionError("Parent gate");
   boolean expected=ios&&enabled&&sdk>=33&&blur&&!saver;
   if(IosLiquidGlassNavigation.isEnabled()!=expected)throw new AssertionError("Compatibility gate");
   BlurredBackgroundDrawableRenderNode renderNode=new BlurredBackgroundDrawableRenderNode();
   IosLiquidGlassNavigation.refresh(renderNode);
   if(renderNode.enabled!=expected)throw new AssertionError("Shader state not refreshed");
   BlurredBackgroundProvider provider=IosLiquidGlassNavigation.colors(null);
   int alpha=provider.background.getColor(null,false)>>>24;
   if(expected ? alpha>100||alpha<40 : alpha<200)throw new AssertionError("Unreadable fallback");
  }
  BlurredBackgroundDrawable drawable=new BlurredBackgroundDrawable();
  IosLiquidGlassNavigation.configure(drawable);
  if(drawable.thickness!=12||drawable.intensity!=.55f)throw new AssertionError("Refraction settings");
 }
}
class Build{static class VERSION{static int SDK_INT;}}
class MainTabsUiHelper{static boolean ios;static boolean isIosNavigationBar(){return ios;}}
class AppearanceConfig{static boolean glass;static boolean iosLiquidGlassNavigation(){return glass;}}
class SharedConfig{static boolean blur;static boolean chatBlurEnabled(){return blur;}}
class LiteMode{static boolean saver;static boolean isPowerSaverApplied(){return saver;}}
class AndroidUtilities{static int dp(int value){return value;}static float dpf2(float value){return value;}}
class Theme{
 static class ResourcesProvider{}static int key_windowBackgroundWhite;
 static int getColor(int key,ResourcesProvider r){return 0xffeeeeee;}
 static int multAlpha(int color,float alpha){return (color&0xffffff)|((int)(255*alpha)<<24);}
}
class BlurredBackgroundDrawable{int thickness;float intensity;void setThickness(int t){thickness=t;}void setIntensity(float i){intensity=i;}}
class BlurredBackgroundDrawableRenderNode extends BlurredBackgroundDrawable{
 boolean enabled;void setLiquidGlassEffectAllowed(boolean enabled){this.enabled=enabled;}
}
class BlurredBackgroundProvider{
 interface ColorProvider{int getColor(Theme.ResourcesProvider r,boolean dark);}
 ColorProvider background;
}
class BlurredBackgroundProviderBuilder extends BlurredBackgroundProvider{
 BlurredBackgroundProviderBuilder(Theme.ResourcesProvider r){}
 BlurredBackgroundProviderBuilder setBackgroundColor(ColorProvider p){background=p;return this;}
 BlurredBackgroundProviderBuilder setStrokeColorTop(int a,int b){return this;}
 BlurredBackgroundProviderBuilder setStrokeColorBottom(int a,int b){return this;}
 BlurredBackgroundProviderBuilder setStrokeWidth(float a,float b){return this;}
 BlurredBackgroundProviderBuilder setShadowColor(int a,int b){return this;}
 BlurredBackgroundProviderBuilder setShadowLayer(float a,float b,float c){return this;}
 BlurredBackgroundProvider build(){return this;}
}
''' + source)


if __name__=='__main__':unittest.main()
