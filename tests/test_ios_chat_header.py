"""Run header policy and capture selection from production Java, without an APK."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java as run_plain_java
from glass_test_support import run_java

JAVA = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java'


@unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
class IosChatHeaderTests(unittest.TestCase):
    def test_panels_follow_header_switch_and_refresh_after_optical_changes(self):
        source=(JAVA / 'org/telegram/ui/Components/ChatActivityTopPanelLayout.java').read_text()
        methods=method(source,'    public void setIosHeaderGlass(')+'\n'+method(source,'    private void updateIosGlassStyle()')
        run_plain_java('''
class PrivacyCheck {
 boolean iosHeaderGlass;int glassRevision=Integer.MIN_VALUE;Boolean refractionEnabled;
 Drawable backgroundDrawable=new Drawable();
 METHODS
 public static void main(String[] args){
  var p=new PrivacyCheck();p.updateIosGlassStyle();if(p.backgroundDrawable.refreshes!=0)throw new AssertionError("Legacy changed");
  p.setIosHeaderGlass(true);p.updateIosGlassStyle();p.updateIosGlassStyle();
  if(p.backgroundDrawable.refreshes!=1)throw new AssertionError("Effect recreated each frame");
  IosLiquidGlassChatHeader.enabled=false;p.updateIosGlassStyle();
  if(p.backgroundDrawable.refreshes!=2||p.backgroundDrawable.enabled)throw new AssertionError("Power-saving fallback");
  LiquidGlassStyle.value++;p.updateIosGlassStyle();
  if(p.backgroundDrawable.refreshes!=3)throw new AssertionError("Shared settings stale");
  p.setIosHeaderGlass(false);p.updateIosGlassStyle();
  if(p.backgroundDrawable.refreshes!=3)throw new AssertionError("Disabled style changed");
  p.backgroundDrawable=null;p.setIosHeaderGlass(true);p.updateIosGlassStyle();
 }
}
class Drawable{int refreshes;boolean enabled;void updateColors(){}}
class LiquidGlassStyle{static int value;static int revision(){return value;}}
class IosLiquidGlassChatHeader{static boolean enabled=true;static boolean isEnabled(){return enabled;}static void refresh(Drawable d){d.refreshes++;d.enabled=enabled;}}
'''.replace('METHODS',methods).replace('app.freezgram.',''))

    def test_avatar_remains_clickable_when_the_menu_icon_is_hidden(self):
        source = (JAVA / 'org/telegram/ui/ActionBar/ActionBar.java').read_text()
        hit = method(source, '    private boolean isInsideIosHeaderAvatar(')
        dispatch = method(source, '    public boolean dispatchTouchEvent(MotionEvent ev)')
        run_java('''
class PrivacyCheck extends BaseView {
 boolean iosChatHeaderGlass=true,glassMode=true;
 AvatarContainer chatAvatarContainer=new AvatarContainer();
 Drawable glassDrawable=new Drawable(),glassDrawableBack,glassDrawableMenu;
 static View findChildUnder(Object parent,int x,int y,View excluded){return excluded==null?((PrivacyCheck)parent).chatAvatarContainer:null;}
 HIT
 DISPATCH
 public static void main(String[] args){
  PrivacyCheck p=new PrivacyCheck();
  if(!p.dispatchTouchEvent(new MotionEvent(325,30)))throw new AssertionError("Avatar menu tap swallowed");
  if(p.dispatchTouchEvent(new MotionEvent(275,30)))throw new AssertionError("Empty area intercepted");
  p.chatAvatarContainer.alpha=0;
  if(p.dispatchTouchEvent(new MotionEvent(325,30)))throw new AssertionError("Hidden avatar intercepted");
  p.chatAvatarContainer.alpha=1;p.iosChatHeaderGlass=false;
  if(p.dispatchTouchEvent(new MotionEvent(325,30)))throw new AssertionError("Legacy hit test changed");
 }
}
class BaseView {public boolean dispatchTouchEvent(MotionEvent e){return true;}}
class View {
 static final int VISIBLE=0;float alpha=1;
 int getVisibility(){return VISIBLE;}float getAlpha(){return alpha;}
 float getX(){return 0;}float getY(){return 0;}int getWidth(){return 40;}int getHeight(){return 40;}
}
class AvatarContainer extends View {
 boolean isAvatarCentered(){return true;}
 float getX(){return 50;}float getY(){return 5;}
 View getAvatarImageView(){return new View(){float getX(){return 255;}float getY(){return 5;}};}
}
class Drawable {Rect getBounds(){return new Rect();}}
class Rect {boolean contains(int x,int y){return x>=100&&x<=200&&y>=5&&y<=55;}}
class MotionEvent {static final int ACTION_DOWN=0;int x,y;MotionEvent(int x,int y){this.x=x;this.y=y;}int getAction(){return 0;}float getX(){return x;}float getY(){return y;}}
'''.replace('HIT',hit).replace('DISPATCH',dispatch.replace('    @Override\n','')))

    def test_ios_has_priority_over_material(self):
        source = (JAVA / 'app/exteraless/appearance/ChatHeaderUiHelper.java').read_text()
        policy = method(source, '    public static boolean isMaterial3ChatHeaderStyle()')
        run_java('''
class PrivacyCheck {
 POLICY
 public static void main(String[] args) {
  for(boolean ios:new boolean[]{false,true}) for(boolean material:new boolean[]{false,true}) {
   AppearanceConfig.ios=ios; AppearanceConfig.material=material;
   if(isMaterial3ChatHeaderStyle()!=(material&&!ios)) throw new AssertionError("iOS must keep its capsule when Material is also selected");
  }
 }
}
class AppearanceConfig {
 static boolean ios,material;
 static boolean iosChatHeader(){return ios;}
 static boolean newChatHeaderStyle(){return material;}
}
'''.replace('POLICY', policy))

    def test_refraction_requires_supported_platform_blur_and_power(self):
        path = JAVA / 'app/freezgram/IosLiquidGlassChatHeader.java'
        self.assertTrue(path.exists(), 'Dedicated header glass policy is missing')
        source = path.read_text()
        source = source[source.index('public final class'):].replace('public final class', 'final class', 1)
        run_java('''
class PrivacyCheck {
 public static void main(String[] args) {
  for(int sdk:new int[]{23,31,32,33,36}) for(boolean ios:new boolean[]{false,true})
  for(boolean blur:new boolean[]{false,true}) for(boolean saver:new boolean[]{false,true}) {
   Build.VERSION.SDK_INT=sdk; AppearanceConfig.ios=ios; SharedConfig.blur=blur; LiteMode.saver=saver;
   boolean expected=ios&&sdk>=33&&blur&&!saver;
   if(IosLiquidGlassChatHeader.isRequested()!=ios || IosLiquidGlassChatHeader.isEnabled()!=expected) throw new AssertionError("Unsafe glass fallback");
   BlurredBackgroundDrawableRenderNode d=new BlurredBackgroundDrawableRenderNode();
   d.enabled=sdk>=33;IosLiquidGlassChatHeader.refresh(d);
   if(d.enabled!=expected)throw new AssertionError("Stale refraction after power or blur changes");
   if(d.thickness!=12||d.intensity!=.55f)throw new AssertionError("Header lens parameters");
   for(boolean dark:new boolean[]{false,true}) {
    int alpha=IosLiquidGlassChatHeader.colors(null).background.getColor(null,dark)>>>24;
    if(expected ? alpha<15||alpha>30 : alpha<200)throw new AssertionError("Unreadable fallback or excessive glass tint");
   }
  }
  IosLiquidGlassChatHeader.refresh(null);
  IosLiquidGlassChatHeader.refresh(new BlurredBackgroundDrawable());
 }
}
class Build {static class VERSION {static int SDK_INT;}}
class AppearanceConfig {static boolean ios;static boolean iosChatHeader(){return ios;}}
class SharedConfig {static boolean blur;static boolean chatBlurEnabled(){return blur;}}
class LiteMode {static boolean saver;static boolean isPowerSaverApplied(){return saver;}}
class AndroidUtilities{static int dp(int value){return value;}static float dpf2(float value){return value;}}
class Theme{
 static class ResourcesProvider{}static int key_chat_topPanelBackground;
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

    def test_header_weak_capture_is_independent_of_global_glass(self):
        source = (JAVA / 'org/telegram/ui/Components/blur3/DownscaleScrollableNoiseSuppressor.java').read_text()
        draw = method(source, '    public void drawInline(Canvas canvas, int index)')
        run_java('''
class PrivacyCheck {
 static final int DRAW_GLASS=-2,DRAW_FROSTED_GLASS=-3,DRAW_FROSTED_GLASS_NO_SATURATION=-4,DRAW_HEADER_GLASS=-5;
 boolean isLiquidGlassEnabled,simpleMode,navigationGlassEnabled;int rectRenderNodesCount=1;
 java.util.ArrayList<SourcePart> rectRenderNodes=new java.util.ArrayList<>();
 RenderNode getRenderNode(int a,int b){return new RenderNode(a);}
 DRAW
 public static void main(String[] args) {
  for(boolean global:new boolean[]{false,true}) for(boolean simple:new boolean[]{false,true}) {
   PrivacyCheck p=new PrivacyCheck();p.isLiquidGlassEnabled=global;p.simpleMode=simple;p.navigationGlassEnabled=true;
   p.rectRenderNodes.add(new SourcePart());Canvas c=new Canvas();
   p.drawInline(c,DRAW_HEADER_GLASS);
   if(c.selected!=2 || c.depth!=0) throw new AssertionError("Header must get the weak output, even with global glass off");
   p.drawInline(c,DRAW_GLASS);
   if(c.selected!=(global||simple?0:1))throw new AssertionError("Legacy glass changed");
  }
 }
}
class Rect {int left,top,right,bottom;}
class SourcePart {Rect position=new Rect();}
class RenderNode {int index;RenderNode(int i){index=i;}}
class Canvas {
 int selected=-1,depth;
 boolean quickReject(int l,int t,int r,int b){return false;}
 void save(){depth++;}void restore(){depth--;}void translate(int x,int y){}
 void drawRenderNode(RenderNode n){selected=n.index;}
}
'''.replace('DRAW\n', draw+'\n'))
