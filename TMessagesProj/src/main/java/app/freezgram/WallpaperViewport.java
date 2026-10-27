package app.freezgram;

import android.graphics.Canvas;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;
import org.telegram.ui.Components.MotionBackgroundDrawable;

/** Experimental center-crop in local coordinates, without root-window offsets. */
public final class WallpaperViewport {
    private WallpaperViewport() {}

    public static void draw(Canvas canvas, Drawable drawable, int width, int height) {
        if (width <= 0 || height <= 0) return;
        int drawWidth = width;
        int drawHeight = height;
        int intrinsicWidth = drawable.getIntrinsicWidth();
        int intrinsicHeight = drawable.getIntrinsicHeight();
        if (intrinsicWidth > 0 && intrinsicHeight > 0) {
            double scale = Math.max((double) width / intrinsicWidth, (double) height / intrinsicHeight);
            drawWidth = (int) Math.ceil(intrinsicWidth * scale);
            drawHeight = (int) Math.ceil(intrinsicHeight * scale);
        }
        Rect previousBounds = new Rect(drawable.getBounds());
        int saveCount = canvas.save();
        try {
            canvas.clipRect(0, 0, width, height);
            canvas.translate((width - drawWidth) / 2f, (height - drawHeight) / 2f);
            drawable.setBounds(0, 0, drawWidth, drawHeight);
            if (drawable instanceof MotionBackgroundDrawable) {
                ((MotionBackgroundDrawable) drawable).drawInLocalCoordinates(canvas);
            } else {
                drawable.draw(canvas);
            }
        } finally {
            drawable.setBounds(previousBounds);
            canvas.restoreToCount(saveCount);
        }
    }
}
