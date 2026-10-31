"""Fast wallpaper rendering must preserve semantic wrappers such as dimming."""
import shutil,unittest
from pathlib import Path
from test_personal_privacy import method,run_java
SOURCE=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/org/telegram/ui/Components/blur3/drawable/BlurredBackgroundDrawable.java'

@unittest.skipUnless(shutil.which('java'),'Java source launcher required')
class WallpaperWrapperTests(unittest.TestCase):
 def test_fast_path_and_fallback_preserve_dimming_wrappers(self):
  source=SOURCE.read_text()
  helpers=method(source,'    public BlurredBackgroundSource getUnwrappedSource()')+method(source,'    protected void drawSource(')
  run_java('''
class PrivacyCheck{
 BlurredBackgroundSource source;Bound boundProps=new Bound();int backgroundColor;String used;Object received;
 BlurredBackgroundSource getSource(){return source;}
 void drawSourceColorImpl(Canvas c,int n){used="opaque";}
 void drawSourceColor(Canvas c,BlurredBackgroundSourceColor s){used="color";}
 void drawSourceBitmap(Canvas c,BlurredBackgroundSourceBitmap s){used="bitmap";}
 void drawSourceRenderNode(Canvas c,BlurredBackgroundSourceRenderNode s){used="node";}
 void drawSourceAny(Canvas c,BlurredBackgroundSource s){used="any";received=s;s.draw(c);}
 HELPERS
 public static void main(String[] args){
  var p=new PrivacyCheck();var raw=new BlurredBackgroundSourceBitmap();var dim=new Dimmed(raw);var rendered=new Rendered(dim);
  p.source=new BlurredBackgroundSourceWrapped(raw);
  if(p.getUnwrappedSource()!=raw)throw new AssertionError("Plain wrapper lost fast path");
  for(var s:new BlurredBackgroundSource[]{dim,rendered,new BlurredBackgroundSourceWrapped(dim),new BlurredBackgroundSourceWrapped(rendered)}){
   p.source=s;Object expected=s instanceof Rendered||s instanceof Dimmed?s:((BlurredBackgroundSourceWrapped)s).input;
   if(p.getUnwrappedSource()!=expected)throw new AssertionError("Fast fade bypassed processed wallpaper");
   var c=new Canvas();p.drawSource(c,s);
   if(!p.used.equals("any")||p.received!=expected||c.dim!=1)throw new AssertionError("Fallback dropped or doubled wallpaper dim");
  }
  p.drawSource(new Canvas(),new BlurredBackgroundSourceWrapped(raw));if(!p.used.equals("bitmap"))throw new AssertionError("Raw bitmap fallback regressed");
  p.source=null;if(p.getUnwrappedSource()!=null)throw new AssertionError("Null source changed");
 }
}
interface BlurredBackgroundSource{void draw(Canvas c);}
class BlurredBackgroundSourceWrapped implements BlurredBackgroundSource{BlurredBackgroundSource input;BlurredBackgroundSourceWrapped(BlurredBackgroundSource s){input=s;}BlurredBackgroundSource getSource(){return input;}public void draw(Canvas c){if(input!=null)input.draw(c);}}
class Dimmed extends BlurredBackgroundSourceWrapped{Dimmed(BlurredBackgroundSource s){super(s);}public void draw(Canvas c){super.draw(c);c.dim++;}}
class Rendered extends BlurredBackgroundSourceWrapped{Rendered(BlurredBackgroundSource s){super(s);}public void draw(Canvas c){super.draw(c);}}
class BlurredBackgroundSourceBitmap implements BlurredBackgroundSource{public void draw(Canvas c){}}
class BlurredBackgroundSourceColor implements BlurredBackgroundSource{public void draw(Canvas c){}}
class BlurredBackgroundSourceRenderNode implements BlurredBackgroundSource{public void draw(Canvas c){}}
class Canvas{int dim;}class Rect{boolean isEmpty(){return false;}}class Bound{Rect boundsWithPadding=new Rect();}
class Color{static int alpha(int c){return c>>>24;}}class Build{static class VERSION{static int SDK_INT=36;}static class VERSION_CODES{static int Q=29;}}
'''.replace('HELPERS',helpers))
