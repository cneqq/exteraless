package app.exteraless.settings;

import android.content.Context;
import android.content.pm.PackageInfo;
import android.text.TextUtils;
import android.util.TypedValue;
import android.view.Gravity;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;


import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.BuildVars;
import org.telegram.messenger.LocaleController;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Components.LayoutHelper;

/** Freezgram settings header with an unmasked, aspect-preserving paper-plane logo. */
public class AboutHeaderCell extends LinearLayout {

    private final ImageView logo;

    public AboutHeaderCell(Context context) {
        super(context);
        setOrientation(VERTICAL);
        setGravity(Gravity.CENTER);

        logo = new ImageView(context);
        logo.setScaleType(ImageView.ScaleType.FIT_CENTER);
        logo.setImageResource(R.drawable.exteraless_icon);
        addView(logo, LayoutHelper.createLinear(72, 72,
                Gravity.TOP | Gravity.CENTER_HORIZONTAL, 0, 40, 0, 0));

        TextView title = new TextView(context);
        title.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlackText));
        title.setTypeface(AndroidUtilities.bold());
        title.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 20);
        title.setGravity(Gravity.CENTER);
        title.setSingleLine(true);
        title.setText(LocaleController.getString(R.string.OpenExtera));
        addView(title, LayoutHelper.createLinear(LayoutHelper.WRAP_CONTENT, LayoutHelper.WRAP_CONTENT,
                Gravity.TOP | Gravity.CENTER_HORIZONTAL, 50, 16, 50, 0));

        TextView version = new TextView(context);
        version.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteGrayText));
        version.setTypeface(AndroidUtilities.bold());
        version.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 15);
        version.setGravity(Gravity.CENTER);
        version.setLineSpacing(AndroidUtilities.dp(2), 1f);
        version.setText(buildVersionString());
        addView(version, LayoutHelper.createLinear(LayoutHelper.WRAP_CONTENT, LayoutHelper.WRAP_CONTENT,
                Gravity.TOP | Gravity.CENTER_HORIZONTAL, 60, 2, 60, 28));
    }

    public void setOnLogoClickListener(OnClickListener listener) {
        logo.setOnClickListener(listener);
    }

    /** "12.9.2 (1258)" — версия плюс versionCode из PackageInfo, как в оригинале. */
    public static String buildVersionString() {
        StringBuilder sb = new StringBuilder(BuildVars.BUILD_VERSION_STRING);
        try {
            PackageInfo info = ApplicationLoader.applicationContext.getPackageManager()
                    .getPackageInfo(ApplicationLoader.applicationContext.getPackageName(), 0);
            if (info != null) {
                sb.append(" (").append(info.versionCode).append(")");
            }
        } catch (Exception ignore) {
        }
        if (!TextUtils.isEmpty(BuildVars.BUILD_COMMIT_ID)) {
            sb.append(" · ").append(BuildVars.BUILD_COMMIT_ID);
        }
        return sb.toString();
    }
}
