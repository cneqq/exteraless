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
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProviderBuilder;

/** Opt-in composer styling, independent of navigation/header style preferences. */
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
        return new BlurredBackgroundProviderBuilder(resourcesProvider)
                .setBackgroundColor((r, dark) -> Theme.multAlpha(
                        Theme.getColor(Theme.key_chat_messagePanelBackground, r),
                        isEnabled() ? (dark ? .18f : .12f) : .92f))
                .setStrokeColorTop(0x66ffffff, 0x4dffffff)
                .setStrokeColorBottom(0x18000000, 0x20ffffff)
                .setStrokeWidth(AndroidUtilities.dpf2(.7f), AndroidUtilities.dpf2(.5f))
                .setShadowColor(0x20000000, 0x30000000)
                .setShadowLayer(AndroidUtilities.dpf2(4), 0, AndroidUtilities.dpf2(1))
                .build();
    }

    public static void refresh(BlurredBackgroundDrawable drawable) {
        if (drawable == null) return;
        drawable.setThickness(AndroidUtilities.dp(12));
        drawable.setIntensity(.55f);
        if (Build.VERSION.SDK_INT >= 33 && drawable instanceof BlurredBackgroundDrawableRenderNode) {
            ((BlurredBackgroundDrawableRenderNode) drawable).setLiquidGlassEffectAllowed(isEnabled());
        }
    }
}
