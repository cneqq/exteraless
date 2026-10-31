"""Wallpaper-only frames must refresh glass even when list captures are unchanged."""
import shutil,unittest
from pathlib import Path
from test_personal_privacy import method,run_java
@unittest.skipUnless(shutil.which('java'),'Java source launcher required')
class WallpaperAnimationTests(unittest.TestCase):
 def test_wallpaper_frames_refresh_sources_without_scroll_changes(self):
  p=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/org/telegram/ui/ChatActivity.java'
  impl=method(p.read_text(),'    private void invalidateMergedVisibleBlurredPositionsAndSourcesImpl(').replace('app.freezgram.LiquidGlassStyle','LiquidGlassStyle')
  run_java('''
class PrivacyCheck{
 static int BLUR_INVALIDATE_FLAG_CLIP=4,BLUR_INVALIDATE_FLAG_POSITIONS=2,BLUR_INVALIDATE_FLAG_WALLPAPER=8;
 Suppressor scrollableViewNoiseSuppressor=new Suppressor();java.util.List<Object> glassDrawablesPositionsMerged=new java.util.ArrayList<>();int glassDrawablesPositionsCount,views;
 Content contentView=new Content();Source glassBackgroundSourceRenderNode=new Source(),glassBackgroundSourceFrostedRenderNode=new Source(),iosHeaderGlassSource=new Source();Bar actionBar=new Bar();Runnable glassSourceInvalidationCallback;
 void invalidateClipRectForBackgroundAndChatList(){}int getMergedVisibleBlurredPositions(java.util.List<Object> p){return 0;}void invalidateAllGlassAttachedViews(){views++;}
 IMPL
 public static void main(String[] args){
  var p=new PrivacyCheck();p.invalidateMergedVisibleBlurredPositionsAndSourcesImpl(0);
  if(p.views!=0)throw new AssertionError("Idle sources unnecessarily refreshed");
  p.invalidateMergedVisibleBlurredPositionsAndSourcesImpl(8);
  if(p.views!=1||p.iosHeaderGlassSource.frames!=1||p.glassBackgroundSourceRenderNode.frames!=1||p.glassBackgroundSourceFrostedRenderNode.frames!=1||p.actionBar.frames!=1)throw new AssertionError("Snow-only frame left frozen glass");
  p.scrollableViewNoiseSuppressor=null;p.invalidateMergedVisibleBlurredPositionsAndSourcesImpl(8);
  if(p.views!=1)throw new AssertionError("Unsupported source fallback ignored");
 }
}
class Source{int frames;void invalidateDisplayListForDrawables(){frames++;}}class Bar{int frames;void invalidate(){frames++;}}
class Content{void drawList(Object c){}int getWidth(){return 400;}int getHeight(){return 800;}}
class Suppressor{boolean setNavigationGlassBlur(float r,boolean e){return false;}boolean invalidateResultRenderNodes(java.util.function.Consumer<Object> d,int w,int h){return false;}void setupRenderNodes(java.util.List<Object> p,int c){}}
class Build{static class VERSION{static int SDK_INT=36;}static class VERSION_CODES{static int S=31;}}
class BitwiseUtils{static boolean hasFlag(int f,int b){return (f&b)!=0;}}
class AndroidUtilities{static float dpf2(int n){return n;}}class LiquidGlassStyle{static int blurRadiusDp(){return 24;}static boolean enhanceColors(){return false;}}
'''.replace('IMPL',impl))
