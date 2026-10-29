package app.freezgram;

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

/** Glass for the centered chat header, independent of bottom-panel preferences. */
public final class IosLiquidGlassChatHeader {
    private IosLiquidGlassChatHeader() {}

    public static boolean isRequested() {
        return AppearanceConfig.iosChatHeader();
    }

    public static boolean isEnabled() {
        return isRequested() && Build.VERSION.SDK_INT >= 33
                && SharedConfig.chatBlurEnabled() && !LiteMode.isPowerSaverApplied();
    }

    public static BlurredBackgroundProvider colors(Theme.ResourcesProvider resourcesProvider) {
        return new BlurredBackgroundProviderBuilder(resourcesProvider)
                .setBackgroundColor((r, dark) -> Theme.multAlpha(
                        Theme.getColor(Theme.key_chat_topPanelBackground, r),
                        isEnabled() ? (dark ? .18f : .12f) : .88f))
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
