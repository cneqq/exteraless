package app.freezgram;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.os.Build;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import app.exteraless.appearance.AppearanceConfig;
import app.exteraless.appearance.AvatarCornersSeekBar;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.LocaleController;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Cells.TextCheckCell;
import org.telegram.ui.Components.LayoutHelper;
import org.telegram.ui.Components.blur3.source.BlurredBackgroundSourceRenderNode;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawable;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawableRenderNode;

/** Independent gift settings; received cards and sending previews share this profile. */
public final class GiftGlassSettingsActivity extends BaseFragment {
    private boolean changed;
    @Override public View createView(Context context) {
        actionBar.setBackButtonImage(R.drawable.ic_ab_back);
        actionBar.setTitle(LocaleController.getString(R.string.FreezgramGiftGlassSettings));
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override public void onItemClick(int id) { if (id == -1) finishFragment(); }
        });
        ScrollView scroll = new ScrollView(context);
        scroll.setBackgroundColor(getThemedColor(Theme.key_windowBackgroundWhite));
        LinearLayout content = new LinearLayout(context); content.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(content);
        Preview preview = new Preview(context);
        content.addView(preview, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 250));
        TextView info = new TextView(context);
        info.setText(LocaleController.getString(R.string.FreezgramGiftGlassInfo));
        info.setTextSize(14); info.setTextColor(getThemedColor(Theme.key_windowBackgroundWhiteGrayText));
        info.setPadding(dp(22), dp(12), dp(22), dp(12)); content.addView(info);
        TextCheckCell enabled = new TextCheckCell(context);
        enabled.setTextAndCheck(LocaleController.getString(R.string.FreezgramGiftCardsGlass), AppearanceConfig.giftCardsGlass(), false);
        enabled.setOnClickListener(v -> {
            AppearanceConfig.giftCardsGlass.setConfigBool(!AppearanceConfig.giftCardsGlass());
            enabled.setChecked(AppearanceConfig.giftCardsGlass()); changed = true; preview.invalidate();
        }); content.addView(enabled);
        slider(context, content, R.string.FreezgramPanelBlur, 30, AppearanceConfig.giftGlassBlur(), value -> {
            AppearanceConfig.giftGlassBlur.setConfigInt(value); changed = true; preview.invalidate();
        });
        slider(context, content, R.string.FreezgramPanelIntensity, 100, AppearanceConfig.giftGlassIntensity(), value -> {
            AppearanceConfig.giftGlassIntensity.setConfigInt(value); changed = true; preview.invalidate();
        });
        slider(context, content, R.string.FreezgramPanelTransparency, 100, AppearanceConfig.giftGlassTransparency(), value -> {
            AppearanceConfig.giftGlassTransparency.setConfigInt(value); changed = true; preview.invalidate();
        });
        fragmentView = scroll;
        return scroll;
    }
    private void slider(Context context, LinearLayout content, int title, int max, int value, AvatarCornersSeekBar.OnDrag drag) {
        AvatarCornersSeekBar slider = new AvatarCornersSeekBar(context, drag, 0, max, LocaleController.getString(title), "0", String.valueOf(max));
        slider.setValue(value); content.addView(slider, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 112));
    }
    @Override public void onFragmentDestroy() {
        android.app.Activity activity = getParentActivity();
        super.onFragmentDestroy();
        if (changed && activity instanceof org.telegram.ui.LaunchActivity) {
            AndroidUtilities.runOnUIThread(() -> ((org.telegram.ui.LaunchActivity) activity).rebuildAllFragments(false));
        }
    }
    private static int dp(float n) { return AndroidUtilities.dp(n); }
    private final class Preview extends View {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private BlurredBackgroundSourceRenderNode wallpaper;
        private BlurredBackgroundDrawable glass;
        Preview(Context context) {
            super(context);
            if (Build.VERSION.SDK_INT >= 33) {
                wallpaper = new BlurredBackgroundSourceRenderNode(null);
                glass = SmallElementsGlass.createGiftSource(wallpaper).createDrawable();
                glass.setColorProvider(GiftGlassStyle.colors(resourceProvider)); glass.setRadius(dp(20));
            }
        }
        private void backdrop(Canvas canvas) {
            canvas.drawColor(getThemedColor(Theme.key_windowBackgroundGray));
            paint.setColor(0xff448ac4); canvas.drawCircle(dp(80), dp(90), dp(60), paint);
            paint.setColor(0xff8058b0); canvas.drawCircle(getWidth() - dp(80), dp(170), dp(60), paint);
        }
        @Override protected void onDraw(Canvas canvas) {
            backdrop(canvas);
            int left = Math.max(dp(16), (getWidth() - dp(220)) / 2), right = getWidth() - left;
            if (glass != null && canvas.isHardwareAccelerated() && SmallElementsGlass.areGiftCardsEnabled()) {
                Canvas capture = wallpaper.beginRecording(getWidth(), getHeight()); backdrop(capture); wallpaper.endRecording();
                ((BlurredBackgroundDrawableRenderNode) glass).setLiquidGlassEffectAllowed(true);
                GiftGlassStyle.configure(glass); glass.updateColors();
                glass.setBounds(left, dp(16), right, getHeight() - dp(16)); glass.draw(canvas);
            } else {
                paint.setColor(getThemedColor(Theme.key_chat_serviceBackground));
                canvas.drawRoundRect(left, dp(16), right, getHeight() - dp(16), dp(20), dp(20), paint);
            }
            paint.setColor(getThemedColor(Theme.key_chat_serviceText)); paint.setTextAlign(Paint.Align.CENTER);
            paint.setTextSize(dp(60)); canvas.drawText("🎁", getWidth() / 2f, dp(115), paint);
            paint.setTextSize(dp(16)); canvas.drawText(LocaleController.getString(R.string.FreezgramGiftGlassSettings), getWidth() / 2f, dp(165), paint);
            paint.setTextSize(dp(14)); canvas.drawText(LocaleController.getString(R.string.Gift2UniqueView), getWidth() / 2f, dp(200), paint);
            paint.setTextAlign(Paint.Align.LEFT);
        }
    }
}
