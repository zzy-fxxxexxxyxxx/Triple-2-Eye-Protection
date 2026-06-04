package com.triple2.eyeprotection;

import android.content.Context;
import android.content.SharedPreferences;

final class UsageStore {
    static final String TYPE_REST_STARTED = "rest_started";
    static final String TYPE_REST_DONE = "rest_done";
    static final String TYPE_SCREEN_REST = "screen_rest";

    private static final String KEY_EVENTS = "usage_events";
    private static final long KEEP_MS = 370L * 24L * 60L * 60L * 1000L;

    private UsageStore() {
    }

    static void record(Context context, String type) {
        long now = System.currentTimeMillis();
        SharedPreferences prefs = AppPrefs.prefs(context);
        String existing = prefs.getString(KEY_EVENTS, "");
        StringBuilder next = new StringBuilder();
        long keepAfter = now - KEEP_MS;
        if (existing != null && !existing.isEmpty()) {
            String[] rows = existing.split(";");
            for (String row : rows) {
                String[] parts = row.split(",", 2);
                if (parts.length != 2) {
                    continue;
                }
                try {
                    long timestamp = Long.parseLong(parts[0]);
                    if (timestamp >= keepAfter) {
                        append(next, timestamp, parts[1]);
                    }
                } catch (NumberFormatException ignored) {
                    // Ignore corrupt rows from older builds.
                }
            }
        }
        append(next, now, type);
        prefs.edit().putString(KEY_EVENTS, next.toString()).apply();
    }

    static int countSince(Context context, long sinceMs, String type) {
        String existing = AppPrefs.prefs(context).getString(KEY_EVENTS, "");
        if (existing == null || existing.isEmpty()) {
            return 0;
        }
        int count = 0;
        String[] rows = existing.split(";");
        for (String row : rows) {
            String[] parts = row.split(",", 2);
            if (parts.length != 2 || !type.equals(parts[1])) {
                continue;
            }
            try {
                long timestamp = Long.parseLong(parts[0]);
                if (timestamp >= sinceMs) {
                    count++;
                }
            } catch (NumberFormatException ignored) {
                // Ignore corrupt rows from older builds.
            }
        }
        return count;
    }

    static String summary(Context context) {
        long now = System.currentTimeMillis();
        long hour = 60L * 60L * 1000L;
        long day = 24L * hour;
        StringBuilder text = new StringBuilder();
        addLine(text, "12h", countSince(context, now - 12L * hour, TYPE_REST_DONE));
        addLine(text, "24h", countSince(context, now - day, TYPE_REST_DONE));
        addLine(text, "7天", countSince(context, now - 7L * day, TYPE_REST_DONE));
        addLine(text, "1个月", countSince(context, now - 30L * day, TYPE_REST_DONE));
        addLine(text, "6个月", countSince(context, now - 180L * day, TYPE_REST_DONE));
        addLine(text, "1年", countSince(context, now - 365L * day, TYPE_REST_DONE));
        return text.toString();
    }

    private static void addLine(StringBuilder text, String label, int count) {
        if (text.length() > 0) {
            text.append('\n');
        }
        text.append(label).append("：完成休息 ").append(count).append(" 次");
    }

    private static void append(StringBuilder builder, long timestamp, String type) {
        if (builder.length() > 0) {
            builder.append(';');
        }
        builder.append(timestamp).append(',').append(type);
    }
}
