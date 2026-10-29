package app.freezgram;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.os.Build;
import android.view.View;
import android.widget.FrameLayout;
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
import org.telegram.ui.Components.LayoutHelper;
import org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawable;
import org.telegram.ui.Components.blur3.source.BlurredBackgroundSourceRenderNode;
import org.telegram.ui.Components.glass.GlassTabView;

/** Local visual settings with sample background content and the actual navigation tabs. */
public final class NavigationGlassSettingsActivity extends BaseFragment {
    public static final int NAVIGATION = 0, SHARED = 1, COMPOSER = 2;
    private final int mode;
    public NavigationGlassSettingsActivity() { this(NAVIGATION); }
    public NavigationGlassSettingsActivity(int mode) { this.mode = mode; }
    private GlassPreview preview;
    private AvatarCornersSeekBar blur, intensity, transparency, width, lift, textInset, emojiInset;
    private boolean geometryChanged;
    private org.telegram.ui.Cells.TextCheckCell contacts;

    private String text(int id) { return LocaleController.getString(id); }

    @Override
    public View createView(Context context) {
        actionBar.setBackButtonImage(R.drawable.ic_ab_back);
        actionBar.setTitle(text(mode == 1 ? R.string.FreezgramSharedGlassSettings : mode == 2 ? R.string.FreezgramComposerSettings : R.string.FreezgramPanelSettings));
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override public void onItemClick(int id) { if (id == -1) finishFragment(); }
        });
        ScrollView scroll = new ScrollView(context);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(getThemedColor(Theme.key_windowBackgroundWhite));
        LinearLayout content = new LinearLayout(context);
        content.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(content);
        preview = new GlassPreview(context);
        content.addView(preview, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, mode == 1 ? 360 : 240));
        TextView info = new TextView(context);
        info.setText(text(mode == 0 ? R.string.FreezgramPanelPreviewInfo : mode == 1 ? R.string.FreezgramSharedGlassPreviewInfo : R.string.FreezgramComposerPreviewInfo));
        info.setTextSize(14);
        info.setTextColor(getThemedColor(Theme.key_windowBackgroundWhiteGrayText));
        info.setPadding(dp(20), dp(12), dp(20), dp(12));
        content.addView(info);
        if (mode == 1) {
            blur = slider(context, content, R.string.FreezgramPanelBlur, 30,
                    AppearanceConfig.navigationGlassBlur(), value -> {
                        AppearanceConfig.navigationGlassBlur.setConfigInt(value); geometryChanged = true; preview.invalidate();
                    });
            intensity = slider(context, content, R.string.FreezgramPanelIntensity, 100,
                    AppearanceConfig.navigationGlassIntensity(), value -> {
                        AppearanceConfig.navigationGlassIntensity.setConfigInt(value); geometryChanged = true; preview.invalidate();
                    });
            transparency = slider(context, content, R.string.FreezgramPanelTransparency, 100,
                    effectiveTransparency(), value -> {
                        AppearanceConfig.navigationGlassTransparency.setConfigInt(value); geometryChanged = true; preview.invalidate();
                    });
        }
        if (mode == 0) {
            width = slider(context, content, R.string.FreezgramPanelWidth, 100,
                    AppearanceConfig.navigationPanelWidth(), value -> {
                        AppearanceConfig.navigationPanelWidth.setConfigInt(Math.max(80, value));
                        width.setValue(Math.max(80, value)); geometryChanged = true; preview.updateGeometry();
                    });
            lift = slider(context, content, R.string.FreezgramPanelLift, 64,
                    AppearanceConfig.navigationPanelLift(), value -> {
                        AppearanceConfig.navigationPanelLift.setConfigInt(value); geometryChanged = true; preview.updateGeometry();
                    });
            contacts = new org.telegram.ui.Cells.TextCheckCell(context);
            contacts.setTextAndCheck(text(R.string.MainTabsContacts), !xyz.nextalone.nagram.NaConfig.INSTANCE.getMainTabsHideContacts().Bool(), false);
            contacts.setOnClickListener(v -> {
                boolean hidden = !xyz.nextalone.nagram.NaConfig.INSTANCE.getMainTabsHideContacts().Bool();
                xyz.nextalone.nagram.NaConfig.INSTANCE.getMainTabsHideContacts().setConfigBool(hidden);
                contacts.setChecked(!hidden); geometryChanged = true; preview.updateGeometry();
            });
            content.addView(contacts);
        }
        if (mode == 2) {
            textInset = slider(context, content, R.string.FreezgramComposerTextInset, 24,
                    AppearanceConfig.composerTextInset(), value -> {
                        AppearanceConfig.composerTextInset.setConfigInt(value); geometryChanged = true; preview.invalidate();
                    });
            emojiInset = slider(context, content, R.string.FreezgramComposerEmojiInset, 16,
                    AppearanceConfig.composerEmojiInset(), value -> {
                        AppearanceConfig.composerEmojiInset.setConfigInt(value); geometryChanged = true; preview.invalidate();
                    });
        }
        TextView reset = new TextView(context);
        reset.setText(text(R.string.FreezgramPanelReset));
        reset.setTextSize(16);
        reset.setTextColor(getThemedColor(Theme.key_windowBackgroundWhiteBlueText));
        reset.setPadding(dp(22), dp(20), dp(22), dp(24));
        reset.setOnClickListener(v -> {
            if (mode == 1) {
                AppearanceConfig.navigationGlassBlur.setConfigInt(6);
                AppearanceConfig.navigationGlassIntensity.setConfigInt(55);
                AppearanceConfig.navigationGlassTransparency.setConfigInt(-1);
                blur.setValue(6); intensity.setValue(55); transparency.setValue(effectiveTransparency());
            } else if (mode == 0) {
                AppearanceConfig.navigationPanelWidth.setConfigInt(100);
                AppearanceConfig.navigationPanelLift.setConfigInt(12);
                width.setValue(100); lift.setValue(12); preview.updateGeometry();
            } else {
                AppearanceConfig.composerTextInset.setConfigInt(12);
                AppearanceConfig.composerEmojiInset.setConfigInt(6);
                textInset.setValue(12); emojiInset.setValue(6);
            }
            geometryChanged = true;
            preview.invalidate();
        });
        content.addView(reset);
        fragmentView = scroll;
        return fragmentView;
    }

    @Override public void onFragmentDestroy() {
        android.app.Activity activity = getParentActivity();
        super.onFragmentDestroy();
        if (geometryChanged && activity instanceof org.telegram.ui.LaunchActivity) {
            AndroidUtilities.runOnUIThread(() -> ((org.telegram.ui.LaunchActivity) activity).rebuildAllFragments(false));
        }
    }

    private int effectiveTransparency() {
        return Math.round(100 * (1 - IosLiquidGlassNavigation.overlayAlpha(Theme.isCurrentThemeDark())));
    }

    private AvatarCornersSeekBar slider(Context context, LinearLayout parent, int title, int max,
                                       int value, AvatarCornersSeekBar.OnDrag onDrag) {
        AvatarCornersSeekBar slider = new AvatarCornersSeekBar(context, onDrag, title == R.string.FreezgramPanelWidth ? 80 : title == R.string.FreezgramComposerTextInset ? 4 : 0, max,
                text(title), title == R.string.FreezgramPanelWidth ? "80" : title == R.string.FreezgramComposerTextInset ? "4" : "0", String.valueOf(max));
        slider.setValueSuffix(max == 100 ? "%" : "dp");
        slider.setValue(value);
        parent.addView(slider, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 112));
        return slider;
    }

    private static int dp(float value) { return AndroidUtilities.dp(value); }

    private final class GlassPreview extends FrameLayout {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final RectF panel = new RectF();
        private BlurredBackgroundSourceRenderNode source;
        private BlurredBackgroundDrawable glass, headerGlass, fieldGlass, leftGlass, rightGlass;
        private final android.graphics.Rect field = new android.graphics.Rect(), leftButton = new android.graphics.Rect(), rightButton = new android.graphics.Rect();
        private final android.graphics.drawable.Drawable attachIcon, emojiIcon, micIcon;

        private LinearLayout tabs;
        private GlassTabView contactTab;

        GlassPreview(Context context) {
            super(context);
            setWillNotDraw(false);
            attachIcon = androidx.core.content.ContextCompat.getDrawable(context, R.drawable.msg_input_attach2).mutate();
            emojiIcon = androidx.core.content.ContextCompat.getDrawable(context, R.drawable.input_smile).mutate();
            micIcon = androidx.core.content.ContextCompat.getDrawable(context, R.drawable.input_mic).mutate();
            tabs = new LinearLayout(context);
            tabs.setOrientation(LinearLayout.HORIZONTAL);
            GlassTabView[] buttons = {
                    GlassTabView.createMainTab(context, resourceProvider, GlassTabView.TabAnimation.CHATS, R.string.MainTabsChats),
                    GlassTabView.createMainTab(context, resourceProvider, GlassTabView.TabAnimation.SETTINGS, R.string.Settings),
                    GlassTabView.createAvatar(context, resourceProvider, currentAccount, R.string.MainTabsProfile)
            };
            for (int i = 0; i < buttons.length; i++) {
                GlassTabView button = buttons[i];
                button.setSelected(i == 0, false);
                button.setOnClickListener(v -> {
                    for (GlassTabView tab : buttons) tab.setSelected(tab == v, true);
                });
                tabs.addView(button, new LinearLayout.LayoutParams(0, LayoutHelper.MATCH_PARENT, 1f));
            }
            contactTab = GlassTabView.createMainTab(context, resourceProvider, GlassTabView.TabAnimation.CONTACTS, R.string.MainTabsContacts);
            contactTab.setOnClickListener(v -> {
                for (GlassTabView tab : buttons) tab.setSelected(false, true);
                contactTab.setSelected(true, true);
            });
            tabs.addView(contactTab, 1, new LinearLayout.LayoutParams(0, LayoutHelper.MATCH_PARENT, 1f));
            for (GlassTabView button : buttons) button.setOnClickListener(v -> {
                contactTab.setSelected(false, true);
                for (GlassTabView tab : buttons) tab.setSelected(tab == v, true);
            });
            FrameLayout.LayoutParams tabsLayout = new FrameLayout.LayoutParams(LayoutHelper.MATCH_PARENT, dp(60));
            tabsLayout.setMargins(dp(12), dp(148), dp(12), 0);
            addView(tabs, tabsLayout);
            updateGeometry();
            // The actual AGSL renderer; unsupported phones show the same opaque fallback.
            if (Build.VERSION.SDK_INT >= 33) {
                source = new BlurredBackgroundSourceRenderNode(null);
                glass = createGlass(30, 0);
                headerGlass = createGlass(23, 0);
                fieldGlass = createGlass(24, 7);
                leftGlass = createGlass(24, 7);
                rightGlass = createGlass(24, 7);
            }
        }

        void updateGeometry() {
            float side = dp(12) + Math.max(0, getWidth() - dp(24)) * (100 - AppearanceConfig.navigationPanelWidth()) / 200f;
            float top = dp((mode == 1 ? 296 : 160) - AppearanceConfig.navigationPanelLift());
            panel.set(side, top, getWidth() - side, top + dp(60));
            FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) tabs.getLayoutParams();
            lp.setMargins(Math.round(side), Math.round(top), Math.round(side), 0);
            tabs.setLayoutParams(lp);
            tabs.setVisibility(mode == 2 ? GONE : VISIBLE);
            contactTab.setVisibility(xyz.nextalone.nagram.NaConfig.INSTANCE.getMainTabsHideContacts().Bool() ? GONE : VISIBLE);
            invalidate();
        }

        @Override protected void onSizeChanged(int w, int h, int oldw, int oldh) {
            super.onSizeChanged(w, h, oldw, oldh); updateGeometry();
        }

        @Override protected boolean verifyDrawable(android.graphics.drawable.Drawable who) {
            return who == glass || who == headerGlass || who == fieldGlass || who == leftGlass || who == rightGlass || super.verifyDrawable(who);
        }

        private void background(Canvas canvas) {
            canvas.drawColor(getThemedColor(Theme.key_windowBackgroundWhite));
            for (int i = 0; i < (mode == 1 ? 7 : 4); i++) {
                float y = dp(32 + i * 55);
                paint.setColor(new int[]{0xff459de3, 0xff8871d7, 0xff50b7a1, 0xffd58b56}[i % 4]);
                canvas.drawCircle(dp(37), y, dp(21), paint);
                paint.setColor(getThemedColor(Theme.key_windowBackgroundWhiteBlackText));
                paint.setTextSize(dp(15));
                canvas.drawText(i % 2 == 0 ? "Freezgram" : text(R.string.MainTabsChats), dp(72), y, paint);
                paint.setAlpha(100);
                canvas.drawRoundRect(dp(72), y + dp(8), getWidth() - dp(28), y + dp(12), dp(2), dp(2), paint);
                paint.setAlpha(255);
            }
        }

        private boolean effectsEnabled() {
            return Build.VERSION.SDK_INT >= 33 && org.telegram.messenger.SharedConfig.chatBlurEnabled()
                    && !org.telegram.messenger.LiteMode.isPowerSaverApplied();
        }

        private BlurredBackgroundDrawable createGlass(int radius, int padding) {
            BlurredBackgroundDrawable drawable = source.createDrawable();
            drawable.setColorProvider(LiquidGlassStyle.colors(resourceProvider, this::effectsEnabled));
            drawable.setRadius(dp(radius)); drawable.setPadding(dp(padding)); drawable.setCallback(this);
            return drawable;
        }

        private void surface(Canvas canvas, BlurredBackgroundDrawable drawable, android.graphics.Rect bounds, int radius, int padding) {
            if (drawable != null && canvas.isHardwareAccelerated()) {
                drawable.setBounds(bounds);
                LiquidGlassStyle.configure(drawable);
                var node = (org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawableRenderNode) drawable;
                node.setLiquidGlassEffectAllowed(effectsEnabled());
                drawable.updateColors(); node.invalidateDisplayList(); drawable.draw(canvas);
            } else {
                paint.setColor(Theme.multAlpha(getThemedColor(Theme.key_windowBackgroundWhite), .82f));
                canvas.drawRoundRect(bounds.left + dp(padding), bounds.top + dp(padding), bounds.right - dp(padding), bounds.bottom - dp(padding), dp(radius), dp(radius), paint);
            }
        }

        private void icon(Canvas canvas, android.graphics.drawable.Drawable drawable, float x, float y) {
            drawable.setTint(getThemedColor(Theme.key_glass_defaultIcon));
            drawable.setBounds(Math.round(x - dp(12)), Math.round(y - dp(12)), Math.round(x + dp(12)), Math.round(y + dp(12)));
            drawable.draw(canvas);
        }

        @Override protected void onDraw(Canvas canvas) {
            background(canvas);
            if (source != null && canvas.isHardwareAccelerated()) {
                Canvas capture = source.beginRecording(getWidth(), getHeight());
                background(capture); source.endRecording();
                source.setBlur(AndroidUtilities.dpf2(LiquidGlassStyle.blurRadiusDp()));
            }
            if (mode != 2) surface(canvas, glass, new android.graphics.Rect((int) panel.left, (int) panel.top, (int) panel.right, (int) panel.bottom), 30, 0);
            if (mode != 0) {
                if (mode == 1) {
                    surface(canvas, headerGlass, new android.graphics.Rect(dp(12), dp(12), getWidth()-dp(12), dp(60)), 23, 0);
                    paint.setColor(getThemedColor(Theme.key_windowBackgroundWhiteBlackText)); paint.setTextSize(dp(16));
                    canvas.drawText("Freezgram", dp(32), dp(43), paint);
                }
                int top = dp(mode == 1 ? 128 : 118);
                android.graphics.Rect whole = new android.graphics.Rect(0, top, getWidth(), top + dp(58));
                boolean split = AppearanceConfig.chatComposerStyle() != 2;
                ChatComposerGlass.surfaceBounds(whole, field, leftButton, rightButton, split);
                surface(canvas, fieldGlass, field, 24, 7);
                if (split) {
                    surface(canvas, leftGlass, leftButton, 24, 7);
                    surface(canvas, rightGlass, rightButton, 24, 7);
                }
                float y = whole.bottom - dp(29);
                icon(canvas, attachIcon, dp(split ? 29 : 26), y);
                icon(canvas, micIcon, getWidth() - dp(29), y);
                float emojiX = split ? getWidth() - dp(66 + ChatComposerGlass.emojiRightInsetDp()) : dp(70);
                icon(canvas, emojiIcon, emojiX, y);
                float textX = dp(split ? ChatComposerGlass.textLeftInsetDp() : 94);
                paint.setColor(getThemedColor(Theme.key_windowBackgroundWhiteGrayText)); paint.setTextSize(dp(16));
                canvas.save();
                canvas.clipRect(textX, top, split ? emojiX - dp(22) : getWidth() - dp(55), whole.bottom);
                canvas.drawText(text(R.string.TypeMessage), textX, y - (paint.ascent() + paint.descent()) / 2, paint);
                canvas.restore();
            }
        }
    }
}
