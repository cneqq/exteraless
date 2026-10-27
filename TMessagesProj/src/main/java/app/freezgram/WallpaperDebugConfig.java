package app.freezgram;

import android.content.Context;
import org.telegram.messenger.ApplicationLoader;

/** Local, opt-in wallpaper experiments. Zero flags preserves upstream behavior. */
public final class WallpaperDebugConfig {
    public static final int BITMAP_SIZE = 1;
    public static final int LIFECYCLE = 2;
    public static final int NO_FAST_RENDER = 4;
    public static final int NO_MOTION = 8;
    public static final int OPAQUE_BASE = 16;
    public static final int LOCAL_VIEWPORT = 32;
    public static final int[] OPTIONS = {BITMAP_SIZE, LIFECYCLE, NO_FAST_RENDER, NO_MOTION, OPAQUE_BASE, LOCAL_VIEWPORT};
    private static volatile int flags = -1;

    private WallpaperDebugConfig() {}

    public static boolean enabled(int option) {
        if (flags == -1) {
            Context context = ApplicationLoader.applicationContext;
            if (context == null) return false;
            flags = context.getSharedPreferences("freezgram_wallpaper_debug", Context.MODE_PRIVATE).getInt("flags", 0);
        }
        return (flags & option) != 0;
    }

    public static void toggle(int option) {
        enabled(option);
        save(flags ^ option);
    }

    public static void reset() { save(0); }

    private static void save(int value) {
        ApplicationLoader.applicationContext.getSharedPreferences("freezgram_wallpaper_debug", Context.MODE_PRIVATE)
                .edit().putInt("flags", value).apply();
        flags = value;
    }
}
