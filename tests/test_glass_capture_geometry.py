"""Production capture geometry: aligned overlaps, negative coordinates and rectangular bitmaps."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java
JAVA=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java'

@unittest.skipUnless(shutil.which('java'),'Java source launcher required')
class CaptureGeometryTests(unittest.TestCase):
    def test_alignment_merges_overlap_and_is_idempotent_in_both_capture_apis(self):
        source=(JAVA/'org/telegram/ui/Components/blur3/DownscaleScrollableNoiseSuppressor.java').read_text()
        methods='\n'.join(method(source,s) for s in (
            '    private static int roundDown(', '    public static int roundUp(',
            '    private void alignCapturePosition(', '    private void finishCaptureSetup(',
            '    public void setupRenderNodes(GlassPositionsArray positions)',
            '    public void setupRenderNodes(List<RectF> positions, int count)'))
        merge=(JAVA/'org/telegram/messenger/utils/RectFMergeBounding.java').read_text()
        merge=merge[merge.index('@Deprecated'):].replace('public class RectFMergeBounding','class RectFMergeBounding')
        run_java('''import java.util.*;
class PrivacyCheck{
 int rectRenderNodesCount;
 ArrayList<RectF> alignedCapturePositions=new ArrayList<>(),mergedCapturePositions=new ArrayList<>();
 ArrayList<SourcePart> rectRenderNodes=new ArrayList<>();
 METHODS
 static class SourcePart{RectF position=new RectF();void setPosition(RectF p){position.set(roundDown(p.left,16),roundDown(p.top,16),roundUp(p.right,16),roundUp(p.bottom,16));}}
 public static void main(String[] args){
  for(float v:new float[]{-48,-32,-31.5f,-16,-.5f,0,.5f,16,17,32}){
   int lo=roundDown(v,16),hi=roundUp(v,16);
   if(lo>v||hi<v||lo%16!=0||hi%16!=0||hi-lo>=32)throw new AssertionError("Capture does not contain negative/fractional coordinates");
   if(roundDown(lo,16)!=lo||roundUp(hi,16)!=hi)throw new AssertionError("Alignment must be idempotent");
  }
  var p=new PrivacyCheck();var list=List.of(new RectF(0,0,15,15),new RectF(17,0,25,15));
  p.setupRenderNodes(list,2);
  if(p.rectRenderNodesCount!=1)throw new AssertionError("Aligned translucent capture regions overlap and blend twice");
  RectF r=p.rectRenderNodes.get(0).position;
  if(r.left!=0||r.top!=0||r.right!=32||r.bottom!=16)throw new AssertionError("Merged capture lost pixels");
  var api=new GlassPositionsArray();api.positions.addAll(list);p.setupRenderNodes(api);
  if(p.rectRenderNodesCount!=1)throw new AssertionError("Second capture API still overlaps");
  p.setupRenderNodes(List.of(new RectF(-17,-17,-1,-1),new RectF(100,100,110,110)),2);
  if(p.rectRenderNodesCount!=2||p.rectRenderNodes.get(0).position.left!=-32)throw new AssertionError("Separate regions or negative edge lost");
  p.setupRenderNodes(list,0);if(p.rectRenderNodesCount!=0)throw new AssertionError("Empty capture retains stale regions");
 }
}
class GlassPositionsArray{ArrayList<RectF> positions=new ArrayList<>();int size(){return positions.size();}RectF get(int i){return positions.get(i);}}
class RectF{float left,top,right,bottom;RectF(){}RectF(float l,float t,float r,float b){set(l,t,r,b);}void set(RectF r){set(r.left,r.top,r.right,r.bottom);}void set(float l,float t,float r,float b){left=l;top=t;right=r;bottom=b;}}
MERGE
'''.replace('METHODS',methods).replace('org.telegram.messenger.utils.RectFMergeBounding','RectFMergeBounding').replace('MERGE',merge))

    def test_rectangular_bitmap_preserves_aspect_and_checks_both_cache_dimensions(self):
        source=(JAVA/'org/telegram/ui/Components/blur3/source/BlurredBackgroundSourceBitmap.java').read_text()
        recording=method(source,'    public Canvas beginRecording(int width, int height, float scale)')
        run_java('''
class PrivacyCheck{
 Bitmap bitmapInternal;
 RECORDING
 public static void main(String[] args){
  var p=new PrivacyCheck();
  for(int[] size:new int[][]{{160,60},{60,160},{120,160},{120,160}})for(int scale:new int[]{1,2}){
   var c=p.beginRecording(size[0],size[1],scale);
   if(c.bitmap.w!=size[0]/scale||c.bitmap.h!=size[1]/scale)throw new AssertionError("Rectangular capture was made square");
   var previous=c.bitmap;var again=p.beginRecording(size[0],size[1],scale);
   if(again.bitmap!=previous)throw new AssertionError("Matching rectangular buffer not reused");
   if(c.x!=scale||c.y!=scale)throw new AssertionError("Capture distorted by unequal scaling");
  }
 }
}
class Bitmap{int w,h;static class Config{static Object ARGB_8888=new Object();}static Bitmap createBitmap(int w,int h,Object config){var b=new Bitmap();b.w=w;b.h=h;return b;}int getWidth(){return w;}int getHeight(){return h;}boolean isRecycled(){return false;}void eraseColor(int c){}}
class Canvas{Bitmap bitmap;float x,y;Canvas(Bitmap b){bitmap=b;}void scale(float a,float b){x=a;y=b;}}
'''.replace('RECORDING',recording))
