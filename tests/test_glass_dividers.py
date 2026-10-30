"""The same production divider geometry is used by menus, top panels and preview."""
from pathlib import Path
import shutil,unittest
from test_personal_privacy import method,run_java

@unittest.skipUnless(shutil.which('java'),'Java source launcher required')
class DividerTests(unittest.TestCase):
 def test_lines_respect_disable_opacity_and_narrow_panel_bounds(self):
  path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/app/freezgram/GlassDividers.java'
  draw=method(path.read_text(),'    public static void draw(')
  run_java('''
class PrivacyCheck{
 static Paint paint=new Paint();DRAW
 public static void main(String[] args){
  for(boolean on:new boolean[]{false,true})for(int width:new int[]{20,100,400})for(int inset:new int[]{0,16,32})for(int opacity:new int[]{0,18,100}){
   AppearanceConfig.enabled=on;AppearanceConfig.inset=inset;AppearanceConfig.opacity=opacity;Canvas c=new Canvas();draw(c,0,width,7,.5f,0xff112233);
   if(c.calls!=(on?1:0))throw new AssertionError("Divider opt-out ignored");
   if(on&&(c.left<0||c.right>width||c.left>c.right||c.bottom<=c.top||c.color>>>24!=(int)(255*opacity/100f*.5f)))throw new AssertionError("Invalid line bounds/opacity");
  }
 }
}
class Canvas{int calls,color;float left,right,top,bottom;void drawRect(float l,float t,float r,float b,Paint p){calls++;left=l;right=r;top=t;bottom=b;color=p.color;}}
class Paint{int color;void setColor(int c){color=c;}}
class AppearanceConfig{static boolean enabled;static int inset,opacity;static boolean glassMenuDividers(){return enabled;}static int glassDividerInset(){return inset;}static int glassDividerOpacity(){return opacity;}static int glassDividerWeight(){return 1;}}
class AndroidUtilities{static int dp(int n){return n*2;}static float dpf2(float n){return n*2;}}
class Theme{static int multAlpha(int c,float a){return(c&0xffffff)|((int)((c>>>24)*a)<<24);}}
'''.replace('DRAW',draw))
