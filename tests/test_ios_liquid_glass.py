"""Exercise the actual navigation glass policy and color fallback with Android stubs."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method
from glass_test_support import run_java


class IosGlassTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_navigation_gets_weak_blur_without_changing_other_glass_outputs(self):
        path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/org/telegram/ui/Components/blur3/DownscaleScrollableNoiseSuppressor.java'
        text=path.read_text()
        constructor=method(text, '    public DownscaleScrollableNoiseSuppressor(boolean simple, boolean allowNoiseSuppress, boolean navigationGlassEnabled)')
        selector=method(text, '    private RenderNode getRenderNode(int a, int b)')
        draw=method(text, '    public void drawNavigationGlass(')+'\n'+method(text, '    public boolean setNavigationGlassBlur(')
        def inner_method(signature):
            start=text.index(signature)
            return text[start:text.index('\n        }',start)+len('\n        }')]
        source_constructor=inner_method('        private SourcePart()')
        invalidate=inner_method('        public void invalidate()')
        run_java('''
class PrivacyCheck {
 public static void main(String[] args) {
  for(boolean global:new boolean[]{false,true})for(boolean nav:new boolean[]{false,true})
  for(boolean simple:new boolean[]{false,true}){
   LiteMode.enabled=global;
   var s=new DownscaleScrollableNoiseSuppressor(simple,false,nav);
   var part=s.new SourcePart();s.rectRenderNodes.add(part);part.invalidate();
   if((part.renderNodesForGlass!=null)!=global)throw new AssertionError("Weak output allocation");
   if(part.renderNodesForGlass!=null&&part.renderNodesForGlass.radius!=6)throw new AssertionError("Weak radius");
   if(part.renderNodesForBlur.radius<38)throw new AssertionError("Frosted blur changed");
   if(s.getRenderNode(0,0)!=(global?part.renderNodesForGlass.renderNodeRestored[0]:part.renderNodesForBlur.renderNodeRestored[0]))
    throw new AssertionError("Legacy glass selection changed");
   if(part.renderNodesForBlur.input!=(global?part.renderNodesForGlass.renderNodeRestored[0]:part.renderNode))
    throw new AssertionError("Legacy blur input changed");
   if(nav&&s.getRenderNode(2,0)!=part.renderNodesForNavigation.renderNodeRestored[0])throw new AssertionError("Navigation still strongly blurred");
   Canvas c=new Canvas();RectF area=new RectF();s.drawNavigationGlass(c,area,6);
   if(nav) {
    s.drawNavigationGlass(c,area,20);
    if(part.renderNodesForNavigation.radius!=20||part.renderNodesForBlur.radius<38)throw new AssertionError("Blur adjustment isolation");
    s.drawNavigationGlass(c,area,0);
    if(part.renderNodesForNavigation.radius!=0||part.renderNodesForNavigation.scaleX!=1)throw new AssertionError("Zero blur");
   }
   if(nav?(c.node!=s.resultRenderNodes[2]||c.clip!=area||c.depth!=0):c.node!=null)throw new AssertionError("Navigation capture isolation");
   area.empty=true;c.node=null;s.drawNavigationGlass(c,area,6);
   if(c.node!=null)throw new AssertionError("Empty bounds drawn");
  }
 }
}
class DownscaleScrollableNoiseSuppressor {
 boolean isLiquidGlassEnabled,simpleMode,navigationGlassEnabled,allowNoiseSuppress;int k;
 RenderNode[] resultRenderNodes;float navigationBlurRadius=6;
 java.util.ArrayList<SourcePart> rectRenderNodes=new java.util.ArrayList<>();
 CONSTRUCTOR
 SELECTOR
 DRAW
 static float dpf2(float value){return value;}
 class SourcePart {
  RenderNode renderNode=new RenderNode(null);DownscaledRenderNode renderNodesForGlass,renderNodesForBlur,renderNodesForNavigation;
  SOURCE_CONSTRUCTOR
  INVALIDATE
 }
 class DownscaledRenderNode {
  float radius;int scaleX;RenderNode input;RenderNode[] renderNodeRestored={new RenderNode(null)};
  DownscaledRenderNode(String name,int effects){}
  DownscaledRenderNode(String name,int effects,boolean simple){}
  void setScale(int x,int y){scaleX=x;}
  void setPrimaryEffectBlur(float r){radius=r;}
  void setPrimaryEffectBlur(float r,Object e){radius=r;}
  void setSecondaryEffect(int i,Object e){}
  void invalidateRenderNodes(RenderNode node){input=node;}
 }
}
class RenderNode{RenderNode(String name){}boolean hasDisplayList(){return false;}}
class LiteMode{static boolean enabled;static int FLAG_LIQUID_GLASS;static boolean isEnabled(int flag){return enabled;}}
class RenderNodeEffects{static Object getSaturationX3RenderEffect(){return null;}}
class RectF{boolean empty;boolean isEmpty(){return empty;}}
class Canvas{
 int depth;RectF clip;RenderNode node;
 void save(){depth++;}void restore(){depth--;}void clipRect(RectF r){clip=r;}void drawRenderNode(RenderNode n){node=n;}
}
'''.replace('SOURCE_CONSTRUCTOR',source_constructor).replace('CONSTRUCTOR',constructor)
           .replace('SELECTOR',selector).replace('DRAW',draw).replace('INVALIDATE',invalidate)
           .replace('private RenderNode getRenderNode','RenderNode getRenderNode')
           .replace('private SourcePart()','SourcePart()'))

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
  AppearanceConfig.lift=40;AppearanceConfig.width=80;
  applyTabsBottomInset(new MainTabsLayout(),wrapper,20,0,0);setBlurBounds(rect,window,20);
  if(wrapper.left!=50||wrapper.bottom!=60||getTabsBottomOccupiedHeightDp()!=116||getTabsFabOffsetDp()!=108)
   throw new AssertionError("Custom gap not propagated");
  material=true;applyTabsBottomInset(new MainTabsLayout(),wrapper,20,0,0);
  if(wrapper.bottom!=0||getTabsBottomLiftDp()!=0||getTabsBottomOccupiedHeightDp()!=64||getTabsFabOffsetDp()!=64)
   throw new AssertionError("Material navigation changed");
 }
}
class AppearanceConfig{static int lift=12,width=100;static int navigationPanelLift(){return lift;}static int navigationPanelWidth(){return width;}}
class MainTabsHelper{
 static int getMainTabsHeightWithMargins(){return 76;}
 static int getMainTabsHeight(){return 60;}static int getMainTabsMargin(){return 8;}
}
class AndroidUtilities{static int dp(int value){return value;}}
class View{int bottom,left;void setPadding(int l,int t,int r,int b){left=l;bottom=b;}int getMeasuredHeight(){return 1000;}int getMeasuredWidth(){return 500;}}
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
   if(expected ? alpha>30||alpha<15 : alpha<200)throw new AssertionError("Unreadable fallback");
   int darkAlpha=provider.background.getColor(null,true)>>>24;
   if(expected ? darkAlpha>30||darkAlpha<20 : darkAlpha<200)throw new AssertionError("Dark tint");
  }
  BlurredBackgroundDrawable drawable=new BlurredBackgroundDrawable();
  IosLiquidGlassNavigation.configure(drawable);
  if(drawable.thickness!=12||drawable.intensity!=.55f)throw new AssertionError("Refraction settings");
  for(int value:new int[]{0,25,90,100}){
   int before=LiquidGlassStyle.revision();
   AppearanceConfig.transparency=value;AppearanceConfig.intensity=value;AppearanceConfig.blur=value%31;
   if(LiquidGlassStyle.revision()==before)throw new AssertionError("Stale style revision");
   if(Math.abs(IosLiquidGlassNavigation.overlayAlpha(false)-(100-value)/100f)>.0001f)throw new AssertionError("Transparency direction");
   IosLiquidGlassNavigation.configure(drawable);
   if(drawable.intensity!=value/100f||IosLiquidGlassNavigation.blurRadiusDp()!=value%31)throw new AssertionError("Saved values ignored");
  }
 }
}
class Build{static class VERSION{static int SDK_INT;}}
class MainTabsUiHelper{static boolean ios;static boolean isIosNavigationBar(){return ios;}}
class AppearanceConfig{
 static boolean glass;static int blur=6,intensity=55,transparency=-1;
 static boolean iosLiquidGlassNavigation(){return glass;}
 static int navigationGlassBlur(){return blur;}
 static int navigationGlassIntensity(){return intensity;}
 static int navigationGlassTransparency(){return transparency;}
}
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
