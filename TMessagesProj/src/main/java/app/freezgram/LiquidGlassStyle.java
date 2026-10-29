package app.freezgram;

import java.util.function.BooleanSupplier;
import app.exteraless.appearance.AppearanceConfig;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawable;
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProvider;
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProviderBuilder;

/** Shared optical parameters, retaining the existing preference keys. */
public final class LiquidGlassStyle {
    private LiquidGlassStyle() {}
    public static float overlayAlpha(boolean dark) {
        int transparency = AppearanceConfig.navigationGlassTransparency();
        return transparency < 0 ? (dark ? .10f : .07f) : (100 - transparency) / 100f;
    }
    public static int blurRadiusDp() { return AppearanceConfig.navigationGlassBlur(); }
    public static boolean enhanceColors() { return AppearanceConfig.glassEnhanceColors(); }
    public static int revision() {
        return (((blurRadiusDp() * 101 + AppearanceConfig.navigationGlassIntensity()) * 102
                + AppearanceConfig.navigationGlassTransparency() + 1) * 2 + (enhanceColors() ? 1 : 0)) * 2 + (AppearanceConfig.glassWallpaperDim() ? 1 : 0);
    }
    public static void configure(BlurredBackgroundDrawable drawable) {
        drawable.setThickness(AndroidUtilities.dp(12));
        drawable.setIntensity(AppearanceConfig.navigationGlassIntensity() / 100f);
    }
    public static BlurredBackgroundProvider colors(Theme.ResourcesProvider resourcesProvider, BooleanSupplier enabled) {
        return new BlurredBackgroundProviderBuilder(resourcesProvider)
                .setBackgroundColor((r, dark) -> Theme.multAlpha(Theme.getColor(Theme.key_windowBackgroundWhite, r),
                        enabled.getAsBoolean() ? overlayAlpha(dark) : .82f))
                .setStrokeColorTop(0x66ffffff, 0x4dffffff)
                .setStrokeColorBottom(0x24000000, 0x26ffffff)
                .setStrokeWidth(AndroidUtilities.dpf2(.9f), AndroidUtilities.dpf2(.5f))
                .setShadowColor(0x24000000, 0x33000000)
                .setShadowLayer(AndroidUtilities.dpf2(6), 0, AndroidUtilities.dpf2(2)).build();
    }
}
