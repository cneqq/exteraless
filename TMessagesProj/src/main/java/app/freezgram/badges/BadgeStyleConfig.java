package app.freezgram.badges;

import android.content.Context;
import android.graphics.drawable.Drawable;
import org.telegram.messenger.ApplicationLoader;
import java.util.ArrayList;
import java.util.WeakHashMap;

/** Local presentation only; choosing a style does not grant a badge. */
public final class BadgeStyleConfig {
    public static final int SPARKLES = 0;
    public static final int PLAIN = 1;
    public static final int SEAL = 2;
    public static final int SEAL_BLUE = 3;
    public static final int SEAL_LAVENDER = 4;
    public static final int SEAL_GRAPHITE = 5;
    public static final int SEAL_MINT = 6;
    public static final int MAX_STYLE = SEAL_MINT;
    private static int style = -1;
    private static final WeakHashMap<Drawable, Boolean> drawables = new WeakHashMap<>();

    private BadgeStyleConfig() {}

    public static int getStyle() {
        if (style < 0) {
            Context context = ApplicationLoader.applicationContext;
            if (context == null) return SPARKLES;
            int stored = context.getSharedPreferences("freezgram_badge_style", Context.MODE_PRIVATE).getInt("style", SPARKLES);
            style = stored >= SPARKLES && stored <= MAX_STYLE ? stored : SPARKLES;
        }
        return style;
    }

    public static void register(Drawable drawable) { drawables.put(drawable, Boolean.TRUE); }

    public static int getSealColor(int style) {
        return switch (style) {
            case SEAL_BLUE -> 0xff6db9e7;
            case SEAL_LAVENDER -> 0xffb6a1de;
            case SEAL_GRAPHITE -> 0xff596675;
            case SEAL_MINT -> 0xff7ed4c6;
            default -> 0xffd3d6da;
        };
    }

    public static void setStyle(int value) {
        if (value < SPARKLES || value > MAX_STYLE) throw new IllegalArgumentException("Invalid badge style");
        ApplicationLoader.applicationContext.getSharedPreferences("freezgram_badge_style", Context.MODE_PRIVATE)
                .edit().putInt("style", value).apply();
        style = value;
        for (Drawable drawable : new ArrayList<>(drawables.keySet())) {
            if (drawable != null) drawable.invalidateSelf();
        }
    }
}
