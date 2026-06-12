package com.triple2.eyeprotection;

import android.content.Context;
import android.content.SharedPreferences;

final class AppPrefs {
    static final String PREFS = "triple2_eye_prefs";

    static final String STATE_STOPPED = "stopped";
    static final String STATE_WORKING = "working";
    static final String STATE_PAUSED = "paused";
    static final String STATE_RESTING = "resting";
    static final String STATE_SCREEN_OFF = "screen_off";

    private static final String KEY_ENABLED = "enabled";
    private static final String KEY_WORK_MINUTES = "work_minutes";
    private static final String KEY_REST_SECONDS = "rest_seconds";
    private static final String KEY_FADE_SECONDS = "fade_seconds";
    private static final String KEY_STATE = "state";
    private static final String KEY_WORK_END_AT = "work_end_at";
    private static final String KEY_REST_END_AT = "rest_end_at";
    private static final String KEY_PAUSE_REMAINING_MS = "pause_remaining_ms";
    private static final String KEY_SCREEN_OFF_AT = "screen_off_at";

    private AppPrefs() {
    }

    static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    static boolean enabled(Context context) {
        return prefs(context).getBoolean(KEY_ENABLED, false);
    }

    static void setEnabled(Context context, boolean enabled) {
        prefs(context).edit().putBoolean(KEY_ENABLED, enabled).apply();
    }

    static int workMinutes(Context context) {
        return Math.max(1, prefs(context).getInt(KEY_WORK_MINUTES, 20));
    }

    static int restSeconds(Context context) {
        return Math.max(1, prefs(context).getInt(KEY_REST_SECONDS, 20));
    }

    static float fadeSeconds(Context context) {
        return clampFadeSeconds(prefs(context).getFloat(KEY_FADE_SECONDS, 1.2f));
    }

    static void setDurations(Context context, int workMinutes, int restSeconds, float fadeSeconds) {
        prefs(context).edit()
                .putInt(KEY_WORK_MINUTES, Math.max(1, workMinutes))
                .putInt(KEY_REST_SECONDS, Math.max(1, restSeconds))
                .putFloat(KEY_FADE_SECONDS, clampFadeSeconds(fadeSeconds))
                .apply();
    }

    private static float clampFadeSeconds(float fadeSeconds) {
        return Math.max(0f, Math.min(10f, fadeSeconds));
    }

    static String state(Context context) {
        return prefs(context).getString(KEY_STATE, STATE_STOPPED);
    }

    static void setState(Context context, String state) {
        prefs(context).edit().putString(KEY_STATE, state).apply();
    }

    static long workEndAt(Context context) {
        return prefs(context).getLong(KEY_WORK_END_AT, 0L);
    }

    static long restEndAt(Context context) {
        return prefs(context).getLong(KEY_REST_END_AT, 0L);
    }

    static long pauseRemainingMs(Context context) {
        return prefs(context).getLong(KEY_PAUSE_REMAINING_MS, 0L);
    }

    static long screenOffAt(Context context) {
        return prefs(context).getLong(KEY_SCREEN_OFF_AT, 0L);
    }

    static void startWorking(Context context, long now) {
        prefs(context).edit()
                .putBoolean(KEY_ENABLED, true)
                .putString(KEY_STATE, STATE_WORKING)
                .putLong(KEY_WORK_END_AT, now + workMinutes(context) * 60_000L)
                .putLong(KEY_REST_END_AT, 0L)
                .putLong(KEY_PAUSE_REMAINING_MS, 0L)
                .putLong(KEY_SCREEN_OFF_AT, 0L)
                .apply();
    }

    static void startResting(Context context, long now) {
        prefs(context).edit()
                .putBoolean(KEY_ENABLED, true)
                .putString(KEY_STATE, STATE_RESTING)
                .putLong(KEY_REST_END_AT, now + restSeconds(context) * 1_000L)
                .putLong(KEY_PAUSE_REMAINING_MS, 0L)
                .putLong(KEY_SCREEN_OFF_AT, 0L)
                .apply();
    }

    static void pause(Context context, long remainingMs) {
        prefs(context).edit()
                .putString(KEY_STATE, STATE_PAUSED)
                .putLong(KEY_PAUSE_REMAINING_MS, Math.max(0L, remainingMs))
                .apply();
    }

    static void resume(Context context, long now) {
        long remaining = Math.max(1_000L, pauseRemainingMs(context));
        prefs(context).edit()
                .putString(KEY_STATE, STATE_WORKING)
                .putLong(KEY_WORK_END_AT, now + remaining)
                .putLong(KEY_PAUSE_REMAINING_MS, 0L)
                .putLong(KEY_SCREEN_OFF_AT, 0L)
                .apply();
    }

    static void enterScreenOff(Context context, long now, long remainingMs) {
        prefs(context).edit()
                .putString(KEY_STATE, STATE_SCREEN_OFF)
                .putLong(KEY_PAUSE_REMAINING_MS, Math.max(0L, remainingMs))
                .putLong(KEY_SCREEN_OFF_AT, now)
                .apply();
    }

    static void stop(Context context) {
        prefs(context).edit()
                .putBoolean(KEY_ENABLED, false)
                .putString(KEY_STATE, STATE_STOPPED)
                .putLong(KEY_WORK_END_AT, 0L)
                .putLong(KEY_REST_END_AT, 0L)
                .putLong(KEY_PAUSE_REMAINING_MS, 0L)
                .putLong(KEY_SCREEN_OFF_AT, 0L)
                .apply();
    }

    static long remainingMs(Context context, long now) {
        String state = state(context);
        if (STATE_WORKING.equals(state)) {
            return Math.max(0L, workEndAt(context) - now);
        }
        if (STATE_RESTING.equals(state)) {
            return Math.max(0L, restEndAt(context) - now);
        }
        if (STATE_PAUSED.equals(state) || STATE_SCREEN_OFF.equals(state)) {
            return Math.max(0L, pauseRemainingMs(context));
        }
        return 0L;
    }

    static String stateLabel(String state) {
        if (STATE_WORKING.equals(state)) {
            return "正在用眼";
        }
        if (STATE_RESTING.equals(state)) {
            return "休息提醒中";
        }
        if (STATE_PAUSED.equals(state)) {
            return "已暂停";
        }
        if (STATE_SCREEN_OFF.equals(state)) {
            return "屏幕已关闭";
        }
        return "未开启";
    }

    static String formatRemaining(long remainingMs) {
        long totalSeconds = Math.max(0L, (remainingMs + 999L) / 1000L);
        long hours = totalSeconds / 3600L;
        long minutes = (totalSeconds % 3600L) / 60L;
        long seconds = totalSeconds % 60L;
        if (hours > 0L) {
            return String.format("%02d:%02d:%02d", hours, minutes, seconds);
        }
        return String.format("%02d:%02d", minutes, seconds);
    }
}
