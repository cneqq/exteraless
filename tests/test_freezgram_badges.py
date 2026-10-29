"""Community badge eligibility tests with synthetic users and no Telegram session."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

MAIN = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main'


class FreezgramBadgeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('java'), 'Java source launcher required')
    def test_actual_registry_and_info_do_not_change_telegram_flags(self):
        source = (MAIN / 'java/app/freezgram/badges/FreezgramBadges.java').read_text()
        source = source[source.index('public final class FreezgramBadges'):].replace(
            'public final class FreezgramBadges', 'final class FreezgramBadges', 1)
        harness = '''
class BadgeCheck {
 static void check(boolean value){if(!value)throw new AssertionError("Badge invariant");}
 public static void main(String[] args){
  check(!FreezgramBadges.hasBadge(null));
  for(long id:new long[]{0,-966442694L,1,966442693L,966442695L,Long.MAX_VALUE}){
   TLRPC.User other=new TLRPC.User();other.id=id;check(!FreezgramBadges.hasBadge(other));
  }
  TLRPC.User owner=new TLRPC.User();owner.id=966442694L;
  check(FreezgramBadges.hasBadge(owner));
  check(!owner.verified&&!owner.scam&&!owner.fake);
  owner.verified=true;check(!FreezgramBadges.hasBadge(owner));check(owner.verified);
  owner.verified=false;owner.scam=true;check(!FreezgramBadges.hasBadge(owner));check(owner.scam);
  owner.scam=false;owner.fake=true;check(!FreezgramBadges.hasBadge(owner));check(owner.fake);
  FreezgramBadges.showInfo(null);check(BulletinFactory.shown==0);
  FreezgramBadges.showInfo(new BaseFragment(null));check(BulletinFactory.shown==0);
  FreezgramBadges.showInfo(new BaseFragment(new Context()));check(BulletinFactory.shown==1);
  check("Founder".equals(BulletinFactory.title)&&"Local community".equals(BulletinFactory.info));
  check(ContextCompat.lastResource==R.drawable.freezgram_community_badge);
  TLRPC.TL_channel channel=new TLRPC.TL_channel();
  channel.id=-(-1004480543290L)-1000000000000L;
  check(FreezgramBadges.hasChannelBadge(channel));
  check(!FreezgramBadges.hasChannelBadge(null));
  TLRPC.Chat group=new TLRPC.Chat();group.id=channel.id;
  check(!FreezgramBadges.hasChannelBadge(group));
  TLRPC.User channelIdUser=new TLRPC.User();channelIdUser.id=channel.id;
  check(!FreezgramBadges.hasBadge(channelIdUser));
  for(long id:new long[]{-1004480543290L,-4480543290L,4480543289L,4480543291L,966442694L}){
   channel.id=id;check(!FreezgramBadges.hasChannelBadge(channel));
  }
  channel.id=4480543290L;
  channel.megagroup=true;check(!FreezgramBadges.hasChannelBadge(channel));channel.megagroup=false;
  channel.verified=true;check(!FreezgramBadges.hasChannelBadge(channel));check(channel.verified);channel.verified=false;
  channel.scam=true;check(!FreezgramBadges.hasChannelBadge(channel));check(channel.scam);channel.scam=false;
  channel.fake=true;check(!FreezgramBadges.hasChannelBadge(channel));check(channel.fake);channel.fake=false;
  FreezgramBadges.showChannelInfo(null);
  FreezgramBadges.showChannelInfo(new BaseFragment(null));check(BulletinFactory.shown==1);
  FreezgramBadges.showChannelInfo(new BaseFragment(new Context()));check(BulletinFactory.shown==2);
  check("Official channel".equals(BulletinFactory.title)&&"Local community".equals(BulletinFactory.info));
  check(ContextCompat.lastResource==R.drawable.freezgram_channel_badge);
 }
}
class TLRPC {
 static class User {long id;boolean verified,scam,fake;}
 static class Chat {long id;boolean verified,scam,fake,megagroup;}
 static class TL_channel extends Chat {}
}
class ChatObject {static boolean isChannel(TLRPC.Chat chat){return chat instanceof TLRPC.TL_channel;}}
class Context {}
class Drawable {Drawable mutate(){return this;}}
class FreezgramBadgeDrawable extends Drawable {FreezgramBadgeDrawable(Drawable seal,Drawable plane){}}
class ContextCompat {static int lastResource;static Drawable getDrawable(Context c,int id){lastResource=id;return new Drawable();}}
class R {
 static class drawable {static int freezgram_community_badge=1,freezgram_channel_badge=4,freezgram_settings_icon=6;}
 static class string {static int FreezgramBadgeFounder=2,FreezgramBadgeLocalInfo=3,FreezgramBadgeOfficialChannel=5;}
}
class LocaleController {static String getString(int id){return id==2?"Founder":id==5?"Official channel":"Local community";}}
class BaseFragment {Context c;BaseFragment(Context c){this.c=c;}Context getContext(){return c;}}
class BulletinFactory {
 static int shown;static String title,info;
 static BulletinFactory of(BaseFragment f){return new BulletinFactory();}
 BulletinFactory createSimpleBulletin(Drawable d,String a,String b){title=a;info=b;return this;}
 void show(){shown++;}
}
'''
        with tempfile.TemporaryDirectory(prefix='freezgram-badges-') as directory:
            path = Path(directory) / 'BadgeCheck.java'
            path.write_text(harness + source)
            result = subprocess.run(['java', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr[:2000])



if __name__ == '__main__':
    unittest.main()
