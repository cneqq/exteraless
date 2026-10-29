"""Exercise the actual navigation glass policy and color fallback with Android stubs."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java


class IosGlassTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_ios_lift_keeps_visual_height_but_moves_capture_and_reserves_content(self):
        path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/app/exteraless/appearance/MainTabsUiHelper.java'
        text=path.read_text()
        methods='\n'.join(method(text, signature) for signature in (
            '    public static int getTabsViewHeightDp()',
            '    public static int getTabsBottomLiftDp()',
            '    public static int getTabsBottomOccupiedHeightDp()',
            '    public static int getTabsFabOffsetDp()',
            '    public static void applyTabsBottomInset(MainTabsLayout layout, View wrapper,',
            '    public static void setBlurBounds('))
        run_java('''
class PrivacyCheck{
 static boolean ios,material;
 static boolean isIosNavigationBar(){return ios&&!material;}
 static boolean isMaterial3NavigationBar(){return material;}
 static int getWrapperSideInset(){return 0;}
 static void applyTabsBottomInset(MainTabsLayout layout,int inset){}
 METHODS
 public static void main(String[] args){
  View window=new View(),wrapper=new View();RectF rect=new RectF();
  applyTabsBottomInset(new MainTabsLayout(),wrapper,20,0,0);
  if(wrapper.bottom!=20||getTabsBottomOccupiedHeightDp()!=76)throw new AssertionError("Legacy changed");
  setBlurBounds(rect,window,20);float oldBottom=rect.bottom;
  ios=true;applyTabsBottomInset(new MainTabsLayout(),wrapper,20,0,0);
  setBlurBounds(rect,window,20);
  if(wrapper.bottom!=32||getTabsBottomOccupiedHeightDp()!=88||getTabsViewHeightDp()!=76)
   throw new AssertionError("Panel height and occupied space confused");
  if(rect.bottom!=oldBottom-12||rect.bottom-rect.top!=60||getTabsFabOffsetDp()!=80)
   throw new AssertionError("Capture or FAB not lifted");
  material=true;applyTabsBottomInset(new MainTabsLayout(),wrapper,20,0,0);
  if(wrapper.bottom!=0||getTabsBottomLiftDp()!=0||getTabsBottomOccupiedHeightDp()!=64||getTabsFabOffsetDp()!=64)
   throw new AssertionError("Material navigation changed");
 }
}
class MainTabsHelper{
 static int getMainTabsHeightWithMargins(){return 76;}
 static int getMainTabsHeight(){return 60;}static int getMainTabsMargin(){return 8;}
}
class AndroidUtilities{static int dp(int value){return value;}}
class View{int bottom;void setPadding(int l,int t,int r,int b){bottom=b;}int getMeasuredHeight(){return 1000;}int getMeasuredWidth(){return 500;}}
class MainTabsLayout extends View{}
class RectF{float top,bottom;void set(int l,int t,int r,int b){top=t;bottom=b;}}
'''.replace('METHODS',methods))

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
   if(expected ? alpha>80||alpha<20 : alpha<200)throw new AssertionError("Unreadable fallback");
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
