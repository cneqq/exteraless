package app.freezgram;

import android.graphics.Rect;
import android.os.Build;
import app.exteraless.appearance.AppearanceConfig;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.LiteMode;
import org.telegram.messenger.SharedConfig;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawable;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawableRenderNode;
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProvider;

/** Composer eligibility and geometry; optics are shared with other glass panels. */
public final class ChatComposerGlass {
    private ChatComposerGlass() {}

    public static boolean isRequested() {
        return AppearanceConfig.chatComposerStyle() != 0;
    }

    public static boolean isEnabled() {
        return isRequested() && Build.VERSION.SDK_INT >= 33
                && SharedConfig.chatBlurEnabled() && !LiteMode.isPowerSaverApplied();
    }

    public static boolean useIosLayout(boolean complexState, int widthDp) {
        return AppearanceConfig.chatComposerStyle() == 1 && !complexState && widthDp >= 240;
    }

    /** Keep recording controls transparent in iOS style even when extra group controls require the whole layout. */
    public static boolean shouldDrawRecordButtonBackground(boolean forbidden, boolean menuState) {
        return !forbidden && !menuState && AppearanceConfig.chatComposerStyle() != 1;
    }

    /** Visible field starts 50dp + 7dp drawable padding from the left edge. */
    public static int textLeftInsetDp() {
        return 57 + 16;
    }
    public static int emojiRightInsetDp() {
        return 16;
    }
    public static int textRightInsetDp(int emojiWidthDp) {
        return emojiWidthDp + emojiRightInsetDp() + 8;
    }

    /** Drawable bounds include the existing 7dp transparent padding on each side. */
    public static void surfaceBounds(Rect whole, Rect field, Rect left, Rect right, boolean split) {
        field.set(whole);
        left.setEmpty();
        right.setEmpty();
        if (!split) return;
        int button = AndroidUtilities.dp(58);
        int inset = AndroidUtilities.dp(50);
        left.set(whole.left, whole.bottom - button, whole.left + button, whole.bottom);
        right.set(whole.right - button, whole.bottom - button, whole.right, whole.bottom);
        field.left += inset;
        field.right -= inset;
    }

    public static BlurredBackgroundProvider colors(Theme.ResourcesProvider resourcesProvider) {
        return LiquidGlassStyle.colors(resourcesProvider, () -> isEnabled());
    }

    public static void refresh(BlurredBackgroundDrawable drawable) {
        if (drawable == null) return;
        LiquidGlassStyle.configure(drawable);
        if (Build.VERSION.SDK_INT >= 33 && drawable instanceof BlurredBackgroundDrawableRenderNode) {
            ((BlurredBackgroundDrawableRenderNode) drawable).setLiquidGlassEffectAllowed(isEnabled());
        }
    }
}
