package app.freezgram;

import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Shader;
import android.os.Build;
import androidx.core.graphics.ColorUtils;
import app.exteraless.appearance.AppearanceConfig;
import org.telegram.messenger.LiteMode;
import org.telegram.messenger.SharedConfig;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawable;
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProvider;
import org.telegram.ui.Components.blur3.drawable.color.BlurredBackgroundProviderBuilder;

/** Independent opt-ins for incoming bubbles, outgoing bubbles and comment strips. */
public final class MessageSurfaceStyle {
    private MessageSurfaceStyle() {}
    public static int style(int profile) {
        return profile == 2 ? AppearanceConfig.commentsSurfaceStyle() : profile == 1 ? AppearanceConfig.outgoingSurfaceStyle() : AppearanceConfig.incomingSurfaceStyle();
    }
    public static int opacity(int profile) {
        return profile == 2 ? AppearanceConfig.commentsSurfaceOpacity() : profile == 1 ? AppearanceConfig.outgoingSurfaceOpacity() : AppearanceConfig.incomingSurfaceOpacity();
    }
    public static int blur(int profile) {
        return profile == 2 ? AppearanceConfig.commentsSurfaceBlur() : profile == 1 ? AppearanceConfig.outgoingSurfaceBlur() : AppearanceConfig.incomingSurfaceBlur();
    }
    public static int intensity(int profile) {
        return profile == 2 ? AppearanceConfig.commentsSurfaceIntensity() : profile == 1 ? AppearanceConfig.outgoingSurfaceIntensity() : AppearanceConfig.incomingSurfaceIntensity();
    }
    public static boolean glassEnabled(int profile) {
        return style(profile) == 1 && Build.VERSION.SDK_INT >= 33 && SharedConfig.chatBlurEnabled() && !LiteMode.isGlassPowerSaverApplied();
    }
    public static int baseColor(Theme.ResourcesProvider provider, int profile) {
        return Theme.getColor(profile == 1 ? Theme.key_chat_outBubble : Theme.key_chat_inBubble, provider) | 0xff000000;
    }
    public static BlurredBackgroundProvider colors(Theme.ResourcesProvider provider, int profile) {
        return new BlurredBackgroundProviderBuilder(provider)
                .setBackgroundColor((r, dark) -> Theme.multAlpha(baseColor(r, profile), opacity(profile) / 100f))
                .setStrokeColorTop(0x66ffffff, 0x66ffffff).setStrokeColorBottom(0x22000000, 0x33000000)
                .setStrokeWidth(0, 0).build();
    }
    public static final class Surface {
        public BlurredBackgroundDrawable glass;
        public int glassProfile = -1;
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final RectF last = new RectF();
        private int lastColor;
        private LinearGradient gradient;
        public void gradient(Canvas canvas, RectF bounds, int profile, Theme.ResourcesProvider provider, float alpha) {
            int color = baseColor(provider, profile);
            if (gradient == null || !last.equals(bounds) || lastColor != color) {
                last.set(bounds); lastColor = color;
                gradient = new LinearGradient(bounds.left, bounds.top, bounds.right, bounds.bottom,
                        ColorUtils.blendARGB(color, 0xffffffff, .10f), ColorUtils.blendARGB(color, 0xff000000, .10f), Shader.TileMode.CLAMP);
                paint.setShader(gradient);
            }
            paint.setAlpha((int) (255 * alpha * opacity(profile) / 100f));
            canvas.drawRect(bounds, paint);
        }
    }
}
