"""Render actual callback backgrounds through recording Canvas stubs."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java

@unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
class CallbackGlassTests(unittest.TestCase):
    def test_callback_colors_survive_glass_and_url_buttons_keep_legacy_background(self):
        path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/org/telegram/ui/Cells/BotButton.java'
        draw=method(path.read_text(),'    private void drawButtonBackground(')
        run_java('''
class PrivacyCheck {
 Path path=new Path();float[] radii=new float[8];Paint paint=new Paint();
 Button button=new Button(),buttonImpl=button;Object glassBackground;
 void releaseGlass(){glassBackground=null;}
 interface GlassBackgroundRenderer {Object draw(Canvas c,RectF r,float[] radii,Object cached);}
 DRAW
 public static void main(String[] args){
  for(BotInlineKeyboard.BackgroundColor color:BotInlineKeyboard.BackgroundColor.values())
  for(boolean enabled:new boolean[]{false,true})for(boolean callback:new boolean[]{false,true}){
   var p=new PrivacyCheck();p.button.color=color;p.button.callback=callback;Canvas c=new Canvas();
   p.drawButtonBackground(c,new RectF(),null,enabled?(canvas,bounds,radii,cached)->{canvas.glass++;return new Object();}:null);
   boolean glass=enabled&&callback;
   if(c.glass!=(glass?1:0)||c.colors.size()!=(glass?0:1)+(color==BotInlineKeyboard.BackgroundColor.NONE?0:1))throw new AssertionError("Wrong base surface");
   if(color!=BotInlineKeyboard.BackgroundColor.NONE){
    int expected=color==BotInlineKeyboard.BackgroundColor.DANGER?0xffee2222:color==BotInlineKeyboard.BackgroundColor.SUCCESS?0xff22dd66:0xff2288ee;
    int actual=c.colors.get(c.colors.size()-1);
    if((actual&0xffffff)!=(expected&0xffffff)||actual>>>24!=(int)(255*(glass?.52f:.7f)))throw new AssertionError("Semantic color lost");
   }
  }
 }
}
class BotInlineKeyboard{enum BackgroundColor{NONE,DANGER,SUCCESS,PRIMARY}}
class Button{boolean callback;BotInlineKeyboard.BackgroundColor color;BotInlineKeyboard.BackgroundColor getColor(){return color;}}
class TLKeyboardHelper{static boolean isType(Button b,Class<?> type){return b.callback;}}
class TL_keyboard{static class TL_inlineButtonTypeCallback{}}
class RectF{}class Path{enum Direction{CW}void rewind(){}void addRoundRect(RectF r,float[] radii,Direction d){}}
class Paint{int color;void setColor(int c){color=c;}}
class Canvas{int glass;java.util.ArrayList<Integer> colors=new java.util.ArrayList<>();void drawPath(Path p,Paint color){colors.add(color.color);}}
class Theme{
 static int key_paint_chatActionBackground,key_botKeyboard_button_danger=1,key_botKeyboard_button_success=2,key_botKeyboard_button_primary=3;
 static Paint chat_actionBackgroundGradientDarkenPaint=new Paint();
 static class ResourcesProvider{boolean hasGradientService(){return false;}boolean isDark(){return true;}}
 static boolean hasGradientService(){return false;}
 static Paint getThemePaint(int key,ResourcesProvider r){return new Paint();}
 static int getColor(int key,ResourcesProvider r){return key==1?0xffee2222:key==2?0xff22dd66:0xff2288ee;}
 static int multAlpha(int color,float a){return (color&0xffffff)|((int)(255*a)<<24);}
}
'''.replace('DRAW',draw))
