package app.freezgram.badges;

import android.content.Context;
import android.graphics.drawable.Drawable;

import androidx.core.content.ContextCompat;

import org.telegram.messenger.LocaleController;
import org.telegram.messenger.R;
import org.telegram.tgnet.TLRPC;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.Components.BulletinFactory;

/** Built-in community badges; no remote service or Telegram verification changes. */
public final class FreezgramBadges {
    private static final long FOUNDER_ID = 966442694L;

    private FreezgramBadges() {}

    public static boolean hasBadge(TLRPC.User user) {
        return user != null && user.id == FOUNDER_ID
                && !user.scam && !user.fake && !user.verified;
    }

    public static Drawable getDrawable(Context context) {
        Drawable drawable = ContextCompat.getDrawable(context, R.drawable.freezgram_profile_badge);
        return drawable == null ? null : drawable.mutate();
    }

    public static String getTitle() {
        return LocaleController.getString(R.string.FreezgramBadgeFounder);
    }

    public static void showInfo(BaseFragment fragment) {
        if (fragment == null || fragment.getContext() == null) {
            return;
        }
        BulletinFactory.of(fragment).createSimpleBulletin(
                getDrawable(fragment.getContext()), getTitle(),
                LocaleController.getString(R.string.FreezgramBadgeLocalInfo)).show();
    }
}
