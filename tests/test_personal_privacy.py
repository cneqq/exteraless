"""Local privacy regressions with synthetic values; no APK build or real account."""
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

MAIN = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main'
JAVA = MAIN / 'java'


def method(source, signature):
    start = source.index(signature)
    return source[start:source.index('\n    }', start) + len('\n    }')]


def run_java(body):
    with tempfile.TemporaryDirectory(prefix='privacy-regression-') as directory:
        source = Path(directory) / 'PrivacyCheck.java'
        source.write_text(body)
        subprocess.run(['java', str(source)], check=True, capture_output=True, text=True)


class PersonalPrivacyTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_startup_without_login_draft_opens_intro(self):
        launch = (JAVA / 'org/telegram/ui/LaunchActivity.java').read_text()
        selection = method(launch, '    private BaseFragment getClientNotActivatedFragment(')
        run_java('''
class PrivacyCheck {
  static class Bundle {
    int view;
    Bundle(int view) { this.view = view; }
    int getInt(String key, int fallback) { return view; }
  }
  static class BaseFragment {}
  static class IntroActivity extends BaseFragment {}
  static class LoginActivity extends BaseFragment {
    static Bundle state;
    static Bundle loadCurrentState(boolean newAccount, int account) { return state; }
  }
  int currentAccount;
  SELECTION
  public static void main(String[] args) {
    PrivacyCheck launch = new PrivacyCheck();
    for (Bundle state : new Bundle[]{null, new Bundle(0), new Bundle(1)}) {
      LoginActivity.state = state;
      BaseFragment result = launch.getClientNotActivatedFragment();
      boolean resume = state != null && state.view != 0;
      if (resume ? !(result instanceof LoginActivity) : !(result instanceof IntroActivity))
        throw new AssertionError("Wrong unauthenticated startup screen");
    }
  }
}
'''.replace('SELECTION', selection))

    def test_backup_is_disabled_and_transfer_exclusions_cover_private_data(self):
        ns = '{http://schemas.android.com/apk/res/android}'
        app = ET.parse(MAIN / 'AndroidManifest.xml').getroot().find('application')
        self.assertEqual(app.get(ns + 'allowBackup'), 'false')
        self.assertEqual(app.get(ns + 'fullBackupContent'), 'false')
        self.assertIsNone(app.get(ns + 'backupAgent'))
        rules = ET.parse(MAIN / 'res/xml/personal_data_extraction_rules.xml').getroot()
        for group in ('cloud-backup', 'device-transfer'):
            excluded = {e.get('domain') for e in rules.find(group).findall('exclude') if e.get('path') == '.'}
            self.assertTrue({'root', 'sharedpref', 'database', 'file', 'external', 'device_root'} <= excluded)

    def test_sensitive_log_sinks_and_mutable_debug_assignment_are_removed(self):
        for name in ('org/telegram/ui/LoginActivity.java', 'org/telegram/messenger/AuthTokensHelper.java'):
            text = (JAVA / name).read_text()
            self.assertIsNone(re.search(r'FileLog\.[dew]\([^\n]*\.future_auth_token', text), name)
            self.assertIsNone(re.search(r'FileLog\.[dew]\([^\n]*phone_code_hash', text), name)
            self.assertNotIn('BackupAgent.requestBackup', text)
        debug = (JAVA / 'org/telegram/messenger/BuildVars.java').read_text()
        self.assertIn('public static final boolean DEBUG_VERSION', debug)
        toggle = (JAVA / 'tw/nekomimi/nekogram/utils/AndroidUtil.java').read_text()
        self.assertNotRegex(toggle, r'BuildVars.DEBUG_VERSION\s*=')
        self.assertNotIn('_log(f"token:', (MAIN / 'python/dev_server.py').read_text())

    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_actual_ai_url_policy(self):
        policy = (JAVA / 'org/telegram/messenger/SecureAiUrl.java').read_text()
        policy = policy[policy.index('public final class'):].replace('public final class', 'final class', 1)
        run_java('''import java.net.URI;
class PrivacyCheck {
  public static void main(String[] args) {
    for (String valid : new String[]{"https://api.example.test/v1", "HTTPS://example.test:8443/v1?q=x"}) {
      if (!valid.equals(SecureAiUrl.requireHttps(valid))) throw new AssertionError("URL changed");
    }
    for (String bad : new String[]{"http://example.test", "http://127.0.0.1:11434", "https://u:p@example.test", "https://example.test/#x", "file:///tmp/key", "https:///no-host", "bad url"}) {
      boolean rejected = false;
      try { SecureAiUrl.requireHttps(bad); } catch (IllegalArgumentException e) { rejected = true; }
      if (!rejected) throw new AssertionError("Unsafe URL accepted");
    }
  }
}
''' + policy)

    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_actual_login_state_cleanup_preserves_unrelated_data(self):
        login = (JAVA / 'org/telegram/ui/LoginActivity.java').read_text()
        tokens = (JAVA / 'org/telegram/messenger/AuthTokensHelper.java').read_text()
        parts = [method(login, signature) for signature in (
            '    public static Bundle loadCurrentState(',
            '    private void clearCurrentState(',
            '    public void saveSelfArgs(')]
        cleanup = method(tokens, '    public static void clearSavedLoginState(')
        run_java('''import java.util.*;
class PrivacyCheck {
  static class Bundle {}
  static class Context { static int MODE_PRIVATE = 0; }
  static class UserConfig { static int MAX_ACCOUNT_COUNT = 4; }
  static class Prefs {
    Map<String,String> values = new HashMap<>();
    Prefs edit() { return this; }
    Prefs clear() { values.clear(); return this; }
    void apply() {}
    boolean commit() { return true; }
  }
  interface SharedPreferences { interface Editor {} }
  static class AppContext {
    Map<String,Prefs> stores = new HashMap<>();
    Prefs getSharedPreferences(String name,int mode) { return stores.computeIfAbsent(name,k->new Prefs()); }
  }
  static class ApplicationLoader { static AppContext applicationContext = new AppContext(); }
  static class AuthTokensHelper { CLEANUP }
  static class Login {
    boolean newAccount = true; int currentAccount = 1;
    METHODS
  }
  public static void main(String[] args) {
    AppContext ctx = ApplicationLoader.applicationContext;
    for (String name : new String[]{"logininfo2","logininfo2_0","logininfo2_1","logininfo2_2","logininfo2_3"})
      ctx.getSharedPreferences(name,0).values.put("passview_code", "SYNTHETIC_NOT_A_REAL_PASSWORD");
    ctx.getSharedPreferences("userconf",0).values.put("session", "SYNTHETIC_SESSION");
    if (Login.loadCurrentState(false,0) != null) throw new AssertionError("Draft restored");
    for (var entry : ctx.stores.entrySet()) {
      if (entry.getKey().startsWith("logininfo2") && !entry.getValue().values.isEmpty()) throw new AssertionError("Draft retained");
    }
    ctx.getSharedPreferences("logininfo2_1",0).values.put("code","SYNTHETIC_CODE");
    new Login().saveSelfArgs(new Bundle());
    if (!ctx.getSharedPreferences("logininfo2_1",0).values.isEmpty()) throw new AssertionError("State persisted");
    if (!"SYNTHETIC_SESSION".equals(ctx.getSharedPreferences("userconf",0).values.get("session"))) throw new AssertionError("Session changed");
  }
}
'''.replace('CLEANUP', cleanup).replace('METHODS', '\n'.join(parts))
            .replace('SharedPreferences preferences =', 'Prefs preferences =')
            .replace('SharedPreferences.Editor editor =', 'Prefs editor ='))


if __name__ == '__main__':
    unittest.main()
