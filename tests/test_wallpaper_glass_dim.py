"""Wallpaper dim is composited in the wallpaper source before foreground content."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import run_java, method


class WallpaperDimTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_displayed_wallpaper_capture_and_switch_fallback(self):
        path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/org/telegram/ui/Components/chat/WallpaperBitmapProvider.java'
        factory=method(path.read_text(),'    public BlurredBackgroundSource withRenderedWallpaper(').replace('app.exteraless.appearance.AppearanceConfig','AppearanceConfig')
        run_java('''
class PrivacyCheck {
 FACTORY
 public static void main(String[] args){
  var p=new PrivacyCheck();var raw=new Source();
  var wrapped=p.withRenderedWallpaper(raw,c->{c.displayed++;return true;});
  Canvas c=new Canvas();AppearanceConfig.enabled=true;wrapped.draw(c,10,20,30,40);
  if(c.displayed!=1||c.raw!=0||c.depth!=0||c.left!=10||c.bottom!=40)throw new AssertionError("Capture must use displayed wallpaper only");
  AppearanceConfig.enabled=false;wrapped.draw(c,10,20,30,40);
  if(c.displayed!=1||c.raw!=1||c.depth!=0)throw new AssertionError("Switch must restore raw image");
  AppearanceConfig.enabled=true;
  p.withRenderedWallpaper(raw,canvas->false).draw(c,0,0,1,1);
  if(c.raw!=2||c.depth!=0)throw new AssertionError("Unlaid-out background needs fallback");
 }
}
class AppearanceConfig{static boolean enabled;static boolean glassWallpaperDim(){return enabled;}}
interface BlurredBackgroundSource{void draw(Canvas c,float l,float t,float r,float b);}
class BlurredBackgroundSourceWrapped implements BlurredBackgroundSource{
 BlurredBackgroundSource source;void setSource(BlurredBackgroundSource s){source=s;}
 public void draw(Canvas c,float l,float t,float r,float b){source.draw(c,l,t,r,b);}
}
class Source implements BlurredBackgroundSource{public void draw(Canvas c,float l,float t,float r,float b){c.raw++;}}
class Canvas{int depth,displayed,raw;float left,bottom;void save(){depth++;}void restore(){depth--;}void clipRect(float l,float t,float r,float b){left=l;bottom=b;}}
'''.replace('FACTORY',factory))

    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_dim_wrap_preserves_source_and_draws_only_the_capture_bounds(self):
        path = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java/org/telegram/ui/Components/chat/WallpaperBitmapProvider.java'
        source = path.read_text()
        start = source.index('    private static final class DimmedWallpaperSource')
        end = source.index('\n    private final BitmapMemoizedMetadata', start)
        wrapper = source[start:end].replace('app.exteraless.appearance.AppearanceConfig','AppearanceConfig')
        run_java('''
class PrivacyCheck {
 WRAPPER
 public static void main(String[] args) {
  for(float dim:new float[]{-1,0,.5f,1,2}) {
   var original=new Source();var wrapped=new DimmedWallpaperSource(original,dim);
   var canvas=new Canvas();wrapped.draw(canvas,10,20,110,220);
   int expected=(int)(255*Math.max(0,Math.min(1,dim)));
   if(canvas.alpha!=expected||!canvas.order.equals("wallpaper,dim"))throw new AssertionError("Wrong dim composition");
   if(canvas.left!=10||canvas.top!=20||canvas.right!=110||canvas.bottom!=220)throw new AssertionError("Dim escaped capture bounds");
   AppearanceConfig.dim=false;wrapped.draw(canvas,10,20,110,220);
   if(canvas.alpha!=0)throw new AssertionError("Dim toggle ignored");
   AppearanceConfig.dim=true;wrapped.draw(canvas,10,20,110,220);
   if(canvas.alpha!=expected)throw new AssertionError("Dim not restored");
   if(wrapped.getSource()!=original||original.color!=0xff8090a0)throw new AssertionError("Wallpaper source modified");
  }
 }
}
interface BlurredBackgroundSource{void draw(Canvas c,float l,float t,float r,float b);}
class BlurredBackgroundSourceWrapped implements BlurredBackgroundSource{
 BlurredBackgroundSource source;void setSource(BlurredBackgroundSource s){source=s;}BlurredBackgroundSource getSource(){return source;}
 public void draw(Canvas c,float l,float t,float r,float b){source.draw(c,l,t,r,b);}
}
class Source implements BlurredBackgroundSource{
 final int color=0xff8090a0;
 public void draw(Canvas c,float l,float t,float r,float b){c.order="wallpaper";}
}
class AppearanceConfig{static boolean dim=true;static boolean glassWallpaperDim(){return dim;}}
class Color{static final int BLACK=0xff000000;}
class Paint{int color;void setColor(int c){color=c;}void setAlpha(int a){color=(color&0xffffff)|(a<<24);}int getColor(){return color;}}
class Canvas{
 String order="";float left,top,right,bottom;int alpha;
 void drawRect(float l,float t,float r,float b,Paint p){left=l;top=t;right=r;bottom=b;alpha=p.getColor()>>>24;order+=",dim";}
}
'''.replace('WRAPPER', wrapper))
