"""Composer policy and surface geometry without an Android build."""
import unittest
import shutil
from pathlib import Path
from test_personal_privacy import method, run_java

JAVA = Path(__file__).resolve().parents[1] / "TMessagesProj/src/main/java"

@unittest.skipUnless(shutil.which("java"), "Java source launcher required")
class ComposerGlassTests(unittest.TestCase):
    def test_policy_and_surface_bounds(self):
        source = (JAVA / "app/freezgram/ChatComposerGlass.java").read_text()
        methods = "\n".join(method(source, sig) for sig in (
            "    public static boolean isRequested()", "    public static boolean isEnabled()",
            "    public static boolean useIosLayout(", "    public static void surfaceBounds("))
        run_java('''
class PrivacyCheck {
 METHODS
 public static void main(String[] args) {
  for(int style:new int[]{0,1,2}) for(int sdk:new int[]{23,31,33,36})
  for(boolean blur:new boolean[]{false,true}) for(boolean power:new boolean[]{false,true}) {
   AppearanceConfig.style=style; Build.VERSION.SDK_INT=sdk;SharedConfig.blur=blur;LiteMode.power=power;
   if(isRequested()!=(style!=0))throw new AssertionError("Default changed");
   if(isEnabled()!=(style!=0&&sdk>=33&&blur&&!power))throw new AssertionError("Unsafe fallback");
   if(useIosLayout(false,320)!=(style==1))throw new AssertionError("Wrong layout");
   if(useIosLayout(true,320)||useIosLayout(false,200))throw new AssertionError("Complex/narrow layout must remain whole");
  }
  for(int width:new int[]{240,320,412,800})for(int height:new int[]{44,88,180}) {
   Rect all=new Rect(0,100,width,100+height+14),field=new Rect(),left=new Rect(),right=new Rect();
   surfaceBounds(all,field,left,right,true);
   if(left.left!=0||left.right!=58||right.left!=width-58||right.right!=width)throw new AssertionError("Button bounds");
   if(left.height()!=58||right.height()!=58||left.bottom!=all.bottom)throw new AssertionError("Circles must stay bottom aligned");
   if(field.left!=50||field.right!=width-50||field.height()!=all.height())throw new AssertionError("Multiline field bounds");
   if(left.right-7>=field.left+7||field.right-7>=right.left+7)throw new AssertionError("Surfaces overlap");
   surfaceBounds(all,field,left,right,false);
   if(field.left!=all.left||field.right!=all.right||field.top!=all.top||field.bottom!=all.bottom||left.height()!=0||right.height()!=0)throw new AssertionError("Whole layout not restored");
  }
 }
 static int dp(int n){return n;}
}
class AppearanceConfig{static int style;static int chatComposerStyle(){return style;}}
class Build{static class VERSION{static int SDK_INT;}}
class SharedConfig{static boolean blur;static boolean chatBlurEnabled(){return blur;}}
class LiteMode{static boolean power;static boolean isPowerSaverApplied(){return power;}}
class Rect {
 int left,top,right,bottom;
 Rect(){} Rect(int l,int t,int r,int b){set(l,t,r,b);}
 void set(int l,int t,int r,int b){left=l;top=t;right=r;bottom=b;}
 void set(Rect r){set(r.left,r.top,r.right,r.bottom);}
 void setEmpty(){set(0,0,0,0);} int height(){return bottom-top;}
}
'''.replace("METHODS", methods).replace("AndroidUtilities.dp", "dp"))

    def test_glass_fallback_and_animation_alpha(self):
        source = (JAVA / "app/freezgram/ChatComposerGlass.java").read_text()
        methods = "\n".join(method(source, sig) for sig in (
            "    public static boolean isRequested()", "    public static boolean isEnabled()",
            "    public static BlurredBackgroundProvider colors(", "    public static void refresh("))
        container = (JAVA / "org/telegram/ui/Components/chat/ChatInputViewsContainer.java").read_text()
        alpha = method(container, "    public void setInputBubbleAlpha(")
        run_java('''
class PrivacyCheck {
 METHODS
 BlurredBackgroundDrawable blurredBackgroundDrawable=new BlurredBackgroundDrawable();
 BlurredBackgroundDrawable composerLeftDrawable=new BlurredBackgroundDrawable(),composerRightDrawable=new BlurredBackgroundDrawable();
 ALPHA
 public static void main(String[] args) {
  for(int style:new int[]{0,1,2}) for(int sdk:new int[]{23,31,32,33,36})
  for(boolean blur:new boolean[]{false,true}) for(boolean power:new boolean[]{false,true}) {
   AppearanceConfig.style=style;Build.VERSION.SDK_INT=sdk;SharedConfig.blur=blur;LiteMode.power=power;
   boolean enabled=style!=0&&sdk>=33&&blur&&!power;
   BlurredBackgroundDrawableRenderNode drawable=new BlurredBackgroundDrawableRenderNode();
   drawable.enabled=sdk>=33;refresh(drawable);
   if(drawable.enabled!=enabled||drawable.thickness!=12||drawable.intensity!=.55f)throw new AssertionError("Lens fallback");
   for(boolean dark:new boolean[]{false,true}){
    int alpha=colors(null).background.getColor(null,dark)>>>24;
    if(enabled?(alpha<25||alpha>50):alpha<230)throw new AssertionError("Surface contrast");
   }
  }
  refresh(null);refresh(new BlurredBackgroundDrawable());
  var container=new PrivacyCheck();
  for(int a:new int[]{0,64,128,255}){
   container.setInputBubbleAlpha(a);
   if(container.blurredBackgroundDrawable.alpha!=a||container.composerLeftDrawable.alpha!=a||container.composerRightDrawable.alpha!=a)throw new AssertionError("Detached circles during animation");
  }
 }
}
class AppearanceConfig{static int style;static int chatComposerStyle(){return style;}}
class Build{static class VERSION{static int SDK_INT;}}
class SharedConfig{static boolean blur;static boolean chatBlurEnabled(){return blur;}}
class LiteMode{static boolean power;static boolean isPowerSaverApplied(){return power;}}
class AndroidUtilities{static int dp(int n){return n;}static float dpf2(float n){return n;}}
class Theme {
 static class ResourcesProvider{} static int key_chat_messagePanelBackground;
 static int getColor(int key,ResourcesProvider r){return 0xffeeeeee;}
 static int multAlpha(int color,float alpha){return (color&0xffffff)|((int)(255*alpha)<<24);}
}
class BlurredBackgroundDrawable {
 int alpha,thickness;float intensity;
 void setAlpha(int a){alpha=a;}void setThickness(int t){thickness=t;}void setIntensity(float i){intensity=i;}
}
class BlurredBackgroundDrawableRenderNode extends BlurredBackgroundDrawable {
 boolean enabled;void setLiquidGlassEffectAllowed(boolean e){enabled=e;}
}
class BlurredBackgroundProvider {
 interface ColorProvider{int getColor(Theme.ResourcesProvider r,boolean dark);}
 ColorProvider background;
}
class BlurredBackgroundProviderBuilder extends BlurredBackgroundProvider {
 BlurredBackgroundProviderBuilder(Theme.ResourcesProvider r){}
 BlurredBackgroundProviderBuilder setBackgroundColor(ColorProvider p){background=p;return this;}
 BlurredBackgroundProviderBuilder setStrokeColorTop(int a,int b){return this;}
 BlurredBackgroundProviderBuilder setStrokeColorBottom(int a,int b){return this;}
 BlurredBackgroundProviderBuilder setStrokeWidth(float a,float b){return this;}
 BlurredBackgroundProviderBuilder setShadowColor(int a,int b){return this;}
 BlurredBackgroundProviderBuilder setShadowLayer(float a,float b,float c){return this;}
 BlurredBackgroundProvider build(){return this;}
}
'''.replace("METHODS",methods).replace("ALPHA",alpha))

    def test_ios_falls_back_for_special_controls_but_keeps_channel_notifications(self):
        source = (JAVA / "org/telegram/ui/Components/ChatActivityEnterView.java").read_text()
        methods = "\n".join(method(source,sig) for sig in (
            "    private static boolean composerControlVisible(", "    private boolean canUseIosComposerLayout("))
        policy = method((JAVA / "app/freezgram/ChatComposerGlass.java").read_text(), "    public static boolean useIosLayout(")
        run_java('''
class PrivacyCheck {
 static int VISIBLE=0;
 boolean isStories,isLiveComment,recordingAudioVideo,stickers;
 Object editingMessageObject;
 View recordedAudioPanel,recordPanel,topView,senderSelectView,botCommandsMenuButton,
 botWebViewButton,botButton,deleteRichDraftButton,richDraftPreview;
 View attachButton=new View(),emojiButton=new View();
 METHODS
 boolean isStickersExpanded(){return stickers;}
 public static void main(String[] args) {
  var enter=new PrivacyCheck();
  if(!enter.canUseIosComposerLayout(320)||enter.canUseIosComposerLayout(200))throw new AssertionError("Normal input geometry");
  for(int condition=0;condition<13;condition++){
   enter=new PrivacyCheck();
   switch(condition){
    case 0:enter.isStories=true;break;case 1:enter.isLiveComment=true;break;
    case 2:enter.recordingAudioVideo=true;break;case 3:enter.editingMessageObject=new Object();break;
    case 4:enter.recordedAudioPanel=new View();break;case 5:enter.recordPanel=new View();break;
    case 6:enter.topView=new View();break;case 7:enter.senderSelectView=new View();break;
    case 8:enter.botWebViewButton=new View();break;case 9:enter.botButton=new View();break;
    case 10:enter.deleteRichDraftButton=new View();break;case 11:enter.richDraftPreview=new View();break;
    case 12:enter.stickers=true;break;
   }
   if(enter.canUseIosComposerLayout(320))throw new AssertionError("Special controls overlap: "+condition);
  }
 }
}
class View{int getVisibility(){return 0;}Object getTag(){return null;}}
class AndroidUtilities{static float density=1;}
class ChatComposerGlass{POLICY}
class AppearanceConfig{static int chatComposerStyle(){return 1;}}
'''.replace("METHODS",methods).replace("POLICY",policy).replace("app.freezgram.ChatComposerGlass", "ChatComposerGlass"))
