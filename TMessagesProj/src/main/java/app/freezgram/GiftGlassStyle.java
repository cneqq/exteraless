package app.freezgram;

import app.exteraless.appearance.AppearanceConfig;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawable;
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProvider;
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProviderBuilder;

/** Gift-only optics, shared by received cards and the sending preview. */
public final class GiftGlassStyle {
    private GiftGlassStyle() {}
    public static int blurRadiusDp() {
        return AppearanceConfig.giftGlassBlur();
    }
    public static int revision() {
        return (blurRadiusDp() * 101 + AppearanceConfig.giftGlassIntensity()) * 101 + AppearanceConfig.giftGlassTransparency();
    }
    public static float opacity() {
        return (100 - AppearanceConfig.giftGlassTransparency()) / 100f;
    }
    public static void configure(BlurredBackgroundDrawable drawable) {
        drawable.setThickness(AndroidUtilities.dp(12));
        drawable.setIntensity(AppearanceConfig.giftGlassIntensity() / 100f);
    }
    public static BlurredBackgroundProvider colors(Theme.ResourcesProvider provider) {
        return new BlurredBackgroundProviderBuilder(provider)
                .setBackgroundColor((r, dark) -> Theme.multAlpha(Theme.getColor(Theme.key_windowBackgroundWhite, r), opacity()))
                .setStrokeColorTop(0x99ffffff, 0x99ffffff)
                .setStrokeColorBottom(0x40000000, 0x55ffffff)
                .setStrokeWidth(AndroidUtilities.dpf2(1.2f), AndroidUtilities.dpf2(.8f))
                .setShadowColor(0x24000000, 0x33000000)
                .setShadowLayer(AndroidUtilities.dpf2(6), 0, AndroidUtilities.dpf2(2)).build();
    }
}
