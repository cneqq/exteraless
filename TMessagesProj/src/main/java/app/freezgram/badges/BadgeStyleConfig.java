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
    private static int style = -1;
    private static final WeakHashMap<Drawable, Boolean> drawables = new WeakHashMap<>();

    private BadgeStyleConfig() {}

    public static int getStyle() {
        if (style < 0) {
            Context context = ApplicationLoader.applicationContext;
            if (context == null) return SPARKLES;
            int stored = context.getSharedPreferences("freezgram_badge_style", Context.MODE_PRIVATE).getInt("style", SPARKLES);
            style = stored >= SPARKLES && stored <= SEAL ? stored : SPARKLES;
        }
        return style;
    }

    public static void register(Drawable drawable) { drawables.put(drawable, Boolean.TRUE); }

    public static void setStyle(int value) {
        if (value < SPARKLES || value > SEAL) throw new IllegalArgumentException("Invalid badge style");
        ApplicationLoader.applicationContext.getSharedPreferences("freezgram_badge_style", Context.MODE_PRIVATE)
                .edit().putInt("style", value).apply();
        style = value;
        for (Drawable drawable : new ArrayList<>(drawables.keySet())) {
            if (drawable != null) drawable.invalidateSelf();
        }
    }
}
