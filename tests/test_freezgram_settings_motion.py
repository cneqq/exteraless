"""Check settings transition cleanup and centered search placeholder policy."""
import shutil
import unittest
from pathlib import Path
from test_personal_privacy import method,run_java
JAVA=Path(__file__).resolve().parents[1]/'TMessagesProj/src/main/java'

@unittest.skipUnless(shutil.which('java'),'Java source launcher required')
class SettingsMotionTests(unittest.TestCase):
    def test_transition_restores_properties_and_completes_once_on_cancel_or_end(self):
        transition=method((JAVA/'app/freezgram/SettingsMotion.java').read_text(),'    public static AnimatorSet transition(')
        run_java('''
class PrivacyCheck{
 static boolean appliesTo(BaseFragment f){return f.applicable;}
 TRANSITION
 public static void main(String[] args){
  for(boolean open:new boolean[]{false,true})for(boolean cancel:new boolean[]{false,true}){
   var f=new BaseFragment();var calls=new int[1];var a=transition(f,open,()->calls[0]++);
   if(a==null||!a.started||a.duration!=(open?320:280)||calls[0]!=0)throw new AssertionError("Transition lifecycle");
   if(cancel)a.listener.onAnimationCancel(a);a.listener.onAnimationEnd(a);a.listener.onAnimationEnd(a);
   if(calls[0]!=1||f.container.alpha!=1||f.container.x!=0)throw new AssertionError("Stuck/duplicate transition completion");
  }
  for(boolean app:new boolean[]{false,true})for(boolean system:new boolean[]{false,true})for(boolean local:new boolean[]{false,true}){
   SharedConfig.enabled=app;ValueAnimator.enabled=system;var f=new BaseFragment();f.applicable=local;
   if((transition(f,true,()->{})!=null)!=(app&&system&&local))throw new AssertionError("Animation opt-out ignored");
  }
 }
}
class BaseFragment{boolean applicable=true;View container=new View(),content=new View();BaseFragment(){content.parent=container;}View getFragmentView(){return content;}}
class View{static Object ALPHA=new Object(),TRANSLATION_X=new Object();Object parent;float alpha=1,x;Object getParent(){return parent;}void setAlpha(float a){alpha=a;}void setTranslationX(float v){x=v;}}
class Animator{}
class AnimatorListenerAdapter{public void onAnimationCancel(Animator a){}public void onAnimationEnd(Animator a){}}
class AnimatorSet extends Animator{boolean started;long duration;AnimatorListenerAdapter listener;void playTogether(Object... a){}void setDuration(long d){duration=d;}void setInterpolator(Object i){}void addListener(AnimatorListenerAdapter l){listener=l;}void start(){started=true;}}
class ObjectAnimator{static Object ofFloat(View v,Object p,float... f){return new Object();}}
class ValueAnimator{static boolean enabled=true;static boolean areAnimatorsEnabled(){return enabled;}}
class Build{static class VERSION{static int SDK_INT=36;}}
class SharedConfig{static boolean enabled=true;static boolean animationsEnabled(){return enabled;}}
class AndroidUtilities{static int dp(int n){return n;}}
class CubicBezierInterpolator{static Object EASE_BOTH=new Object();}
'''.replace('TRANSITION',transition))

    def test_only_idle_empty_search_centers_without_moving_typed_text_or_filters(self):
        gravity=method((JAVA/'org/telegram/ui/Components/FragmentSearchField.java').read_text(),'    private void updatePlaceholderGravity()')
        run_java('''
class PrivacyCheck{
 boolean centeredPlaceholder;EditText editText=new EditText();java.util.ArrayList<Object> currentSearchFilters=new java.util.ArrayList<>();
 GRAVITY
 public static void main(String[] args){
  for(int flags=0;flags<32;flags++){
   var p=new PrivacyCheck();p.centeredPlaceholder=(flags&1)!=0;p.editText.length=(flags&2)!=0?1:0;p.editText.focus=(flags&4)!=0;
   if((flags&8)!=0)p.currentSearchFilters.add(new Object());LocaleController.isRTL=(flags&16)!=0;
   p.updatePlaceholderGravity();boolean center=(flags&15)==1;
   int expected=Gravity.CENTER_VERTICAL|(center?Gravity.CENTER_HORIZONTAL:LocaleController.isRTL?Gravity.RIGHT:Gravity.LEFT);
   if(p.editText.gravity!=expected)throw new AssertionError("Typing/filter alignment changed");
  }
 }
}
class EditText{int length,gravity;boolean focus;int length(){return length;}boolean hasFocus(){return focus;}void setGravity(int n){gravity=n;}}
class LocaleController{static boolean isRTL;}
class Gravity{static int CENTER_VERTICAL=16,CENTER_HORIZONTAL=1,RIGHT=5,LEFT=3;}
'''.replace('GRAVITY',gravity))
