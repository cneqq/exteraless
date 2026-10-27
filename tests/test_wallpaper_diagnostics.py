"""Check that opt-in wallpaper metadata detects empty bitmap bands."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import run_java


class WallpaperDiagnosticsTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_reports_empty_lower_half_and_does_nothing_when_disabled(self):
        path = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java/app/freezgram/WallpaperDiagnostics.java'
        source = path.read_text()
        source = source[source.index('public final class'):].replace('public final class', 'final class', 1)
        run_java('''import java.util.*;
class PrivacyCheck {
  public static void main(String[] args) {
    Bitmap pattern = new Bitmap();
    if (WallpaperDiagnostics.record(pattern,null,new Rect(),-57,false,true)) throw new AssertionError();
    if (pattern.reads != 0 || !Log.lines.isEmpty()) throw new AssertionError("Disabled diagnostics read pixels");
    Log.enabled=true;
    WallpaperDiagnostics.record(pattern,null,new Rect(),-57,false,true);
    String result=String.join("\\n",Log.lines);
    if (!result.contains("alphaPercentTopToBottom=[100, 100, 100, 100, 0, 0, 0, 0]"))
      throw new AssertionError("Did not detect empty lower half: "+result);
    if (!result.contains("gradient=none")) throw new AssertionError("Null bitmap failed");
  }
}
class Log {
  static int DEBUG=3; static boolean enabled; static List<String> lines=new ArrayList<>();
  static boolean isLoggable(String tag,int level){return enabled;}
  static void i(String tag,String message){lines.add(message);}
}
class Rect { public String toString(){return "0,0,8,64";} }
class Bitmap {
  int reads;
  boolean isRecycled(){return false;}
  int getWidth(){return 8;} int getHeight(){return 64;}
  String getConfig(){return "ALPHA_8";}
  void getPixels(int[] row,int offset,int stride,int x,int y,int width,int height){
    reads++; Arrays.fill(row,y<32?0xff000000:0);
  }
}
''' + source)


if __name__ == '__main__':
    unittest.main()
