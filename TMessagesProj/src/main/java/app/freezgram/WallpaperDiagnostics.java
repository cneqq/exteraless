package app.freezgram;

import android.graphics.Bitmap;
import android.graphics.Rect;
import android.util.Log;
import java.util.Arrays;

/** Opt-in geometry/pixel coverage only. Enable with adb setprop log.tag.FreezgramWallpaper DEBUG. */
public final class WallpaperDiagnostics {
    private static final String TAG = "FreezgramWallpaper";

    private WallpaperDiagnostics() {}

    public static boolean enabled() { return Log.isLoggable(TAG, Log.DEBUG); }

    public static boolean record(Bitmap pattern, Bitmap gradient, Rect bounds, int intensity,
                                 boolean preview, boolean hardware) {
        if (!enabled()) return false;
        try {
            Log.i(TAG, "draw bounds=" + bounds + " intensity=" + intensity
                    + " preview=" + preview + " hardware=" + hardware);
            describe("pattern", pattern);
            describe("gradient", gradient);
            return true;
        } catch (Exception e) {
            Log.i(TAG, "bitmap metadata unavailable: " + e.getClass().getSimpleName());
            return true;
        }
    }

    public static void window(int width, int height, int rootHeight, int translationY, int bottomClip,
                              String drawableType) {
        if (enabled()) {
            Log.i(TAG, "window=" + width + "x" + height + " rootHeight=" + rootHeight
                    + " translationY=" + translationY + " bottomClip=" + bottomClip
                    + " drawable=" + drawableType);
        }
    }

    private static void describe(String label, Bitmap bitmap) {
        if (bitmap == null || bitmap.isRecycled()) {
            Log.i(TAG, label + "=none");
            return;
        }
        int width = bitmap.getWidth(), height = bitmap.getHeight();
        int[] row = new int[width];
        int[] alphaCoverage = new int[8];
        int[] brightness = new int[8];
        // Eight sampled rows per band, reported as aggregates; no image content is logged.
        for (int band = 0; band < 8; band++) {
            long visible = 0, light = 0;
            for (int sample = 0; sample < 8; sample++) {
                int y = Math.min(height - 1, (int) ((band * 8L + sample) * height / 64));
                bitmap.getPixels(row, 0, width, 0, y, width, 1);
                for (int pixel : row) {
                    if ((pixel >>> 24) != 0) visible++;
                    light += ((pixel >>> 16) & 255) + ((pixel >>> 8) & 255) + (pixel & 255);
                }
            }
            alphaCoverage[band] = (int) (visible * 100 / (width * 8L));
            brightness[band] = (int) (light / (width * 8L * 3));
        }
        Log.i(TAG, label + "=" + width + "x" + height + " config=" + bitmap.getConfig()
                + " alphaPercentTopToBottom=" + Arrays.toString(alphaCoverage)
                + " rgbMeanTopToBottom=" + Arrays.toString(brightness));
    }
}
