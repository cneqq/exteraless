package app.freezgram.badges;

import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.LayerDrawable;
import android.os.SystemClock;
import android.view.View;

import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.LiteMode;
import org.telegram.messenger.R;
import org.telegram.messenger.SharedConfig;

/** Community seal with the Freezgram plane and lightweight sparkle effects. */
public final class FreezgramBadgeDrawable extends Drawable {
    private final Drawable seal;
    private final Drawable plane;
    private final Drawable backing;
    private int appliedStyle = -1;
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path star = new Path();
    private final Runnable nextFrame = this::invalidateSelf;
    private int alpha = 255;

    public FreezgramBadgeDrawable(Drawable seal, Drawable plane) {
        this.seal = seal;
        this.plane = plane;
        backing = seal instanceof LayerDrawable
                ? ((LayerDrawable) seal).findDrawableByLayerId(R.id.freezgram_badge_background) : null;
        BadgeStyleConfig.register(this);
        paint.setColor(0xff76c5ff);
        star.moveTo(0, -1);
        star.lineTo(.22f, -.22f);
        star.lineTo(1, 0);
        star.lineTo(.22f, .22f);
        star.lineTo(0, 1);
        star.lineTo(-.22f, .22f);
        star.lineTo(-1, 0);
        star.lineTo(-.22f, -.22f);
        star.close();
    }

    private boolean animate() {
        if (BadgeStyleConfig.getStyle() == BadgeStyleConfig.PLAIN || alpha == 0 || !isVisible() || !SharedConfig.animationsEnabled()
                || !LiteMode.isEnabled(LiteMode.FLAG_ANIMATED_EMOJI_CHAT_NOT_PREMIUM)) return false;
        Callback callback = getCallback();
        if (!(callback instanceof View)) return false;
        View view = (View) callback;
        return view.isAttachedToWindow() && view.isShown() && view.getWindowVisibility() == View.VISIBLE;
    }

    @Override
    public void draw(Canvas canvas) {
        Rect bounds = getBounds();
        if (bounds.isEmpty()) return;
        boolean animated = animate();
        float phase = animated ? (SystemClock.uptimeMillis() % 2400) / 2400f : 0;
        int save = canvas.save();
        canvas.translate(bounds.left, bounds.top);
        canvas.scale(bounds.width() / 32f, bounds.height() / 28f);
        int style = BadgeStyleConfig.getStyle();
        if (style >= BadgeStyleConfig.SEAL) {
            if (backing != null && appliedStyle != style) {
                backing.setTint(BadgeStyleConfig.getSealColor(style));
                appliedStyle = style;
            }
            int sealSave = canvas.save();
            canvas.translate(2, 2);
            int sealSize = AndroidUtilities.dp(24);
            canvas.scale(24f / sealSize, 24f / sealSize);
            seal.setBounds(0, 0, sealSize, sealSize);
            seal.setAlpha(alpha);
            seal.draw(canvas);
            canvas.restoreToCount(sealSave);
        } else {
            int size = style == BadgeStyleConfig.PLAIN ? 26 : 22;
            int pixels = AndroidUtilities.dp(size);
            int planeSave = canvas.save();
            float centerX = style == BadgeStyleConfig.PLAIN ? 16 : 14;
            // Optical centering of the asymmetric plane, including its transparent margins.
            canvas.translate(centerX - size / 2f - size * .057f, 14 - size / 2f - size * .017f);
            canvas.scale((float) size / pixels, (float) size / pixels);
            plane.setBounds(0, 0, pixels, pixels);
            plane.setAlpha(alpha);
            plane.draw(canvas);
            canvas.restoreToCount(planeSave);
        }
        if (style != BadgeStyleConfig.PLAIN) {
            sparkle(canvas, 28.2f, 7, 1.9f, phase, animated);
            sparkle(canvas, 29, 18.5f, 2.6f, phase + .36f, animated);
            sparkle(canvas, 2, 5, 1.15f, phase + .68f, animated);
        }
        canvas.restoreToCount(save);

        // A frame requests a redraw only; it does not schedule another frame itself.
        // When the host stops drawing, the animation stops as well.
        unscheduleSelf(nextFrame);
        if (animated) scheduleSelf(nextFrame, SystemClock.uptimeMillis() + 50);
    }

    private void sparkle(Canvas canvas, float x, float y, float radius, float phase, boolean animated) {
        float pulse = animated ? .5f + .5f * (float) Math.sin(phase * Math.PI * 2) : .75f;
        paint.setAlpha((int) (alpha * (.35f + .65f * pulse)));
        float scale = radius * (.72f + .28f * pulse);
        int save = canvas.save();
        canvas.translate(x, y);
        canvas.scale(scale, scale);
        canvas.drawPath(star, paint);
        canvas.restoreToCount(save);
    }

    @Override public int getIntrinsicWidth() { return AndroidUtilities.dp(32); }
    @Override public int getIntrinsicHeight() { return AndroidUtilities.dp(28); }
    @Override public void setAlpha(int alpha) { this.alpha = alpha; invalidateSelf(); }
    @Override public void setColorFilter(ColorFilter filter) {
        seal.setColorFilter(filter);
        plane.setColorFilter(filter);
        paint.setColorFilter(filter);
        invalidateSelf();
    }
    @Override public int getOpacity() { return PixelFormat.TRANSLUCENT; }
}
