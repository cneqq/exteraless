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
import java.util.function.Consumer;
class PrivacyCheck{
 TRANSITION
 public static void main(String[] args){
  for(boolean open:new boolean[]{false,true})for(boolean cancel:new boolean[]{false,true}){
   var v=new View();var calls=new int[1];var progress=new float[1];var a=transition(v,open,()->calls[0]++,x->progress[0]=x);
   if(a==null||!a.started||a.duration!=(open?320:280)||calls[0]!=0)throw new AssertionError("Transition lifecycle");
   a.frames.emit(.5f);
   if(progress[0]!=.5f||v.alpha!=.5f||v.x!=14)throw new AssertionError("Shared frame progress/geometry missing");
   if(cancel)a.listener.onAnimationCancel(a);a.listener.onAnimationEnd(a);a.listener.onAnimationEnd(a);
   if(calls[0]!=1||v.alpha!=1||v.x!=0)throw new AssertionError("Stuck/duplicate transition completion");
  }
  for(boolean app:new boolean[]{false,true})for(boolean system:new boolean[]{false,true})for(int style:new int[]{0,1}){
   SharedConfig.enabled=app;ValueAnimator.enabled=system;AppearanceConfig.style=style;var v=new View();
   if((transition(v,true,()->{},x->{})!=null)!=(app&&system&&style==1))throw new AssertionError("Animation opt-out ignored");
  }
 }
}
class BaseFragment{boolean applicable=true;View container=new View(),content=new View();BaseFragment(){content.parent=container;}View getFragmentView(){return content;}}
class View{static Object ALPHA=new Object(),TRANSLATION_X=new Object();Object parent;float alpha=1,x;Object getParent(){return parent;}void setAlpha(float a){alpha=a;}void setTranslationX(float v){x=v;}}
class Animator{}
class AnimatorListenerAdapter{public void onAnimationCancel(Animator a){}public void onAnimationEnd(Animator a){}}
class AnimatorSet extends Animator{boolean started;long duration;AnimatorListenerAdapter listener;ValueAnimator frames;void playTogether(ValueAnimator f){frames=f;}void setDuration(long d){duration=d;}void setInterpolator(Object i){}void addListener(AnimatorListenerAdapter l){listener=l;}void start(){started=true;}}
class ObjectAnimator{static Object ofFloat(View v,Object p,float... f){return new Object();}}
class ValueAnimator{
 interface Update{void onUpdate(ValueAnimator v);}Update listener;float value;
 static boolean enabled=true;static boolean areAnimatorsEnabled(){return enabled;}
 static ValueAnimator ofFloat(float... f){return new ValueAnimator();}
 void addUpdateListener(Update l){listener=l;}Object getAnimatedValue(){return value;}
 void emit(float x){value=x;listener.onUpdate(this);}
}
class AppearanceConfig{static int style=1;static int transitionStyle(){return style;}}
class Build{static class VERSION{static int SDK_INT=36;}}
class SharedConfig{static boolean enabled=true;static boolean animationsEnabled(){return enabled;}}
class AndroidUtilities{static int dp(int n){return n;}}
class CubicBezierInterpolator{static Object EASE_BOTH=new Object();}
'''.replace('TRANSITION',transition))

    def test_shared_route_preserves_native_preview_predictive_and_standard_fallback(self):
        source=(JAVA/'org/telegram/ui/ActionBar/ActionBarLayout.java').read_text()
        start=source.index('    private void startLayoutAnimation(')
        prefix=source[start:source.index('        if (first) {',start)]
        prefix=prefix.replace('app.freezgram.SettingsMotion','SettingsMotion')+'    }'
        dispatch=method(source,'    private void dispatchSharedTransitionProgress(')
        run_java('''
import java.util.function.Consumer;
class PrivacyCheck{
 boolean predictiveBackInProgress;Object containerView=new Object(),containerViewBack=new Object();
 AnimatorSet currentAnimation;Fragment newFragment=new Fragment(),oldFragment=new Fragment();float animationProgress;
 ROUTE
 DISPATCH
 void onAnimationEndCheck(boolean b){}
 public static void main(String[] args){
  for(boolean first:new boolean[]{false,true})for(boolean preview:new boolean[]{false,true})
  for(boolean predictive:new boolean[]{false,true})for(boolean opening:new boolean[]{false,true})for(boolean smooth:new boolean[]{false,true}){
   var p=new PrivacyCheck();p.predictiveBackInProgress=predictive;SettingsMotion.smooth=smooth;
   p.startLayoutAnimation(opening,first,preview);
   boolean expected=first&&!preview&&!predictive&&smooth;
   if((p.currentAnimation!=null)!=expected)throw new AssertionError("Native route overridden or shared route missing");
   if(expected){
    if(SettingsMotion.container!=(opening?p.containerView:p.containerViewBack))throw new AssertionError("Wrong closing/opening container");
    SettingsMotion.progress.accept(.4f);
    if(p.animationProgress!=.4f||p.newFragment.progress!=.4f||p.oldFragment.progress!=.4f||!p.newFragment.entering||p.oldFragment.entering)throw new AssertionError("Fragment progress lost");
   }
  }
 }
}
class Fragment{float progress;boolean entering;void onTransitionAnimationProgress(boolean e,float p){entering=e;progress=p;}}
class AnimatorSet{}
class SettingsMotion{
 static boolean smooth;static Object container;static Consumer<Float> progress;
 static AnimatorSet transition(Object c,boolean open,Runnable done,Consumer<Float> p){container=c;progress=p;return smooth?new AnimatorSet():null;}
}
'''.replace('ROUTE',prefix).replace('DISPATCH',dispatch))

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
