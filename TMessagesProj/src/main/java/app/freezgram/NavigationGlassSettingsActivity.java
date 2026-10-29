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
    private GlassPreview preview;
    private AvatarCornersSeekBar blur, intensity, transparency, width, lift;
    private boolean geometryChanged;
    private org.telegram.ui.Cells.TextCheckCell contacts;

    private String text(int id) { return LocaleController.getString(id); }

    @Override
    public View createView(Context context) {
        actionBar.setBackButtonImage(R.drawable.ic_ab_back);
        actionBar.setTitle(text(R.string.FreezgramPanelSettings));
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
        content.addView(preview, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 240));
        TextView info = new TextView(context);
        info.setText(text(R.string.FreezgramPanelPreviewInfo));
        info.setTextSize(14);
        info.setTextColor(getThemedColor(Theme.key_windowBackgroundWhiteGrayText));
        info.setPadding(dp(20), dp(12), dp(20), dp(12));
        content.addView(info);
        blur = slider(context, content, R.string.FreezgramPanelBlur, 30,
                AppearanceConfig.navigationGlassBlur(), value -> {
                    AppearanceConfig.navigationGlassBlur.setConfigInt(value); preview.invalidate();
                });
        intensity = slider(context, content, R.string.FreezgramPanelIntensity, 100,
                AppearanceConfig.navigationGlassIntensity(), value -> {
                    AppearanceConfig.navigationGlassIntensity.setConfigInt(value); preview.invalidate();
                });
        transparency = slider(context, content, R.string.FreezgramPanelTransparency, 100,
                effectiveTransparency(), value -> {
                    AppearanceConfig.navigationGlassTransparency.setConfigInt(value); preview.invalidate();
                });
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
            if (!hidden) AppearanceConfig.showFeedTab.setConfigBool(false);
            contacts.setChecked(!hidden); geometryChanged = true; preview.updateGeometry();
        });
        content.addView(contacts);
        TextView reset = new TextView(context);
        reset.setText(text(R.string.FreezgramPanelReset));
        reset.setTextSize(16);
        reset.setTextColor(getThemedColor(Theme.key_windowBackgroundWhiteBlueText));
        reset.setPadding(dp(22), dp(20), dp(22), dp(24));
        reset.setOnClickListener(v -> {
            AppearanceConfig.navigationGlassBlur.setConfigInt(6);
            AppearanceConfig.navigationGlassIntensity.setConfigInt(55);
            AppearanceConfig.navigationGlassTransparency.setConfigInt(-1);
            AppearanceConfig.navigationPanelWidth.setConfigInt(100);
            AppearanceConfig.navigationPanelLift.setConfigInt(12);
            width.setValue(100); lift.setValue(12); geometryChanged = true; preview.updateGeometry();
            blur.setValue(6); intensity.setValue(55); transparency.setValue(effectiveTransparency());
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
        AvatarCornersSeekBar slider = new AvatarCornersSeekBar(context, onDrag, title == R.string.FreezgramPanelWidth ? 80 : 0, max,
                text(title), title == R.string.FreezgramPanelWidth ? "80" : "0", String.valueOf(max));
        slider.setValueSuffix(max == 30 || max == 64 ? "dp" : "%");
        slider.setValue(value);
        parent.addView(slider, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, 112));
        return slider;
    }

    private static int dp(float value) { return AndroidUtilities.dp(value); }

    private final class GlassPreview extends FrameLayout {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final RectF panel = new RectF();
        private BlurredBackgroundSourceRenderNode source;
        private BlurredBackgroundDrawable glass;

        private LinearLayout tabs;
        private GlassTabView contactTab;

        GlassPreview(Context context) {
            super(context);
            setWillNotDraw(false);
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
                glass = source.createDrawable();
                glass.setColorProvider(IosLiquidGlassNavigation.colors(resourceProvider));
                glass.setRadius(dp(30));
                glass.setCallback(this);
            }
        }

        void updateGeometry() {
            float side = dp(12) + Math.max(0, getWidth() - dp(24)) * (100 - AppearanceConfig.navigationPanelWidth()) / 200f;
            float top = dp(160 - AppearanceConfig.navigationPanelLift());
            panel.set(side, top, getWidth() - side, top + dp(60));
            FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) tabs.getLayoutParams();
            lp.setMargins(Math.round(side), Math.round(top), Math.round(side), 0);
            tabs.setLayoutParams(lp);
            contactTab.setVisibility(xyz.nextalone.nagram.NaConfig.INSTANCE.getMainTabsHideContacts().Bool() ? GONE : VISIBLE);
            invalidate();
        }

        @Override protected void onSizeChanged(int w, int h, int oldw, int oldh) {
            super.onSizeChanged(w, h, oldw, oldh); updateGeometry();
        }

        @Override protected boolean verifyDrawable(android.graphics.drawable.Drawable who) {
            return who == glass || super.verifyDrawable(who);
        }

        private void background(Canvas canvas) {
            canvas.drawColor(getThemedColor(Theme.key_windowBackgroundWhite));
            for (int i = 0; i < 4; i++) {
                float y = dp(32 + i * 55);
                paint.setColor(new int[]{0xff459de3, 0xff8871d7, 0xff50b7a1, 0xffd58b56}[i]);
                canvas.drawCircle(dp(37), y, dp(21), paint);
                paint.setColor(getThemedColor(Theme.key_windowBackgroundWhiteBlackText));
                paint.setTextSize(dp(15));
                canvas.drawText(i % 2 == 0 ? "Freezgram" : text(R.string.MainTabsChats), dp(72), y, paint);
                paint.setAlpha(100);
                canvas.drawRoundRect(dp(72), y + dp(8), getWidth() - dp(28), y + dp(12), dp(2), dp(2), paint);
                paint.setAlpha(255);
            }
        }

        @Override protected void onDraw(Canvas canvas) {
            background(canvas);

            if (glass != null && canvas.isHardwareAccelerated()) {
                Canvas capture = source.beginRecording(getWidth(), getHeight());
                background(capture);
                source.endRecording();
                source.setBlur(AndroidUtilities.dpf2(IosLiquidGlassNavigation.blurRadiusDp()));
                glass.setBounds((int) panel.left, (int) panel.top, (int) panel.right, (int) panel.bottom);
                IosLiquidGlassNavigation.refresh(glass);
                glass.updateColors();
                ((org.telegram.ui.Components.blur3.drawable.BlurredBackgroundDrawableRenderNode) glass).invalidateDisplayList();
                glass.draw(canvas);
            } else {
                paint.setColor(Theme.multAlpha(getThemedColor(Theme.key_windowBackgroundWhite), .82f));
                canvas.drawRoundRect(panel, dp(30), dp(30), paint);
            }
        }
    }
}
