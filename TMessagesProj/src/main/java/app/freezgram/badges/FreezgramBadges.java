package app.freezgram.badges;

import android.content.Context;
import android.graphics.drawable.Drawable;

import androidx.core.content.ContextCompat;

import org.telegram.messenger.LocaleController;
import org.telegram.messenger.ChatObject;
import org.telegram.messenger.R;
import org.telegram.tgnet.TLRPC;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.Components.BulletinFactory;

/** Built-in community badges; no remote service or Telegram verification changes. */
public final class FreezgramBadges {
    private static final long FOUNDER_ID = 966442694L;
    private static final long OFFICIAL_CHANNEL_ID = 4480543290L;

    private FreezgramBadges() {}

    public static boolean hasBadge(TLRPC.User user) {
        return user != null && user.id == FOUNDER_ID
                && !user.scam && !user.fake && !user.verified;
    }

    public static Drawable getDrawable(Context context) {
        Drawable plane = ContextCompat.getDrawable(context, R.drawable.freezgram_settings_icon);
        return plane == null ? null : new FreezgramBadgeDrawable(plane.mutate());
    }

    public static boolean hasChannelBadge(TLRPC.Chat chat) {
        return chat != null && chat.id == OFFICIAL_CHANNEL_ID && ChatObject.isChannel(chat)
                && !chat.megagroup && !chat.scam && !chat.fake && !chat.verified;
    }

    public static Drawable getChannelDrawable(Context context) {
        return getDrawable(context);
    }

    public static String getTitle() {
        return LocaleController.getString(R.string.FreezgramBadgeFounder);
    }

    public static void showInfo(BaseFragment fragment) {
        showInfo(fragment, false);
    }

    public static String getChannelTitle() {
        return LocaleController.getString(R.string.FreezgramBadgeOfficialChannel);
    }

    public static void showChannelInfo(BaseFragment fragment) {
        showInfo(fragment, true);
    }

    private static void showInfo(BaseFragment fragment, boolean channel) {
        if (fragment == null || fragment.getContext() == null) {
            return;
        }
        BulletinFactory.of(fragment).createSimpleBulletin(
                getDrawable(fragment.getContext()), channel ? getChannelTitle() : getTitle(),
                LocaleController.getString(R.string.FreezgramBadgeLocalInfo)).show();
    }
}
