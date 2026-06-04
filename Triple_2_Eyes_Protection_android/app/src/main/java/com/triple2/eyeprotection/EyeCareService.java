package com.triple2.eyeprotection;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.os.VibrationEffect;
import android.os.Vibrator;

public class EyeCareService extends Service {
    public static final String ACTION_START = "com.triple2.eyeprotection.START";
    public static final String ACTION_PAUSE = "com.triple2.eyeprotection.PAUSE";
    public static final String ACTION_RESUME = "com.triple2.eyeprotection.RESUME";
    public static final String ACTION_RESET = "com.triple2.eyeprotection.RESET";
    public static final String ACTION_STOP = "com.triple2.eyeprotection.STOP";
    public static final String ACTION_REST_NOW = "com.triple2.eyeprotection.REST_NOW";
    public static final String ACTION_REST_DONE = "com.triple2.eyeprotection.REST_DONE";
    public static final String ACTION_CHECK = "com.triple2.eyeprotection.CHECK";
    public static final String ACTION_BOOT = "com.triple2.eyeprotection.BOOT";
    public static final String ACTION_UPDATE_SETTINGS = "com.triple2.eyeprotection.UPDATE_SETTINGS";
    public static final String ACTION_STATUS = "com.triple2.eyeprotection.STATUS";

    public static final String EXTRA_STATE = "state";
    public static final String EXTRA_REMAINING_MS = "remaining_ms";
    public static final String EXTRA_WORK_MINUTES = "work_minutes";
    public static final String EXTRA_REST_SECONDS = "rest_seconds";
    public static final String EXTRA_ENABLED = "enabled";

    private static final String CHANNEL_ID = "eye_care_timer";
    private static final int NOTIFICATION_ID = 2202;
    private static final int REQUEST_CONTENT = 10;
    private static final int REQUEST_PAUSE = 11;
    private static final int REQUEST_RESUME = 12;
    private static final int REQUEST_RESET = 13;
    private static final int REQUEST_REST_NOW = 14;
    private static final int REQUEST_REST_DONE = 15;
    private static final int REQUEST_ALARM = 16;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private BroadcastReceiver screenReceiver;

    private final Runnable tickRunnable = new Runnable() {
        @Override
        public void run() {
            checkDue();
            publishStatus();
            notifyNow(false);
            handler.postDelayed(this, 1000L);
        }
    };

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        registerScreenReceiver();
        handler.post(tickRunnable);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        startForeground(NOTIFICATION_ID, buildNotification(false));
        acquireWakeLockBriefly();

        String action = intent == null ? ACTION_CHECK : intent.getAction();
        if (action == null) {
            action = ACTION_CHECK;
        }
        handleAction(action);
        publishStatus();
        notifyNow(false);
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        handler.removeCallbacks(tickRunnable);
        cancelAlarm();
        if (screenReceiver != null) {
            unregisterReceiver(screenReceiver);
            screenReceiver = null;
        }
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private void handleAction(String action) {
        long now = System.currentTimeMillis();
        if (ACTION_START.equals(action) || ACTION_RESET.equals(action)) {
            AppPrefs.startWorking(this, now);
            scheduleAlarm(AppPrefs.workEndAt(this));
            return;
        }
        if (ACTION_PAUSE.equals(action)) {
            if (AppPrefs.STATE_WORKING.equals(AppPrefs.state(this))) {
                AppPrefs.pause(this, AppPrefs.remainingMs(this, now));
                cancelAlarm();
            }
            return;
        }
        if (ACTION_RESUME.equals(action)) {
            if (AppPrefs.STATE_PAUSED.equals(AppPrefs.state(this))) {
                AppPrefs.resume(this, now);
                scheduleAlarm(AppPrefs.workEndAt(this));
            }
            return;
        }
        if (ACTION_STOP.equals(action)) {
            AppPrefs.stop(this);
            cancelAlarm();
            publishStatus();
            stopForeground(true);
            stopSelf();
            return;
        }
        if (ACTION_REST_NOW.equals(action)) {
            enterRest(true);
            return;
        }
        if (ACTION_REST_DONE.equals(action)) {
            if (AppPrefs.STATE_RESTING.equals(AppPrefs.state(this))) {
                UsageStore.record(this, UsageStore.TYPE_REST_DONE);
            }
            AppPrefs.startWorking(this, now);
            scheduleAlarm(AppPrefs.workEndAt(this));
            return;
        }
        if (ACTION_BOOT.equals(action)) {
            restoreAfterBoot(now);
            return;
        }
        if (ACTION_CHECK.equals(action)) {
            checkDue();
            rescheduleForCurrentState();
        }
    }

    private void restoreAfterBoot(long now) {
        if (!AppPrefs.enabled(this)) {
            stopSelf();
            return;
        }
        String state = AppPrefs.state(this);
        if (AppPrefs.STATE_STOPPED.equals(state)) {
            AppPrefs.startWorking(this, now);
        } else if (AppPrefs.STATE_SCREEN_OFF.equals(state)) {
            AppPrefs.startWorking(this, now);
        } else {
            checkDue();
        }
        rescheduleForCurrentState();
    }

    private void checkDue() {
        long now = System.currentTimeMillis();
        String state = AppPrefs.state(this);
        if (AppPrefs.STATE_WORKING.equals(state) && AppPrefs.remainingMs(this, now) <= 0L) {
            enterRest(true);
        }
    }

    private void enterRest(boolean alert) {
        long now = System.currentTimeMillis();
        AppPrefs.startResting(this, now);
        UsageStore.record(this, UsageStore.TYPE_REST_STARTED);
        scheduleAlarm(AppPrefs.restEndAt(this));
        notifyNow(alert);
        vibrateForRest();
        showRestActivity();
    }

    private void onScreenOff() {
        long now = System.currentTimeMillis();
        if (AppPrefs.STATE_WORKING.equals(AppPrefs.state(this))) {
            AppPrefs.enterScreenOff(this, now, AppPrefs.remainingMs(this, now));
            cancelAlarm();
            publishStatus();
            notifyNow(false);
        }
    }

    private void onScreenActive() {
        if (!AppPrefs.STATE_SCREEN_OFF.equals(AppPrefs.state(this))) {
            return;
        }
        long now = System.currentTimeMillis();
        long inactiveMs = Math.max(0L, now - AppPrefs.screenOffAt(this));
        long requiredRestMs = AppPrefs.restSeconds(this) * 1000L;
        if (inactiveMs >= requiredRestMs) {
            UsageStore.record(this, UsageStore.TYPE_SCREEN_REST);
            UsageStore.record(this, UsageStore.TYPE_REST_DONE);
            AppPrefs.startWorking(this, now);
        } else {
            AppPrefs.resume(this, now);
        }
        scheduleAlarm(AppPrefs.workEndAt(this));
        publishStatus();
        notifyNow(false);
    }

    private void rescheduleForCurrentState() {
        String state = AppPrefs.state(this);
        if (AppPrefs.STATE_WORKING.equals(state)) {
            scheduleAlarm(AppPrefs.workEndAt(this));
        } else if (AppPrefs.STATE_RESTING.equals(state)) {
            scheduleAlarm(AppPrefs.restEndAt(this));
        } else {
            cancelAlarm();
        }
    }

    private Notification buildNotification(boolean alertRest) {
        long now = System.currentTimeMillis();
        String state = AppPrefs.state(this);
        long remaining = AppPrefs.remainingMs(this, now);

        Intent mainIntent = new Intent(this, MainActivity.class);
        mainIntent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity(
                this,
                REQUEST_CONTENT,
                mainIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Notification.Builder builder = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                ? new Notification.Builder(this, CHANNEL_ID)
                : new Notification.Builder(this);

        builder.setSmallIcon(R.drawable.ic_stat_eye)
                .setContentTitle("Triple 2 Eye Protection")
                .setContentText(notificationText(state, remaining))
                .setContentIntent(contentIntent)
                .setOngoing(!AppPrefs.STATE_STOPPED.equals(state))
                .setOnlyAlertOnce(!alertRest)
                .setShowWhen(false);

        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            builder.setPriority(Notification.PRIORITY_HIGH);
        }

        if (AppPrefs.STATE_RESTING.equals(state)) {
            Intent restIntent = new Intent(this, RestActivity.class);
            restIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            PendingIntent restPendingIntent = PendingIntent.getActivity(
                    this,
                    REQUEST_REST_DONE,
                    restIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            );
            builder.setContentIntent(restPendingIntent)
                    .setCategory(Notification.CATEGORY_ALARM)
                    .setPriority(Notification.PRIORITY_MAX)
                    .setFullScreenIntent(restPendingIntent, alertRest)
                    .addAction(R.drawable.ic_stat_eye, "休息好了", serviceIntent(ACTION_REST_DONE, REQUEST_REST_DONE));
        } else {
            if (AppPrefs.STATE_PAUSED.equals(state)) {
                builder.addAction(R.drawable.ic_stat_eye, "继续", serviceIntent(ACTION_RESUME, REQUEST_RESUME));
            } else {
                builder.addAction(R.drawable.ic_stat_eye, "暂停", serviceIntent(ACTION_PAUSE, REQUEST_PAUSE));
            }
            builder.addAction(R.drawable.ic_stat_eye, "重置", serviceIntent(ACTION_RESET, REQUEST_RESET));
            builder.addAction(R.drawable.ic_stat_eye, "立即休息", serviceIntent(ACTION_REST_NOW, REQUEST_REST_NOW));
        }

        return builder.build();
    }

    private String notificationText(String state, long remaining) {
        if (AppPrefs.STATE_WORKING.equals(state)) {
            return "距离休息还有 " + AppPrefs.formatRemaining(remaining);
        }
        if (AppPrefs.STATE_RESTING.equals(state)) {
            if (remaining <= 0L) {
                return "休息时间已到，点击“休息好了”开始下一轮";
            }
            return "请远望放松，还需 " + AppPrefs.formatRemaining(remaining);
        }
        if (AppPrefs.STATE_PAUSED.equals(state)) {
            return "已暂停，剩余 " + AppPrefs.formatRemaining(remaining);
        }
        if (AppPrefs.STATE_SCREEN_OFF.equals(state)) {
            return "息屏中；满 " + AppPrefs.restSeconds(this) + " 秒会视为已休息";
        }
        return "护眼服务未开启";
    }

    private void publishStatus() {
        long now = System.currentTimeMillis();
        Intent status = new Intent(ACTION_STATUS);
        status.setPackage(getPackageName());
        status.putExtra(EXTRA_STATE, AppPrefs.state(this));
        status.putExtra(EXTRA_REMAINING_MS, AppPrefs.remainingMs(this, now));
        status.putExtra(EXTRA_WORK_MINUTES, AppPrefs.workMinutes(this));
        status.putExtra(EXTRA_REST_SECONDS, AppPrefs.restSeconds(this));
        status.putExtra(EXTRA_ENABLED, AppPrefs.enabled(this));
        sendBroadcast(status);
    }

    private void notifyNow(boolean alertRest) {
        NotificationManager manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (manager != null) {
            manager.notify(NOTIFICATION_ID, buildNotification(alertRest));
        }
    }

    private PendingIntent serviceIntent(String action, int requestCode) {
        Intent intent = new Intent(this, EyeCareService.class);
        intent.setAction(action);
        return PendingIntent.getService(
                this,
                requestCode,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
    }

    private PendingIntent alarmIntent() {
        Intent intent = new Intent(this, AlarmReceiver.class);
        intent.setAction(ACTION_CHECK);
        return PendingIntent.getBroadcast(
                this,
                REQUEST_ALARM,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
    }

    private void scheduleAlarm(long triggerAtMillis) {
        if (triggerAtMillis <= 0L) {
            return;
        }
        AlarmManager alarmManager = (AlarmManager) getSystemService(ALARM_SERVICE);
        if (alarmManager == null) {
            return;
        }
        PendingIntent pendingIntent = alarmIntent();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && !alarmManager.canScheduleExactAlarms()) {
            alarmManager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAtMillis, pendingIntent);
        } else {
            alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAtMillis, pendingIntent);
        }
    }

    private void cancelAlarm() {
        AlarmManager alarmManager = (AlarmManager) getSystemService(ALARM_SERVICE);
        if (alarmManager != null) {
            alarmManager.cancel(alarmIntent());
        }
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            return;
        }
        NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "护眼倒计时",
                NotificationManager.IMPORTANCE_HIGH
        );
        channel.setDescription("显示护眼倒计时和休息提醒");
        channel.enableVibration(true);
        NotificationManager manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (manager != null) {
            manager.createNotificationChannel(channel);
        }
    }

    private void registerScreenReceiver() {
        screenReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                String action = intent.getAction();
                if (Intent.ACTION_SCREEN_OFF.equals(action)) {
                    onScreenOff();
                } else if (Intent.ACTION_SCREEN_ON.equals(action) || Intent.ACTION_USER_PRESENT.equals(action)) {
                    onScreenActive();
                }
            }
        };
        IntentFilter filter = new IntentFilter();
        filter.addAction(Intent.ACTION_SCREEN_OFF);
        filter.addAction(Intent.ACTION_SCREEN_ON);
        filter.addAction(Intent.ACTION_USER_PRESENT);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(screenReceiver, filter, Context.RECEIVER_NOT_EXPORTED);
        } else {
            registerReceiver(screenReceiver, filter);
        }
    }

    private void showRestActivity() {
        Intent intent = new Intent(this, RestActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        try {
            startActivity(intent);
        } catch (RuntimeException ignored) {
            // Android may block background activity launches; the full-screen notification remains as fallback.
        }
    }

    private void vibrateForRest() {
        Vibrator vibrator = (Vibrator) getSystemService(VIBRATOR_SERVICE);
        if (vibrator == null || !vibrator.hasVibrator()) {
            return;
        }
        long[] pattern = new long[]{0L, 300L, 180L, 300L};
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1));
        } else {
            vibrator.vibrate(pattern, -1);
        }
    }

    private void acquireWakeLockBriefly() {
        PowerManager powerManager = (PowerManager) getSystemService(POWER_SERVICE);
        if (powerManager == null) {
            return;
        }
        PowerManager.WakeLock wakeLock = powerManager.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "Triple2EyeProtection:ServiceWake"
        );
        wakeLock.setReferenceCounted(false);
        try {
            wakeLock.acquire(5_000L);
        } catch (RuntimeException ignored) {
            // Some vendor builds are strict about wake locks; foreground service still continues.
        }
    }
}
