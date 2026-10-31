import shutil,unittest
from pathlib import Path
from test_personal_privacy import method,run_java
JAVA=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java'
@unittest.skipUnless(shutil.which('java'),'Java source launcher required')
class GreetingWallpaperTests(unittest.TestCase):
 def test_greeting_sticker_returns_after_constrained_measurement(self):
  source=(JAVA/'org/telegram/ui/Components/ChatGreetingsView.java').read_text()
  measure=method(source,'    protected void onMeasure(')
  run_java('''
class PrivacyCheck extends Base{
 static int VISIBLE=0,GONE=8;boolean ignoreLayot,preview,showSticker=true;int measured;
 View stickerContainer=new View(),stickerToSendView=new View(),descriptionView=new View();
 int getMeasuredHeight(){return measured;}
 MEASURE
 public static void main(String[] args){
  var p=new PrivacyCheck();p.onMeasure(0,200);
  if(p.stickerContainer.visibility!=GONE)throw new AssertionError("Constrained layout did not hide sticker");
  p.onMeasure(0,400);
  if(p.stickerContainer.visibility!=VISIBLE||p.stickerToSendView.visibility!=VISIBLE)throw new AssertionError("Sticker stays hidden after space returns");
  p.onMeasure(0,0);if(p.stickerContainer.visibility!=VISIBLE)throw new AssertionError("Unspecified height hides greetings");
  p.showSticker=false;p.onMeasure(0,400);if(p.stickerContainer.visibility!=GONE)throw new AssertionError("Explicit opt-out ignored");
 }
}
class Base{protected void onMeasure(int w,int h){PrivacyCheck p=(PrivacyCheck)this;p.measured=p.stickerContainer.visibility==0?300:80;}}
class View{static int VISIBLE=0,GONE=8;int visibility;void setVisibility(int v){visibility=v;}}
class MeasureSpec{static int UNSPECIFIED=0;static int getMode(int n){return n==0?0:1;}static int getSize(int n){return n;}}
'''.replace('MEASURE',measure))

 def test_base_retains_wallpaper_color_and_negative_intensity_semantics(self):
  source=(JAVA/'org/telegram/ui/Components/SizeNotifierFrameLayout.java').read_text()
  helper=method(source,'    private static int wallpaperBaseColor(')
  run_java('''
class PrivacyCheck{
 HELPER
 public static void main(String[] args){
  if(wallpaperBaseColor(new ColorDrawable())!=0xff123456)throw new AssertionError("Solid wallpaper base lost its color");
  var m=new MotionBackgroundDrawable();if(wallpaperBaseColor(m)!=0xff654321)throw new AssertionError("Gradient wallpaper got dark theme underlay");
  m.intensity=-50;if(wallpaperBaseColor(m)!=0xff000000)throw new AssertionError("Negative intensity design changed");
  if(wallpaperBaseColor(null)!=0xff202020)throw new AssertionError("Unknown wallpaper fallback lost");
 }
}
class Drawable{}class ColorDrawable extends Drawable{int getColor(){return 0x80123456;}}
class MotionBackgroundDrawable extends Drawable{int intensity=50;int getIntensity(){return intensity;}int[] getColors(){return new int[]{0x00654321,0xffaaaaaa};}}
class Theme{static int key_windowBackgroundWhite;static int getColor(int k){return 0xff202020;}}
'''.replace('HELPER',helper))
