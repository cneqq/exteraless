package app.exteraless.shortcuts;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Toast;

import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.FileLog;
import org.telegram.messenger.LocaleController;
import org.telegram.messenger.R;

import tw.nekomimi.nekogram.NekoConfig;

public class QuickToggleActivity extends Activity {

    public static final String ACTION_GHOST_MODE = "app.exteraless.action.TOGGLE_GHOST_MODE";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        final String action = getIntent() == null ? null : getIntent().getAction();
        CharSequence message = null;
        try {
            ApplicationLoader.postInitApplication();
            if (ACTION_GHOST_MODE.equals(action)) {
                message = toggleGhostMode();
            }
        } catch (Throwable e) {
            FileLog.e(e);
        }
        if (message != null) {
            Toast.makeText(getApplicationContext(), message, Toast.LENGTH_SHORT).show();
        }
        finish();
    }

    private CharSequence toggleGhostMode() {
        try {
            NekoConfig.toggleGhostMode();
        } catch (Throwable e) {
            FileLog.e(e);
        }
        return LocaleController.getString(NekoConfig.isGhostModeActive()
                ? R.string.GhostModeEnabled
                : R.string.GhostModeDisabled);
    }

}
