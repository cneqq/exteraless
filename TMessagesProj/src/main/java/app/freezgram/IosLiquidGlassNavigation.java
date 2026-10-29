package app.freezgram;

import android.os.Build;
import app.exteraless.appearance.AppearanceConfig;
import app.exteraless.appearance.MainTabsUiHelper;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.LiteMode;
import org.telegram.messenger.SharedConfig;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawable;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawableRenderNode;
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProvider;
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProviderBuilder;

/** Opt-in iOS navigation glass using the client's existing backdrop and AGSL engine. */
public final class IosLiquidGlassNavigation {
    private IosLiquidGlassNavigation() {}

    public static boolean isRequested() {
        return MainTabsUiHelper.isIosNavigationBar() && AppearanceConfig.iosLiquidGlassNavigation();
    }

    public static boolean isEnabled() {
        return isRequested() && Build.VERSION.SDK_INT >= 33
                && SharedConfig.chatBlurEnabled() && !LiteMode.isPowerSaverApplied();
    }

    public static BlurredBackgroundProvider colors(Theme.ResourcesProvider resourcesProvider) {
        return new BlurredBackgroundProviderBuilder(resourcesProvider)
                .setBackgroundColor((r, dark) -> Theme.multAlpha(
                        Theme.getColor(Theme.key_windowBackgroundWhite, r),
                        isEnabled() ? overlayAlpha(dark) : .82f))
                .setStrokeColorTop(0x66ffffff, 0x4dffffff)
                .setStrokeColorBottom(0x24000000, 0x26ffffff)
                .setStrokeWidth(AndroidUtilities.dpf2(.9f), AndroidUtilities.dpf2(.5f))
                .setShadowColor(0x24000000, 0x33000000)
                .setShadowLayer(AndroidUtilities.dpf2(6), 0, AndroidUtilities.dpf2(2))
                .build();
    }

    public static float overlayAlpha(boolean dark) {
        int transparency = AppearanceConfig.navigationGlassTransparency();
        return transparency < 0 ? (dark ? .10f : .07f) : (100 - transparency) / 100f;
    }

    public static int blurRadiusDp() { return AppearanceConfig.navigationGlassBlur(); }

    public static void configure(BlurredBackgroundDrawable drawable) {
        drawable.setThickness(AndroidUtilities.dp(12));
        drawable.setIntensity(AppearanceConfig.navigationGlassIntensity() / 100f);
    }

    public static void refresh(BlurredBackgroundDrawable drawable) {
        if (isRequested()) configure(drawable);
        if (Build.VERSION.SDK_INT >= 33 && isRequested()
                && drawable instanceof BlurredBackgroundDrawableRenderNode) {
            ((BlurredBackgroundDrawableRenderNode) drawable).setLiquidGlassEffectAllowed(isEnabled());
        }
    }
}
