"""Verify recycled dialog rows release badges and retain peer-specific artwork."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method, run_java


class DialogBadgeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_recycled_rows_do_not_keep_another_peers_badge(self):
        path=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java/org/telegram/ui/Cells/DialogCell.java'
        update=method(path.read_text(), '    private void updateCommunityBadge()')
        run_java('''
class PrivacyCheck {
  Drawable communityBadge; int communityBadgeType;
  TLRPC.User user; TLRPC.Chat chat; Object customDialog; boolean folder,forum,dialogFolder,isTopic;
  boolean isFolderCell(){return folder;}boolean isForumCell(){return forum;}boolean isDialogFolder(){return dialogFolder;}
  Object getContext(){return this;}
  UPDATE
  static void check(boolean condition){if(!condition)throw new AssertionError("Recycled dialog badge");}
  public static void main(String[] args){
    PrivacyCheck cell=new PrivacyCheck();cell.user=new TLRPC.User();cell.user.badged=true;
    cell.updateCommunityBadge();Drawable founder=cell.communityBadge;
    check(founder!=null&&founder.kind==1&&founder.callback==cell);
    cell.updateCommunityBadge();check(cell.communityBadge==founder);
    cell.user=new TLRPC.User();cell.updateCommunityBadge();
    check(cell.communityBadge==null&&founder.callback==null);
    cell.chat=new TLRPC.Chat();cell.chat.badged=true;cell.updateCommunityBadge();
    check(cell.communityBadge.kind==2);
    for(int mode=0;mode<5;mode++){
      Drawable old=cell.communityBadge;
      cell.customDialog=mode==0?new Object():null;cell.folder=mode==1;cell.forum=mode==2;
      cell.dialogFolder=mode==3;cell.isTopic=mode==4;
      cell.updateCommunityBadge();check(cell.communityBadge==null&&old.callback==null);
      cell.customDialog=null;cell.folder=cell.forum=cell.dialogFolder=cell.isTopic=false;
      cell.updateCommunityBadge();check(cell.communityBadge.kind==2);
    }
    cell.chat=null;cell.user.badged=true;cell.user.self=true;cell.updateCommunityBadge();
    check(cell.communityBadge==null);
  }
}
class TLRPC {static class User{boolean badged,self;}static class Chat{boolean badged;}}
class UserObject{static boolean isUserSelf(TLRPC.User user){return user!=null&&user.self;}}
class Drawable{int kind;Object callback;Drawable(int kind){this.kind=kind;}void setCallback(Object c){callback=c;}}
class FreezgramBadges{
 static boolean hasBadge(TLRPC.User user){return user!=null&&user.badged;}
 static boolean hasChannelBadge(TLRPC.Chat chat){return chat!=null&&chat.badged;}
 static Drawable getDrawable(Object c){return new Drawable(1);}
 static Drawable getChannelDrawable(Object c){return new Drawable(2);}
}
'''.replace('UPDATE',update))


if __name__=='__main__':
    unittest.main()
