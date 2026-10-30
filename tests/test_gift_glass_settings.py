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
