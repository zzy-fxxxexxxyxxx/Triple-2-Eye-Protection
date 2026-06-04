package com.triple2.eyeprotection;

import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.view.MotionEvent;
import android.widget.Button;

final class UiFeedback {
    private UiFeedback() {
    }

    static void applyButtonFeedback(Button button, int normalColor, int cornerRadiusPx) {
        int pressedColor = blend(normalColor, Color.BLACK, 0.18f);
        int focusedColor = blend(normalColor, Color.WHITE, 0.10f);
        int disabledColor = Color.rgb(174, 190, 181);

        StateListDrawable background = new StateListDrawable();
        background.addState(new int[]{-android.R.attr.state_enabled}, rounded(disabledColor, cornerRadiusPx));
        background.addState(new int[]{android.R.attr.state_pressed}, rounded(pressedColor, cornerRadiusPx));
        background.addState(new int[]{android.R.attr.state_focused}, rounded(focusedColor, cornerRadiusPx));
        background.addState(new int[]{}, rounded(normalColor, cornerRadiusPx));
        button.setBackground(background);

        button.setTextColor(new ColorStateList(
                new int[][]{
                        new int[]{-android.R.attr.state_enabled},
                        new int[]{}
                },
                new int[]{
                        Color.rgb(235, 242, 238),
                        Color.WHITE
                }
        ));
        button.setHapticFeedbackEnabled(false);
        button.setOnTouchListener((view, event) -> {
            if (!view.isEnabled()) {
                return false;
            }
            int action = event.getActionMasked();
            if (action == MotionEvent.ACTION_DOWN) {
                view.animate()
                        .scaleX(0.975f)
                        .scaleY(0.975f)
                        .alpha(0.92f)
                        .setDuration(55L)
                        .start();
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                view.animate()
                        .scaleX(1f)
                        .scaleY(1f)
                        .alpha(1f)
                        .setDuration(110L)
                        .start();
            }
            return false;
        });
    }

    private static GradientDrawable rounded(int color, int cornerRadiusPx) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color);
        drawable.setCornerRadius(cornerRadiusPx);
        return drawable;
    }

    private static int blend(int from, int to, float amount) {
        float inverse = 1f - amount;
        int alpha = Math.round(Color.alpha(from) * inverse + Color.alpha(to) * amount);
        int red = Math.round(Color.red(from) * inverse + Color.red(to) * amount);
        int green = Math.round(Color.green(from) * inverse + Color.green(to) * amount);
        int blue = Math.round(Color.blue(from) * inverse + Color.blue(to) * amount);
        return Color.argb(alpha, red, green, blue);
    }
}
