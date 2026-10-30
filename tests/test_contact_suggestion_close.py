"""Local per-account suggestion dismissal leaves other peer-bar actions untouched."""
from pathlib import Path
import shutil,unittest
from test_personal_privacy import method,run_java

@unittest.skipUnless(shutil.which('java'),'Java source launcher required')
class ContactCloseTests(unittest.TestCase):
 def test_only_plain_add_contact_is_dismissed_and_saved_per_account(self):
  path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/org/telegram/ui/ChatActivity.java'
  source=path.read_text();dismiss=method(source,'    private boolean dismissAddContactSuggestion()')
  start=source.index('        boolean showAdd = preferences.getBoolean("dialog_bar_add"')
  policy=source[start:source.index('\n',source.index('        showAdd &= ',start))]
  run_java('''
class PrivacyCheck{
 User currentUser=new User();Button addToContactsButton=new Button();Object currentEncryptedChat;
 boolean addToContactsButtonArchive;long dialog_id=42;int currentAccount,updates;
 void updateTopPanel(boolean animated){updates++;}
 DISMISS
 static boolean offered(Prefs preferences,long did){boolean DEBUG_TOP_PANELS=false;POLICY return showAdd;}
 public static void main(String[] args){
  for(int bits=0;bits<32;bits++){
   var p=new PrivacyCheck();p.currentUser.contact=(bits&1)!=0;p.currentUser.self=(bits&2)!=0;p.addToContactsButton.visible=(bits&4)==0;
   p.addToContactsButtonArchive=(bits&8)!=0;p.addToContactsButton.tag=(bits&16)!=0?new Object():null;
   if(p.dismissAddContactSuggestion()!=(bits==0)||p.updates!=(bits==0?1:0))throw new AssertionError("Other peer action dismissed");
  }
  var p=new PrivacyCheck();p.currentAccount=1;p.dismissAddContactSuggestion();
  if(offered(MessagesController.getNotificationsSettings(1),42)||!offered(MessagesController.getNotificationsSettings(2),42)||!offered(MessagesController.getNotificationsSettings(1),43))throw new AssertionError("Dismissal leaked across accounts/chats");
  p.currentEncryptedChat=new Object();p.currentUser.id=99;p.dismissAddContactSuggestion();
  if(offered(MessagesController.getNotificationsSettings(1),99))throw new AssertionError("Encrypted peer key differs from read path");
 }
}
class View{static final int VISIBLE=0;}
class User{boolean contact,self;long id=42;}
class Button{boolean visible=true;Object tag;int getVisibility(){return visible?0:8;}Object getTag(){return tag;}}
class MessagesController{static java.util.Map<Integer,Prefs> accounts=new java.util.HashMap<>();static Prefs getNotificationsSettings(int a){return accounts.computeIfAbsent(a,k->new Prefs());}}
class Prefs{java.util.Map<String,Boolean> values=new java.util.HashMap<>();Prefs edit(){return this;}Prefs putBoolean(String k,boolean v){values.put(k,v);return this;}void apply(){}boolean getBoolean(String k,boolean fallback){return k.startsWith("dialog_bar_add")?true:values.getOrDefault(k,fallback);}}
'''.replace('DISMISS',dismiss).replace('POLICY',policy))
