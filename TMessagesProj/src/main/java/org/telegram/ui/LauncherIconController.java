package org.telegram.ui;

import android.content.ComponentName;
import android.content.Context;
import android.content.pm.PackageManager;

import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.R;

public class LauncherIconController {
    // Compatibility aliases keep an existing launcher entry usable during an update.
    // They all show the Freezgram artwork and are disabled after selecting a current icon.
    private static final String[] LEGACY_ICONS = {
        "BlueprintIcon", "RedIcon", "NyaIcon", "AyuIcon",
        "QuackIcon", "GoIcon", "HandIcon", "MonoIcon",
        "NothingIcon", "PlusIcon", "TelegramIcon", "VintageIcon",
        "AquaIcon", "PremiumIcon", "TurboIcon", "NoxIcon"
    };

    public static void tryFixLauncherIconIfNeeded() {
        LauncherIcon selected = LauncherIcon.EXTERALESS;
        for (LauncherIcon icon : LauncherIcon.values()) {
            if (isEnabled(icon)) {
                selected = icon;
                break;
            }
        }
        setIcon(selected);
    }

    public static boolean isEnabled(LauncherIcon icon) {
        Context ctx = ApplicationLoader.applicationContext;
        int i = ctx.getPackageManager().getComponentEnabledSetting(icon.getComponentName(ctx));
        // Пока пользователь ничего не выбирал, включённой считается наша иконка:
        // именно она стоит у <application> в манифесте, и переключатель должен
        // показывать выбранным то, что человек видит на рабочем столе.
        return i == PackageManager.COMPONENT_ENABLED_STATE_ENABLED
                || i == PackageManager.COMPONENT_ENABLED_STATE_DEFAULT && icon == LauncherIcon.EXTERALESS;
    }

    public static void setIcon(LauncherIcon icon) {
        Context ctx = ApplicationLoader.applicationContext;
        PackageManager pm = ctx.getPackageManager();
        // Enable the replacement before disabling any entry, avoiding a launcher gap.
        if (pm.getComponentEnabledSetting(icon.getComponentName(ctx)) != PackageManager.COMPONENT_ENABLED_STATE_ENABLED) {
            pm.setComponentEnabledSetting(icon.getComponentName(ctx), PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                    PackageManager.DONT_KILL_APP);
        }
        for (LauncherIcon other : LauncherIcon.values()) {
            if (other != icon) {
                disableIcon(pm, other.getComponentName(ctx));
            }
        }
        for (String legacy : LEGACY_ICONS) {
            disableIcon(pm, new ComponentName(ctx.getPackageName(), "org.telegram.messenger." + legacy));
        }
    }

    private static void disableIcon(PackageManager pm, ComponentName name) {
        if (pm.getComponentEnabledSetting(name) != PackageManager.COMPONENT_ENABLED_STATE_DISABLED) {
            pm.setComponentEnabledSetting(name, PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                    PackageManager.DONT_KILL_APP);
        }
    }

    public enum LauncherIcon {
        EXTERALESS("ExteralessIcon", R.drawable.exteraless_icon_background,
                R.drawable.exteraless_icon_foreground, R.string.AppIconExteraless),
        FREEZGRAM_WHITE("FreezgramWhiteIcon", R.drawable.freezgram_white_icon_background,
                R.drawable.freezgram_white_icon_foreground, R.string.AppIconFreezgramWhite),
        FREEZGRAM_MONO_DARK("FreezgramMonoDarkIcon", R.drawable.freezgram_mono_dark_icon_background,
                R.drawable.freezgram_mono_dark_icon_foreground, R.string.AppIconFreezgramMonoDark);


        public final String key;
        public final int background;
        public final int foreground;
        public final int title;
        public final boolean premium;

        private ComponentName componentName;

        public ComponentName getComponentName(Context ctx) {
            if (componentName == null) {
                componentName = new ComponentName(ctx.getPackageName(), "org.telegram.messenger." + key);
            }
            return componentName;
        }

        LauncherIcon(String key, int background, int foreground, int title) {
            this(key, background, foreground, title, false);
        }

        LauncherIcon(String key, int background, int foreground, int title, boolean premium) {
            this.key = key;
            this.background = background;
            this.foreground = foreground;
            this.title = title;
            this.premium = premium;
        }

    }
}
