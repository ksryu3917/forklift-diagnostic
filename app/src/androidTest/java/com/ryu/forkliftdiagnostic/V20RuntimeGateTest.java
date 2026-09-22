package com.ryu.forkliftdiagnostic;
import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.click;
import static androidx.test.espresso.action.ViewActions.scrollTo;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.matcher.ViewMatchers.*;
import android.content.Context;import android.content.Intent;import android.os.Environment;
import androidx.test.core.app.ActivityScenario;import androidx.test.core.app.ApplicationProvider;import androidx.test.ext.junit.runners.AndroidJUnit4;import androidx.test.platform.app.InstrumentationRegistry;import androidx.test.uiautomator.*;
import com.ryu.forkliftdiagnostic.ui.*;import org.junit.*;import org.junit.runner.RunWith;import java.io.File;
@RunWith(AndroidJUnit4.class) public class V20RuntimeGateTest {
 private UiDevice device;private Context target;private ActivityScenario<?> scenario;private File dir;
 @Before public void setup()throws Exception{device=UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());target=ApplicationProvider.getApplicationContext();device.wakeUp();device.executeShellCommand("wm dismiss-keyguard");dir=new File(target.getExternalFilesDir(Environment.DIRECTORY_PICTURES),"v20-runtime");if(!dir.exists())Assert.assertTrue(dir.mkdirs());device.executeShellCommand("mkdir -p /sdcard/Download/v20-runtime");}
 @After public void close(){if(scenario!=null)scenario.close();}
 private void shot(String name)throws Exception{File p=new File(dir,name+".png");Assert.assertTrue(device.takeScreenshot(p));device.executeShellCommand("cp "+p.getAbsolutePath()+" /sdcard/Download/v20-runtime/"+name+".png");File x=new File(dir,name+".xml");device.dumpWindowHierarchy(x);device.executeShellCommand("cp "+x.getAbsolutePath()+" /sdcard/Download/v20-runtime/"+name+".xml");}
 private double renderedDifference(String left,String right,android.graphics.Rect area)throws Exception{
  android.graphics.Bitmap a=android.graphics.BitmapFactory.decodeFile(new File(dir,left+".png").getAbsolutePath());
  android.graphics.Bitmap b=android.graphics.BitmapFactory.decodeFile(new File(dir,right+".png").getAbsolutePath());
  Assert.assertNotNull(a);Assert.assertNotNull(b);Assert.assertEquals(a.getWidth(),b.getWidth());Assert.assertEquals(a.getHeight(),b.getHeight());
  long changed=0,total=0;
  for(int y=Math.max(0,area.top+8);y<Math.min(a.getHeight(),area.bottom-8);y+=2)
   for(int x=Math.max(0,area.left+8);x<Math.min(a.getWidth(),area.right-8);x+=2){
    int u=a.getPixel(x,y),v=b.getPixel(x,y);
    int delta=Math.abs(android.graphics.Color.red(u)-android.graphics.Color.red(v))+Math.abs(android.graphics.Color.green(u)-android.graphics.Color.green(v))+Math.abs(android.graphics.Color.blue(u)-android.graphics.Color.blue(v));
    if(delta>24)changed++;total++;
   }
  a.recycle();b.recycle();Assert.assertTrue("No visible image pixels",total>0);return (double)changed/total;
 }
 private void graph(String file){Intent i=new Intent(target,DiagnosticRunnerActivity.class);i.putExtra("graph",file);scenario=ActivityScenario.launch(i);}
 private void choose(String id){onView(isAssignableFrom(android.widget.CheckBox.class)).perform(scrollTo(),click());onView(withContentDescription("choice_"+id)).perform(scrollTo(),click());}
 @Test public void allSixteenScreensAndGestures()throws Exception{
  target.getSharedPreferences("vehicle",0).edit().clear().putString("manufacturer","DOOSAN").putString("model","D25S-7").putString("engine","D24").commit();
  try {
  graph("e_license_terminal_stop.json");onView(withText(org.hamcrest.Matchers.containsString("LP1"))).check(matches(isDisplayed()));shot("01-license-LP1");choose("normal");shot("02-license-LP2-power");choose("present");shot("03-license-LP3-ground-drop");choose("normal");onView(withContentDescription("terminal_stop")).perform(scrollTo()).check(matches(isDisplayed()));shot("04-license-bulb-socket-stop");scenario.close();graph("e_license_terminal_stop.json");choose("abnormal");shot("05-license-common-LAMP");scenario.close();
  scenario=ActivityScenario.launch(new Intent(target,EvidenceViewerActivity.class));UiObject zoom=device.findObject(new UiSelector().description("zoom_pan_canvas"));Assert.assertTrue(zoom.waitForExists(5000));android.graphics.Rect imageArea=zoom.getVisibleBounds();shot("06-zoom-before");Assert.assertTrue(zoom.pinchOut(75,24));device.waitForIdle();shot("07-zoom-after-pinch");Assert.assertTrue("Pinch did not change rendered OEM image",renderedDifference("06-zoom-before","07-zoom-after-pinch",imageArea)>0.005);android.graphics.Rect b=zoom.getBounds();device.swipe(b.centerX(),b.centerY(),b.centerX()+120,b.centerY()+60,18);device.waitForIdle();shot("08-zoom-after-drag");Assert.assertTrue("Pan did not change rendered OEM image",renderedDifference("07-zoom-after-pinch","08-zoom-after-drag",imageArea)>0.005);
  device.click(imageArea.centerX(),imageArea.centerY());device.click(imageArea.centerX(),imageArea.centerY());device.waitForIdle();shot("08b-zoom-double-tap-reset");Assert.assertTrue("Double tap did not restore original framing",renderedDifference("06-zoom-before","08b-zoom-double-tap-reset",imageArea)<0.005);scenario.close();
  scenario=ActivityScenario.launch(new Intent(target,VehicleSelectActivity.class));shot("09-manufacturer-model-select");scenario.close();scenario=ActivityScenario.launch(new Intent(target,StudyActivity.class));shot("10-study-home");onView(withContentDescription("study_scope_stop")).perform(scrollTo()).check(matches(isDisplayed()));shot("11-study-exact-model-stop");scenario.close();
  graph("ev_reach_no_travel_mech.json");choose("yes");shot("12-reach-motor-turns-first-check");choose("rotates");choose("shock");shot("13-lift-brake-release-hand-turn");choose("periodic");choose("inside");choose("metal");shot("14-reducer-axle-isolation-result");scenario.close();graph("ev_battery_short_runtime.json");choose("yes");shot("15-battery-pack-va-cell-gravity");scenario.close();scenario=ActivityScenario.launch(new Intent(target,MainActivity.class));onView(withText(org.hamcrest.Matchers.containsString("v20"))).check(matches(isDisplayed()));shot("16-release-identity");
  } catch(Throwable failure) { try {shot("failure-current-screen");}catch(Exception capture){failure.addSuppressed(capture);}if(failure instanceof Exception)throw (Exception)failure;throw (Error)failure;}
 }
}
