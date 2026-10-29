"""Exercise plain badge sizing and alpha forwarding with synthetic drawables."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import run_java


class PlainBadgeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_plane_size_is_density_aware_and_alpha_is_preserved(self):
        path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/app/freezgram/badges/FreezgramBadgeDrawable.java'
        source=path.read_text()
        source=source[source.index('public final class'):].replace('public final class','final class',1)
        run_java('''
class PrivacyCheck{
 public static void main(String[] args){
  for(int density:new int[]{1,2,3,4}){
   AndroidUtilities.density=density;Drawable plane=new Drawable();
   FreezgramBadgeDrawable badge=new FreezgramBadgeDrawable(plane);Canvas canvas=new Canvas();
   badge.draw(canvas);if(plane.draws!=0)throw new AssertionError("Empty bounds drawn");
   badge.setBounds(0,0,badge.getIntrinsicWidth(),badge.getIntrinsicHeight());
   if(badge.getIntrinsicWidth()!=32*density||badge.getIntrinsicHeight()!=28*density)throw new AssertionError();
   for(int alpha:new int[]{0,128,255}){
    badge.setAlpha(alpha);badge.draw(canvas);
    if(plane.alpha!=alpha||plane.bounds.width()!=26*density||plane.bounds.height()!=26*density||canvas.depth!=0)
     throw new AssertionError("Plane rendering invariant");
   }
  }
 }
}
class Rect{
 int left,top,right,bottom;int width(){return right-left;}int height(){return bottom-top;}
 boolean isEmpty(){return width()<=0||height()<=0;}
}
class Drawable{
 Rect bounds=new Rect();int alpha=255,draws;Rect getBounds(){return bounds;}
 void setBounds(int l,int t,int r,int b){bounds.left=l;bounds.top=t;bounds.right=r;bounds.bottom=b;}
 public void draw(Canvas c){draws++;}void invalidateSelf(){}
 public void setAlpha(int a){alpha=a;}public void setColorFilter(ColorFilter f){}
 public int getIntrinsicWidth(){return 0;}public int getIntrinsicHeight(){return 0;}public int getOpacity(){return 0;}
}
class Canvas{int depth;int save(){return depth++;}void restoreToCount(int count){depth=count;}void translate(float x,float y){}void scale(float x,float y){}}
class ColorFilter{}class PixelFormat{static int TRANSLUCENT=-3;}
class AndroidUtilities{static int density=1;static int dp(int value){return value*density;}}
''' + source)


if __name__=='__main__':unittest.main()
