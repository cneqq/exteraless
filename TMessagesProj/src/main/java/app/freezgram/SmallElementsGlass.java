package app.freezgram;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Rect;
import android.os.Build;
import android.view.View;
import app.exteraless.appearance.AppearanceConfig;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.LiteMode;
import org.telegram.messenger.SharedConfig;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawable;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawableRenderNode;
import org.telegram.ui.Components.blur3.source.BlurredBackgroundSource;
import org.telegram.ui.Components.blur3.source.BlurredBackgroundSourceBitmap;
import org.telegram.ui.Components.blur3.source.BlurredBackgroundSourceRenderNode;
import org.telegram.ui.Components.blur3.utils.Blur3Utils;

/** Shared opt-in for small app surfaces; system notifications are not affected. */
public final class SmallElementsGlass {
    private SmallElementsGlass() {}
    public static boolean isEnabled() {
        return AppearanceConfig.smallElementsGlass() && Build.VERSION.SDK_INT >= 33
                && SharedConfig.chatBlurEnabled() && !LiteMode.isPowerSaverApplied();
    }

    /** Bridge existing bitmap captures into the same AGSL renderer used by the panels. */
    public static BlurredBackgroundSource createSource(BlurredBackgroundSource source) {
        return new SnapshotSource(source);
    }

    private static final class SnapshotSource extends BlurredBackgroundSourceRenderNode {
        private final BlurredBackgroundSource input;
        private Bitmap lastBitmap;
        private int lastRevision = Integer.MIN_VALUE;
        SnapshotSource(BlurredBackgroundSource source) { super(source); input = source; }
        @Override public void draw(Canvas canvas, float left, float top, float right, float bottom) {
            int width = Math.max(1, (int) Math.ceil(right) + AndroidUtilities.dp(64));
            int height = Math.max(1, (int) Math.ceil(bottom) + AndroidUtilities.dp(64));
            Bitmap bitmap = input instanceof BlurredBackgroundSourceBitmap ? ((BlurredBackgroundSourceBitmap) input).getBitmap() : null;
            int revision = LiquidGlassStyle.revision();
            if (bitmap == null || bitmap != lastBitmap || revision != lastRevision || needUpdateDisplayList(width, height)) {
                lastBitmap = bitmap; lastRevision = revision;
                Canvas capture = beginRecording(width, height);
                input.draw(capture, 0, 0, width, height);
                endRecording();
                setBlur(AndroidUtilities.dpf2(LiquidGlassStyle.blurRadiusDp()), LiquidGlassStyle.enhanceColors()
                        ? org.telegram.messenger.utils.RenderNodeEffects.getSaturationX3RenderEffect() : null);
            }
            super.draw(canvas, left, top, right, bottom);
        }
    }

    /** One in-memory snapshot per displayed notice. Released when its view detaches. */
    public static final class NotificationBackdrop {
        private final BlurredBackgroundSourceBitmap bitmapSource = new BlurredBackgroundSourceBitmap();
        private BlurredBackgroundDrawable glass;
        private Bitmap bitmap;
        private View capturedRoot;
        private int rootWidth, rootHeight;
        private final int[] ownerLocation = new int[2], rootLocation = new int[2];

        public boolean draw(Canvas canvas, View owner, Rect bounds, Theme.ResourcesProvider provider, int radiusDp) {
            if (!isEnabled() || !canvas.isHardwareAccelerated() || AndroidUtilities.makingGlobalBlurBitmap) return false;
            View root = owner.getRootView();
            if (root.getWidth() <= 0 || root.getHeight() <= 0) return false;
            if (bitmap == null || root != capturedRoot || rootWidth != root.getWidth() || rootHeight != root.getHeight()) {
                release(); capturedRoot = root; rootWidth = root.getWidth(); rootHeight = root.getHeight();
                // Bulletin/Undo draw guards exclude notices from this capture, including this owner.
                AndroidUtilities.makeGlobalBlurBitmap(value -> { bitmap = value; bitmapSource.setBitmap(value); }, 4f, 0, root, null);
                if (bitmap == null) return false;
                Blur3Utils.checkBitmapSourceMatrixScale(bitmapSource, root);
                glass = createSource(bitmapSource).createDrawable();
                glass.setColorProvider(LiquidGlassStyle.colors(provider, SmallElementsGlass::isEnabled));
            }
            owner.getLocationOnScreen(ownerLocation); root.getLocationOnScreen(rootLocation);
            glass.setSourceOffset(ownerLocation[0] - rootLocation[0], ownerLocation[1] - rootLocation[1]);
            glass.setBounds(bounds); glass.setRadius(AndroidUtilities.dp(radiusDp));
            LiquidGlassStyle.configure(glass);
            ((BlurredBackgroundDrawableRenderNode) glass).setLiquidGlassEffectAllowed(true);
            glass.updateColors(); glass.draw(canvas);
            return true;
        }

        public void release() {
            glass = null; bitmapSource.setBitmap(null);
            // RenderNodes can still reference the old image until the frame completes; let GC release it.
            bitmap = null; capturedRoot = null;
        }
    }
}
