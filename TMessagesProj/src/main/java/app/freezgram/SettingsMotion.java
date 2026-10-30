package app.freezgram;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.animation.ValueAnimator;
import android.os.Build;
import android.view.View;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.SharedConfig;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.Components.CubicBezierInterpolator;

/** Local transitions for Freezgram settings; system/app animation opt-outs remain authoritative. */
public final class SettingsMotion {
    private SettingsMotion() {}

    public static boolean appliesTo(BaseFragment fragment) {
        String name = fragment.getClass().getName();
        return name.startsWith("app.exteraless.settings.") || name.startsWith("app.freezgram.");
    }

    public static AnimatorSet transition(BaseFragment fragment, boolean opening, Runnable completion) {
        if (!appliesTo(fragment) || !SharedConfig.animationsEnabled()
                || Build.VERSION.SDK_INT >= 26 && !ValueAnimator.areAnimatorsEnabled()) return null;
        View content = fragment.getFragmentView();
        if (content == null || !(content.getParent() instanceof View)) return null;
        View container = (View) content.getParent();
        float travel = AndroidUtilities.dp(28);
        container.setAlpha(opening ? 0f : 1f);
        container.setTranslationX(opening ? travel : 0f);
        AnimatorSet animation = new AnimatorSet();
        animation.playTogether(
                ObjectAnimator.ofFloat(container, View.ALPHA, opening ? 0f : 1f, opening ? 1f : 0f),
                ObjectAnimator.ofFloat(container, View.TRANSLATION_X, opening ? travel : 0f, opening ? 0f : travel));
        animation.setDuration(opening ? 320 : 280);
        animation.setInterpolator(CubicBezierInterpolator.EASE_BOTH);
        animation.addListener(new AnimatorListenerAdapter() {
            private boolean finished;
            private void finish() {
                if (finished) return;
                finished = true;
                container.setAlpha(1f);
                container.setTranslationX(0f);
                completion.run();
            }
            @Override public void onAnimationCancel(Animator animator) { finish(); }
            @Override public void onAnimationEnd(Animator animator) { finish(); }
        });
        animation.start();
        return animation;
    }
}
