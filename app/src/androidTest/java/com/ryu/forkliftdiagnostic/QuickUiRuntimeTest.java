package com.ryu.forkliftdiagnostic;

import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.click;
import static androidx.test.espresso.action.ViewActions.scrollTo;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.matcher.ViewMatchers.isDisplayed;
import static androidx.test.espresso.matcher.ViewMatchers.withContentDescription;
import static androidx.test.espresso.matcher.ViewMatchers.withText;
import static org.hamcrest.Matchers.containsString;
import static org.junit.Assert.*;

import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Environment;

import androidx.test.core.app.ActivityScenario;
import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.UiObject;
import androidx.test.uiautomator.UiSelector;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.File;

@RunWith(AndroidJUnit4.class)
public class QuickUiRuntimeTest {
    private UiDevice device;
    private Context target;
    private File shots;
    private ActivityScenario<?> scenario;

    @Before public void setUp() throws Exception {
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        target = ApplicationProvider.getApplicationContext();

        device.wakeUp();
        device.executeShellCommand("wm dismiss-keyguard");
        device.pressHome();

        target.getSharedPreferences("field_measurements_v1", Context.MODE_PRIVATE).edit().clear().commit();
        target.getSharedPreferences("field_measurement_session", Context.MODE_PRIVATE).edit().clear().commit();

        shots = new File(target.getExternalFilesDir(Environment.DIRECTORY_PICTURES), "v893-runtime");
        assertTrue(shots.exists() || shots.mkdirs());
        device.executeShellCommand("rm -rf /sdcard/Download/v893-runtime");
        device.executeShellCommand("mkdir -p /sdcard/Download/v893-runtime");
    }

    @After public void tearDown() throws Exception {
        if (scenario != null) scenario.close();
    }

    private void startLicenseQuick() {
        Intent i = new Intent(target, TestPointLocatorActivity.class);
        i.putExtra("group_id", "EL_LICENSE");
        scenario = ActivityScenario.launch(i);
        onView(withContentDescription("testpoint-group:EL_LICENSE")).check(matches(isDisplayed()));
        onView(withContentDescription("quick-point:LP1"))
                .check(matches(withText(containsString("다른 미등/후미등 정상 여부"))));
    }

    private void startLicenseCircuit() {
        Intent i = new Intent(target, ElectricalDiagnosticActivity.class);
        i.putExtra("graph_id", "E_LICENSE_NO");
        scenario = ActivityScenario.launch(i);
        onView(withContentDescription("electrical-graph:E_LICENSE_NO")).check(matches(isDisplayed()));
    }

    private void shot(String name) throws Exception {
        File f = new File(shots, name + ".png");
        assertTrue("screenshot failed: " + f, device.takeScreenshot(f));
        assertTrue("empty screenshot: " + f, f.length() > 1000);
        device.executeShellCommand("cp " + f.getAbsolutePath()
                + " /sdcard/Download/v893-runtime/" + name + ".png");
    }

    private void dumpHierarchy(String name) {
        try {
            File f = new File(shots, name + ".xml");
            device.dumpWindowHierarchy(f);
            device.executeShellCommand("cp " + f.getAbsolutePath()
                    + " /sdcard/Download/v893-runtime/" + name + ".xml");
        } catch (Exception ignore) {}
    }

    @Test public void licenseLocalBranchShowsExactlyOnePointAtATime() throws Exception {
        try {
            startLicenseQuick();
            shot("01-license-initial-LP1");

            onView(withContentDescription("quick-pass:LP1")).perform(click());
            onView(withContentDescription("quick-point:LP2"))
                    .check(matches(withText(containsString("번호판등 +전원"))));
            shot("02-license-LP2-power");

            onView(withContentDescription("quick-pass:LP2")).perform(click());
            onView(withContentDescription("quick-point:LP3"))
                    .check(matches(withText(containsString("번호판등 접지 전압강하"))));
            shot("03-license-LP3-ground-drop");

            onView(withContentDescription("quick-pass:LP3")).perform(click());
            onView(withText(containsString("전구/소켓 접촉 영역"))).check(matches(isDisplayed()));
            assertNoActiveQuickPoint();
            shot("04-license-bulb-socket-stop");
        } catch (Throwable t) {
            dumpHierarchy("FAIL-license-local");
            shotBestEffort("FAIL-license-local");
            throw t;
        }
    }

    @Test public void licenseCommonFailureMovesOnlyToLampPath() throws Exception {
        try {
            startLicenseQuick();
            onView(withContentDescription("quick-fail:LP1")).perform(click());
            onView(withContentDescription("quick-point:LP4"))
                    .check(matches(withText(containsString("LAMP"))));
            shot("05-license-common-LAMP");
        } catch (Throwable t) {
            dumpHierarchy("FAIL-license-common");
            shotBestEffort("FAIL-license-common");
            throw t;
        }
    }

    @Test public void circuitViewerPinchAndDragChangesRenderedImage() throws Exception {
        try {
            startLicenseCircuit();
            onView(withContentDescription("circuit-evidence:E_LICENSE_NO")).perform(scrollTo(), click());
            onView(withContentDescription("circuit-image:E_LICENSE_NO")).perform(scrollTo(), click());
            onView(withContentDescription("zoom-image")).check(matches(isDisplayed()));
            shot("06-zoom-before");

            UiObject zoom = device.findObject(new UiSelector().description("zoom-image"));
            assertTrue("zoom image missing in real window", zoom.waitForExists(5000));
            assertTrue("pinch out failed", zoom.pinchOut(75, 24));
            device.waitForIdle();
            shot("07-zoom-after-pinch");
            assertImagesDiffer("06-zoom-before.png", "07-zoom-after-pinch.png");

            android.graphics.Rect b = zoom.getBounds();
            device.swipe(b.centerX(), b.centerY(),
                    b.centerX()+Math.max(50,b.width()/5), b.centerY(), 18);
            device.waitForIdle();
            shot("08-zoom-after-drag");
            assertImagesDiffer("07-zoom-after-pinch.png", "08-zoom-after-drag.png");
        } catch (Throwable t) {
            dumpHierarchy("FAIL-zoom");
            shotBestEffort("FAIL-zoom");
            throw t;
        }
    }

    private void assertNoActiveQuickPoint() {
        for (String pid : new String[]{"LP1","LP2","LP3","LP4"}) {
            assertFalse("unexpected active quick point: " + pid,
                    device.findObject(new UiSelector().description("quick-point:"+pid)).exists());
        }
    }

    private void shotBestEffort(String name) {
        try { shot(name); } catch (Throwable ignore) {}
    }

    private void assertImagesDiffer(String a, String b) {
        Bitmap x=BitmapFactory.decodeFile(new File(shots,a).getAbsolutePath());
        Bitmap y=BitmapFactory.decodeFile(new File(shots,b).getAbsolutePath());
        assertNotNull(x); assertNotNull(y);
        int changed=0, sampled=0;
        int w=Math.min(x.getWidth(),y.getWidth()), h=Math.min(x.getHeight(),y.getHeight());
        for(int py=h/5;py<h;py+=8) for(int px=0;px<w;px+=8){
            sampled++;
            if(x.getPixel(px,py)!=y.getPixel(px,py))changed++;
        }
        assertTrue("rendered image did not change enough: "+changed+"/"+sampled,
                changed>Math.max(30,sampled/200));
    }
}
