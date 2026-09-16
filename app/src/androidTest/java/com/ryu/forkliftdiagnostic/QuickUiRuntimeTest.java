package com.ryu.forkliftdiagnostic;

import static org.junit.Assert.*;

import android.app.Instrumentation;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Environment;

import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.uiautomator.By;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.UiObject;
import androidx.test.uiautomator.UiSelector;
import androidx.test.uiautomator.Until;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.File;

@RunWith(AndroidJUnit4.class)
public class QuickUiRuntimeTest {
    private Instrumentation instrumentation;
    private UiDevice device;
    private Context target;
    private File shots;

    @Before public void setUp() throws Exception {
        instrumentation = InstrumentationRegistry.getInstrumentation();
        device = UiDevice.getInstance(instrumentation);
        target = instrumentation.getTargetContext();
        target.getSharedPreferences("field_measurements_v1", Context.MODE_PRIVATE).edit().clear().commit();
        target.getSharedPreferences("field_measurement_session", Context.MODE_PRIVATE).edit().clear().commit();
        shots = new File(target.getExternalFilesDir(Environment.DIRECTORY_PICTURES), "v892-runtime");
        assertTrue(shots.exists() || shots.mkdirs());
        device.executeShellCommand("mkdir -p /sdcard/Download/v892-runtime");
    }

    private void startLicenseQuick() {
        Intent i = new Intent(target, TestPointLocatorActivity.class);
        i.putExtra("group_id", "EL_LICENSE");
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        target.startActivity(i);
        assertTrue(device.wait(Until.hasObject(By.textContains("다른 미등/후미등 정상 여부")), 30000));
    }

    private void startLicenseCircuit() {
        Intent i = new Intent(target, ElectricalDiagnosticActivity.class);
        i.putExtra("graph_id", "E_LICENSE_NO");
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        target.startActivity(i);
        assertTrue(device.wait(Until.hasObject(By.textContains("번호판등")), 30000));
    }

    private void shot(String name) throws Exception {
        File f = new File(shots, name + ".png");
        assertTrue("screenshot failed: " + f, device.takeScreenshot(f));
        assertTrue(f.length() > 1000);
        device.executeShellCommand("cp " + f.getAbsolutePath() + " /sdcard/Download/v892-runtime/" + name + ".png");
        String size = device.executeShellCommand("stat -c %s /sdcard/Download/v892-runtime/" + name + ".png").trim();
        assertTrue("public screenshot copy failed: " + name, Long.parseLong(size) > 1000);
    }

    private void tapExact(String text) {
        assertTrue("missing button: " + text, device.wait(Until.hasObject(By.text(text)), 15000));
        device.findObject(By.text(text)).click();
        device.waitForIdle();
    }

    private void assertHas(String text) {
        assertTrue("missing text: " + text, device.wait(Until.hasObject(By.textContains(text)), 15000));
    }

    private void assertNotHas(String text) {
        assertFalse("unexpected text: " + text, device.hasObject(By.textContains(text)));
    }

    private void assertNoActiveQuickPoint() {
        assertFalse("unexpected active quick-point PASS button", device.hasObject(By.text("정상")));
        assertFalse("unexpected active quick-point FAIL button", device.hasObject(By.text("이상")));
    }

    private void scrollToText(String text) {
        for (int n=0; n<10 && !device.hasObject(By.textContains(text)); n++) {
            device.swipe(device.getDisplayWidth()/2, device.getDisplayHeight()*3/4,
                    device.getDisplayWidth()/2, device.getDisplayHeight()/4, 18);
            device.waitForIdle();
        }
        assertHas(text);
    }

    @Test public void licenseLocalBranchShowsOnePointAtATime() throws Exception {
        startLicenseQuick();
        assertHas("다른 미등/후미등 정상 여부");
        assertNotHas("번호판등 +전원");
        assertNotHas("번호판등 접지 전압강하");
        assertNotHas("공통 LAMP 릴레이");
        shot("01-license-initial-one-question");

        tapExact("정상");
        assertHas("번호판등 +전원");
        assertNotHas("번호판등 접지 전압강하");
        assertNotHas("공통 LAMP 릴레이");
        shot("02-license-local-power");

        tapExact("정상");
        assertHas("번호판등 접지 전압강하");
        assertNotHas("공통 LAMP 릴레이");
        shot("03-license-ground-drop");

        tapExact("정상");
        assertHas("전구/소켓 접촉 영역");
        assertNoActiveQuickPoint();
        shot("04-license-bulb-socket-stop");
    }

    @Test public void licenseCommonFailureMovesToLampPath() throws Exception {
        startLicenseQuick();
        tapExact("이상");
        assertHas("공통 LAMP 릴레이 / 라이트 스위치");
        assertNotHas("번호판등 +전원");
        assertNotHas("번호판등 접지 전압강하");
        shot("05-license-common-lamp-path");
    }

    @Test public void circuitViewerPinchAndDragChangeRenderedImage() throws Exception {
        startLicenseCircuit();
        tapExact("회로 · 퓨즈/릴레이 · OEM 근거 보기");
        scrollToText("고장 전용 재작성 회로");
        UiObject image = device.findObject(new UiSelector().className("android.widget.ImageView"));
        for (int n=0; n<8 && !image.exists(); n++) {
            device.swipe(device.getDisplayWidth()/2, device.getDisplayHeight()*3/4,
                    device.getDisplayWidth()/2, device.getDisplayHeight()/4, 18);
            device.waitForIdle();
        }
        assertTrue("circuit image not visible", image.exists());
        image.click();
        assertHas("두 손가락 확대");
        shot("06-zoom-before");

        UiObject zoom = device.findObject(new UiSelector().className("android.widget.ImageView"));
        assertTrue("zoom image missing", zoom.exists());
        assertTrue("pinch out failed", zoom.pinchOut(75, 24));
        device.waitForIdle();
        shot("07-zoom-after-pinch");
        assertImagesDiffer("06-zoom-before.png", "07-zoom-after-pinch.png");

        android.graphics.Rect b = zoom.getBounds();
        device.swipe(b.centerX(), b.centerY(), b.centerX()+Math.max(40,b.width()/5), b.centerY(), 18);
        device.waitForIdle();
        shot("08-zoom-after-drag");
        assertImagesDiffer("07-zoom-after-pinch.png", "08-zoom-after-drag.png");

    }

    private void assertImagesDiffer(String a, String b) {
        Bitmap x=BitmapFactory.decodeFile(new File(shots,a).getAbsolutePath());
        Bitmap y=BitmapFactory.decodeFile(new File(shots,b).getAbsolutePath());
        assertNotNull(x); assertNotNull(y);
        int changed=0, sampled=0;
        int w=Math.min(x.getWidth(),y.getWidth()), h=Math.min(x.getHeight(),y.getHeight());
        for(int py=h/5;py<h;py+=8) for(int px=0;px<w;px+=8){sampled++;if(x.getPixel(px,py)!=y.getPixel(px,py))changed++;}
        assertTrue("rendered image did not change enough: "+changed+"/"+sampled, changed>Math.max(30,sampled/200));
    }
}
