"""Gift optics are independent and preview capture excludes gift contents."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java
JAVA=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java'

@unittest.skipUnless(shutil.which('java'),'Java source launcher required')
class GiftSettingsTests(unittest.TestCase):
 def test_gift_profile_independent_and_zero_opacity_is_supported(self):
  source=(JAVA/'app/freezgram/GiftGlassStyle.java').read_text()
  helpers='\n'.join(method(source,m) for m in ['    public static int blurRadiusDp()', '    public static int revision()', '    public static float opacity()', '    public static void configure('])
  run_java('''
class PrivacyCheck{
 HELPERS
 public static void main(String[] args){
  var d=new BlurredBackgroundDrawable();configure(d);int previous=revision();
  if(d.intensity!=.7f||blurRadiusDp()!=24||opacity()!=.25f)throw new AssertionError("Gift defaults missing");
  AppearanceConfig.transparency=100;
  if(opacity()!=0||revision()==previous)throw new AssertionError("Gift transparency ignored");previous=revision();
  AppearanceConfig.intensity=0;configure(d);
  if(d.intensity!=0||revision()==previous)throw new AssertionError("Gift intensity ignored");
  AppearanceConfig.blur=0;if(blurRadiusDp()!=0)throw new AssertionError("Gift blur ignored");
 }
}
class AppearanceConfig{static int blur=24,intensity=70,transparency=75;static int giftGlassBlur(){return blur;}static int giftGlassIntensity(){return intensity;}static int giftGlassTransparency(){return transparency;}}
class BlurredBackgroundDrawable{float intensity;void setThickness(int n){}void setIntensity(float f){intensity=f;}}
class AndroidUtilities{static int dp(int n){return n;}}
'''.replace('HELPERS',helpers))

 def test_style_preserves_legacy_opt_out_and_all_three_selections(self):
  source=(JAVA/'app/freezgram/GiftGlassStyle.java').read_text()
  policy=method(source,'    public static int style()')
  run_java('''
class PrivacyCheck{
 static int ORDINARY=0;
 POLICY
 public static void main(String[] args){
  for(int style=0;style<=2;style++)for(boolean legacy:new boolean[]{false,true}){
   AppearanceConfig.style=style;AppearanceConfig.legacy=legacy;
   if(style()!=(legacy?style:0))throw new AssertionError("Legacy opt-out or card style ignored");
  }
 }
}
class AppearanceConfig{static int style;static boolean legacy;static boolean giftCardsGlass(){return legacy;}static int giftCardStyle(){return style;}}
'''.replace('POLICY',policy))

 def test_soft_surface_is_opaque_and_nft_finish_keeps_backdrop_visible(self):
  source=(JAVA/'app/freezgram/GiftGlassStyle.java').read_text()
  a=source.index('    public static final class SoftCard')
  b=source.index('    public static int blurRadiusDp()',a)
  render=source[a:b]+method(source,'    public static float cornerRadius(')
  run_java('''
class PrivacyCheck{
 RENDER
 public static void main(String[] args){
  var card=new SoftCard();var c=new Canvas();var r=new RectF();r.right=200;r.bottom=220;
  card.draw(c,r,20,null,1f,false);var gradient=c.gradient;
  if((gradient.top>>>24)!=255||(gradient.bottom>>>24)!=255||c.alpha!=255||c.edges!=1)throw new AssertionError("Soft card must be opaque");
  card.draw(c,r,20,null,1f,false);if(c.gradient!=gradient)throw new AssertionError("Gradient allocated every frame");
  card.draw(c,r,20,null,1f,true);
  if((c.gradient.top>>>24)>=255||(c.gradient.bottom>>>24)>=255)throw new AssertionError("NFT backdrop overwritten by opaque finish");
  var another=new SoftCard();another.draw(c,r,20,null,1f,false);
  if(c.gradient==gradient)throw new AssertionError("Cards share mutable geometry");
  var old=c.gradient;AppearanceConfig.angle=90;another.draw(c,r,20,null,1f,false);
  if(c.gradient==old)throw new AssertionError("New gradient direction did not invalidate shader");
  AppearanceConfig.opacity=40;another.draw(c,r,20,null,1f,false);
  if(c.alpha!=102)throw new AssertionError("Gradient opacity ignored");
 }
}
class Canvas{LinearGradient gradient;int alpha,edges;void drawRoundRect(RectF r,float x,float y,Paint p){if(p.shader!=null){gradient=p.shader;alpha=p.alpha;}else edges++;}}
class Paint{static int ANTI_ALIAS_FLAG=1;enum Style{FILL,STROKE}LinearGradient shader;int alpha;Paint(int f){}void setShader(LinearGradient g){shader=g;}void setStyle(Style s){}void setAlpha(int a){alpha=a;}void setColor(int c){}void setStrokeWidth(float w){}}
class RectF{float left,top,right,bottom;void set(RectF r){left=r.left;top=r.top;right=r.right;bottom=r.bottom;}void inset(float x,float y){}}
class LinearGradient{int top,bottom;LinearGradient(float l,float t,float r,float b,int c,int d,Shader.TileMode m){top=c;bottom=d;}}
class Shader{enum TileMode{CLAMP}}
class Theme{static int key_windowBackgroundWhiteBlueText=1,key_windowBackgroundWhite=2,key_chat_serviceText=3;static class ResourcesProvider{}static int getColor(int key,Object p){return key==1?0xff448acc:0xffffffff;}}
class ColorUtils{static double calculateLuminance(int c){return c==0xffffffff?1:0;}static int blendARGB(int a,int b,float p){return (int)(a*(1.0-p)+b*p);}}
class AppearanceConfig{static int corners=-1,strength=32,angle=45,opacity=100,outline=19;static int giftCardCorners(){return corners;}static int giftGradientStrength(){return strength;}static int giftGradientAngle(){return angle;}static int giftGradientOpacity(){return opacity;}static int giftGradientOutline(){return outline;}}
class AndroidUtilities{static float dpf2(float f){return f;}}
'''.replace('RENDER',render))

 def test_official_preview_selects_available_catalog_gift_with_real_sticker(self):
  source=(JAVA/'app/freezgram/GiftCardPreview.java').read_text()
  select=method(source,'    static TL_stars.StarGift selectGift(')
  run_java('''
class PrivacyCheck{
 SELECT
 public static void main(String[] args){
  var expensive=new TL_stars.TL_starGift();expensive.stars=50;
  var bear=new TL_stars.TL_starGift();bear.stars=15;
  var sold=new TL_stars.TL_starGift();sold.stars=1;sold.sold_out=true;
  var missing=new TL_stars.TL_starGift();missing.stars=1;missing.sticker=null;
  var auction=new TL_stars.TL_starGift();auction.stars=1;auction.auction=true;
  var unique=new TL_stars.StarGift();unique.stars=1;
  if(selectGift(java.util.List.of(expensive,bear,sold,missing,auction,unique))!=bear)throw new AssertionError("Preview does not use an available official catalog gift");
  if(selectGift(java.util.List.of(sold,missing,auction,unique))!=null)throw new AssertionError("Preview invented a gift when catalog unavailable");
 }
}
class TL_stars{static class StarGift{long stars;Object sticker=new Object();boolean sold_out,auction;}static class TL_starGift extends StarGift{}}
'''.replace('SELECT',select))

 def test_ordinary_opacity_and_rounding_do_not_mutate_shared_theme_paints(self):
  source=(JAVA/'app/freezgram/GiftGlassStyle.java').read_text()
  helpers=method(source,'    public static void drawOrdinary(')+method(source,'    public static float cornerRadius(')
  run_java('''
class PrivacyCheck{
 HELPERS
 public static void main(String[] args){
  var c=new Canvas();var fill=new Paint();var shade=new Paint();
  for(int opacity:new int[]{0,50,100}){
   AppearanceConfig.opacity=opacity;drawOrdinary(c,new RectF(),20,fill,shade);
   if(c.alpha!=(int)(255*opacity/100f)||c.fills!=2||c.depth!=0||fill.alpha!=200||shade.alpha!=200)throw new AssertionError("Wrong ordinary opacity or shared paint modified");
  }
  AppearanceConfig.corners=8;drawOrdinary(c,new RectF(),20,fill,null);
  if(c.radius!=8||c.fills!=1)throw new AssertionError("Custom corners or optional darken ignored");
 }
}
class Canvas{int alpha,depth,fills;float radius;void saveLayerAlpha(RectF r,int a){alpha=a;depth++;fills=0;}void drawRoundRect(RectF r,float x,float y,Paint p){radius=x;fills++;}void restore(){depth--;}}
class Paint{int alpha=200;}class RectF{}
class AppearanceConfig{static int opacity=100,corners=-1;static int giftOrdinaryOpacity(){return opacity;}static int giftCardCorners(){return corners;}}
class AndroidUtilities{static float dpf2(int n){return n;}}
'''.replace('HELPERS',helpers))

 def test_sending_preview_only_captures_wallpaper_when_enabled(self):
  source=(JAVA/'org/telegram/ui/Gifts/SendGiftSheet.java').read_text()
  capture=method(source,'    private void prepareGiftGlass(').replace('app.freezgram.SmallElementsGlass','SmallElementsGlass')
  run_java('''
class PrivacyCheck{
 Source giftPreviewSource=new Source();Chat chatView=new Chat();
 CAPTURE
 public static void main(String[] args){
  for(boolean enabled:new boolean[]{false,true})for(boolean hardware:new boolean[]{false,true})for(int size:new int[]{0,400}){
   var p=new PrivacyCheck();SmallElementsGlass.enabled=enabled;var c=new Canvas();c.hardware=hardware;p.chatView.size=size;
   p.prepareGiftGlass(c);boolean expected=enabled&&hardware&&size>0;
   if(p.chatView.captures!=(expected?1:0)||p.giftPreviewSource.recorded!=expected)throw new AssertionError("Preview captured contents or ignored fallback");
  }
 }
}
class Canvas{boolean hardware;boolean isHardwareAccelerated(){return hardware;}}
class Source{boolean recorded;Canvas beginRecording(int w,int h){return new Canvas();}void endRecording(){recorded=true;}}
class Chat{int size,captures;int getWidth(){return size;}int getHeight(){return size;}boolean drawWallpaperForGlass(Canvas c){captures++;return true;}}
class SmallElementsGlass{static boolean enabled;static boolean areGiftCardsEnabled(){return enabled;}}
'''.replace('CAPTURE',capture))
