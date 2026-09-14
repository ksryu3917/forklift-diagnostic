package com.ryu.forkliftdiagnostic;

import android.app.*;
import android.content.*;
import android.graphics.*;
import android.graphics.drawable.ColorDrawable;
import android.view.*;
import android.widget.*;

/** Full-screen image viewer for OEM sheets and re-authored diagrams.
 *  Pinch zoom, drag, double-tap zoom/reset. No external dependency.
 */
public final class ZoomImageDialog {
    private ZoomImageDialog() {}

    public static void show(Activity activity, Bitmap bitmap) {
        if (activity == null || bitmap == null) return;
        final Dialog dialog = new Dialog(activity, android.R.style.Theme_Black_NoTitleBar_Fullscreen);
        LinearLayout root = new LinearLayout(activity);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.BLACK);

        LinearLayout bar = new LinearLayout(activity);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setPadding(dp(activity, 10), dp(activity, 4), dp(activity, 8), dp(activity, 4));
        TextView hint = new TextView(activity);
        hint.setText("두 손가락 확대 · 드래그 이동 · 더블탭 확대/원위치");
        hint.setTextColor(Color.WHITE);
        hint.setTextSize(13);
        bar.addView(hint, new LinearLayout.LayoutParams(0, dp(activity, 48), 1));
        Button close = new Button(activity);
        close.setText("닫기");
        close.setAllCaps(false);
        close.setTextColor(Color.WHITE);
        close.setBackgroundColor(Color.TRANSPARENT);
        close.setOnClickListener(v -> dialog.dismiss());
        bar.addView(close, new LinearLayout.LayoutParams(dp(activity, 72), dp(activity, 48)));
        root.addView(bar);

        ZoomImageView view = new ZoomImageView(activity);
        view.setBackgroundColor(Color.BLACK);
        view.setImageBitmap(bitmap);
        root.addView(view, new LinearLayout.LayoutParams(-1, 0, 1));
        dialog.setContentView(root);
        dialog.show();
        Window w = dialog.getWindow();
        if (w != null) {
            w.setBackgroundDrawable(new ColorDrawable(Color.BLACK));
            w.setLayout(-1, -1);
        }
    }

    private static int dp(Context c, int n) {
        return (int)(n * c.getResources().getDisplayMetrics().density + 0.5f);
    }

    private static final class ZoomImageView extends ImageView implements View.OnTouchListener {
        private final Matrix matrix = new Matrix();
        private final ScaleGestureDetector scaleDetector;
        private final GestureDetector gestureDetector;
        private float minScale = 1f;
        private float currentScale = 1f;
        private float lastX, lastY;
        private boolean dragging;
        private boolean fitted;

        ZoomImageView(Context context) {
            super(context);
            setScaleType(ScaleType.MATRIX);
            setOnTouchListener(this);
            scaleDetector = new ScaleGestureDetector(context, new ScaleGestureDetector.SimpleOnScaleGestureListener() {
                @Override public boolean onScale(ScaleGestureDetector detector) {
                    float factor = detector.getScaleFactor();
                    float target = currentScale * factor;
                    if (target < minScale) factor = minScale / currentScale;
                    if (target > 6f) factor = 6f / currentScale;
                    currentScale *= factor;
                    matrix.postScale(factor, factor, detector.getFocusX(), detector.getFocusY());
                    constrain();
                    setImageMatrix(matrix);
                    return true;
                }
            });
            gestureDetector = new GestureDetector(context, new GestureDetector.SimpleOnGestureListener() {
                @Override public boolean onDoubleTap(MotionEvent e) {
                    if (currentScale > minScale * 1.15f) {
                        fitToView();
                    } else {
                        float factor = Math.min(2.5f, 6f/currentScale);
                        currentScale *= factor;
                        matrix.postScale(factor, factor, e.getX(), e.getY());
                        constrain();
                        setImageMatrix(matrix);
                    }
                    return true;
                }
            });
        }

        @Override protected void onSizeChanged(int w, int h, int oldw, int oldh) {
            super.onSizeChanged(w, h, oldw, oldh);
            fitted = false;
            post(this::fitToView);
        }

        private void fitToView() {
            if (getDrawable() == null || getWidth() <= 0 || getHeight() <= 0) return;
            int dw = getDrawable().getIntrinsicWidth();
            int dh = getDrawable().getIntrinsicHeight();
            if (dw <= 0 || dh <= 0) return;
            float sx = (float)getWidth() / dw;
            float sy = (float)getHeight() / dh;
            minScale = Math.min(sx, sy);
            if (minScale <= 0f) minScale = 1f;
            currentScale = minScale;
            float tx = (getWidth() - dw * minScale) / 2f;
            float ty = (getHeight() - dh * minScale) / 2f;
            matrix.reset();
            matrix.postScale(minScale, minScale);
            matrix.postTranslate(tx, ty);
            setImageMatrix(matrix);
            fitted = true;
        }

        private void constrain() {
            if (getDrawable() == null) return;
            RectF rect = new RectF(0, 0, getDrawable().getIntrinsicWidth(), getDrawable().getIntrinsicHeight());
            matrix.mapRect(rect);
            float dx = 0, dy = 0;
            if (rect.width() <= getWidth()) dx = getWidth()/2f - rect.centerX();
            else if (rect.left > 0) dx = -rect.left;
            else if (rect.right < getWidth()) dx = getWidth() - rect.right;
            if (rect.height() <= getHeight()) dy = getHeight()/2f - rect.centerY();
            else if (rect.top > 0) dy = -rect.top;
            else if (rect.bottom < getHeight()) dy = getHeight() - rect.bottom;
            matrix.postTranslate(dx, dy);
        }

        @Override public boolean onTouch(View v, MotionEvent e) {
            if (!fitted) fitToView();
            gestureDetector.onTouchEvent(e);
            scaleDetector.onTouchEvent(e);
            if (scaleDetector.isInProgress()) return true;
            switch (e.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    lastX = e.getX(); lastY = e.getY(); dragging = true; return true;
                case MotionEvent.ACTION_MOVE:
                    if (dragging && currentScale > minScale * 1.01f) {
                        float dx = e.getX() - lastX, dy = e.getY() - lastY;
                        matrix.postTranslate(dx, dy);
                        constrain();
                        setImageMatrix(matrix);
                    }
                    lastX = e.getX(); lastY = e.getY(); return true;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    dragging = false; return true;
            }
            return true;
        }
    }
}
