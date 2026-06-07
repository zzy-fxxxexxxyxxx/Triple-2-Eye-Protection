package com.triple2.eyeprotection;

import android.Manifest;
import android.app.Activity;
import android.app.AlarmManager;
import android.app.AlertDialog;
import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final int PRIMARY = Color.rgb(31, 122, 77);
    private static final int BACKGROUND = Color.rgb(245, 249, 247);
    private static final int CARD = Color.WHITE;
    private static final int TEXT = Color.rgb(32, 38, 35);

    private TextView stateText;
    private TextView countdownText;
    private TextView statsText;
    private EditText workMinutesEdit;
    private EditText restSecondsEdit;
    private Button pauseButton;
    private Button startButton;

    private final BroadcastReceiver statusReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            refreshFromPrefs();
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestNotificationPermission();
        buildUi();
        refreshFromPrefs();
        if (AppPrefs.enabled(this)) {
            sendCommand(EyeCareService.ACTION_CHECK);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        registerStatusReceiver();
        refreshFromPrefs();
    }

    @Override
    protected void onPause() {
        unregisterReceiver(statusReceiver);
        super.onPause();
    }

    private void buildUi() {
        ScrollView scrollView = new ScrollView(this);
        scrollView.setFillViewport(true);
        scrollView.setBackgroundColor(BACKGROUND);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(24), dp(20), dp(28));
        scrollView.addView(root, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT,
                ScrollView.LayoutParams.WRAP_CONTENT
        ));

        TextView title = new TextView(this);
        title.setText("Triple 2 Eye Protection");
        title.setTextColor(TEXT);
        title.setTextSize(24);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("护眼倒计时会通过常驻通知在后台运行");
        subtitle.setTextColor(Color.rgb(88, 103, 96));
        subtitle.setTextSize(14);
        subtitle.setPadding(0, dp(6), 0, dp(18));
        root.addView(subtitle);

        LinearLayout statusCard = card();
        stateText = label("未开启", 18, true);
        countdownText = label("00:00", 52, true);
        countdownText.setGravity(Gravity.CENTER_HORIZONTAL);
        countdownText.setTypeface(Typeface.MONOSPACE, Typeface.BOLD);
        statusCard.addView(stateText);
        statusCard.addView(countdownText);
        root.addView(statusCard);

        LinearLayout settingsCard = card();
        settingsCard.addView(label("设置", 18, true));
        workMinutesEdit = numberEdit("20");
        restSecondsEdit = numberEdit("20");
        settingsCard.addView(durationRow("用眼时间：", workMinutesEdit, "分钟"));
        settingsCard.addView(durationRow("休息时间：", restSecondsEdit, "秒"));

        Button saveButton = button("保存设置");
        saveButton.setOnClickListener(v -> {
            if (saveSettings()) {
                Toast.makeText(this, "设置已保存，当前轮次可点“重置”后立即生效", Toast.LENGTH_SHORT).show();
                refreshFromPrefs();
            }
        });
        settingsCard.addView(saveButton);
        root.addView(settingsCard);

        LinearLayout actionsCard = card();
        actionsCard.addView(label("控制", 18, true));
        startButton = button("开启护眼");
        startButton.setOnClickListener(v -> {
            if (saveSettings()) {
                sendCommand(EyeCareService.ACTION_START);
            }
        });
        actionsCard.addView(startButton);

        pauseButton = button("暂停");
        pauseButton.setOnClickListener(v -> {
            String state = AppPrefs.state(this);
            if (AppPrefs.STATE_PAUSED.equals(state)) {
                sendCommand(EyeCareService.ACTION_RESUME);
            } else {
                sendCommand(EyeCareService.ACTION_PAUSE);
            }
        });
        actionsCard.addView(pauseButton);

        Button resetButton = button("重置");
        resetButton.setOnClickListener(v -> {
            if (saveSettings()) {
                sendCommand(EyeCareService.ACTION_RESET);
            }
        });
        actionsCard.addView(resetButton);

        Button restNowButton = button("立即休息");
        restNowButton.setOnClickListener(v -> {
            if (saveSettings()) {
                sendCommand(EyeCareService.ACTION_REST_NOW);
            }
        });
        actionsCard.addView(restNowButton);

        Button stopButton = button("关闭服务");
        stopButton.setOnClickListener(v -> sendCommand(EyeCareService.ACTION_STOP));
        actionsCard.addView(stopButton);
        root.addView(actionsCard);

        LinearLayout keepAliveCard = card();
        keepAliveCard.addView(label("华为保活", 18, true));
        TextView keepAliveText = label("建议开启：允许通知、全屏提醒、悬浮窗/显示在其他应用上层、忽略电池优化、应用启动管理中允许自启动/关联启动/后台活动，并在多任务界面锁定应用。", 14, false);
        keepAliveText.setTextColor(Color.rgb(88, 103, 96));
        keepAliveCard.addView(keepAliveText);

        Button keepAliveButton = button("打开保活设置");
        keepAliveButton.setOnClickListener(v -> showKeepAliveDialog());
        keepAliveCard.addView(keepAliveButton);
        root.addView(keepAliveCard);

        LinearLayout statsCard = card();
        statsCard.addView(label("休息统计", 18, true));
        statsText = label("", 14, false);
        statsText.setTextColor(Color.rgb(72, 87, 80));
        statsCard.addView(statsText);
        root.addView(statsCard);

        setContentView(scrollView);
    }

    private void refreshFromPrefs() {
        if (stateText == null) {
            return;
        }
        long now = System.currentTimeMillis();
        String state = AppPrefs.state(this);
        stateText.setText(AppPrefs.stateLabel(state));
        countdownText.setText(AppPrefs.formatRemaining(AppPrefs.remainingMs(this, now)));
        statsText.setText(UsageStore.summary(this));

        if (!workMinutesEdit.hasFocus()) {
            workMinutesEdit.setText(String.valueOf(AppPrefs.workMinutes(this)));
        }
        if (!restSecondsEdit.hasFocus()) {
            restSecondsEdit.setText(String.valueOf(AppPrefs.restSeconds(this)));
        }

        pauseButton.setEnabled(AppPrefs.STATE_WORKING.equals(state) || AppPrefs.STATE_PAUSED.equals(state));
        pauseButton.setText(AppPrefs.STATE_PAUSED.equals(state) ? "继续" : "暂停");
        startButton.setText(AppPrefs.STATE_STOPPED.equals(state) ? "开启护眼" : "重新开始");
    }

    private boolean saveSettings() {
        try {
            int workMinutes = Integer.parseInt(workMinutesEdit.getText().toString().trim());
            int restSeconds = Integer.parseInt(restSecondsEdit.getText().toString().trim());
            if (workMinutes <= 0 || restSeconds <= 0) {
                Toast.makeText(this, "时间必须大于 0", Toast.LENGTH_SHORT).show();
                return false;
            }
            AppPrefs.setDurations(this, workMinutes, restSeconds);
            return true;
        } catch (NumberFormatException e) {
            Toast.makeText(this, "请输入有效数字", Toast.LENGTH_SHORT).show();
            return false;
        }
    }

    private void sendCommand(String action) {
        Intent intent = new Intent(this, EyeCareService.class);
        intent.setAction(action);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent);
        } else {
            startService(intent);
        }
    }

    private void showKeepAliveDialog() {
        String[] items = new String[]{
                "请求忽略电池优化",
                "打开精确闹钟权限",
                "打开全屏提醒权限",
                "打开悬浮窗权限",
                "打开华为应用启动管理",
                "打开本应用详情"
        };
        new AlertDialog.Builder(this)
                .setTitle("华为保活设置")
                .setMessage("P60 上请尽量允许后台活动。系统设置入口可能会因 HarmonyOS/EMUI 版本不同而变化，打不开时会回到应用详情页。")
                .setItems(items, (dialog, which) -> {
                    if (which == 0) {
                        requestIgnoreBatteryOptimizations();
                    } else if (which == 1) {
                        requestExactAlarmPermission();
                    } else if (which == 2) {
                        requestFullScreenIntentPermission();
                    } else if (which == 3) {
                        requestOverlayPermission();
                    } else if (which == 4) {
                        openHuaweiStartupManager();
                    } else {
                        openAppDetails();
                    }
                })
                .show();
    }

    private void requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 2202);
        }
    }

    private void requestIgnoreBatteryOptimizations() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) {
            return;
        }
        PowerManager powerManager = (PowerManager) getSystemService(POWER_SERVICE);
        if (powerManager != null && powerManager.isIgnoringBatteryOptimizations(getPackageName())) {
            Toast.makeText(this, "已经在电池优化白名单中", Toast.LENGTH_SHORT).show();
            return;
        }
        Intent intent = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
        intent.setData(Uri.parse("package:" + getPackageName()));
        startSafely(intent);
    }

    private void requestExactAlarmPermission() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) {
            Toast.makeText(this, "当前系统不需要单独开启精确闹钟权限", Toast.LENGTH_SHORT).show();
            return;
        }
        AlarmManager alarmManager = (AlarmManager) getSystemService(ALARM_SERVICE);
        if (alarmManager != null && alarmManager.canScheduleExactAlarms()) {
            Toast.makeText(this, "精确闹钟权限已允许", Toast.LENGTH_SHORT).show();
            return;
        }
        Intent intent = new Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM);
        intent.setData(Uri.parse("package:" + getPackageName()));
        startSafely(intent);
    }

    private void requestFullScreenIntentPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            NotificationManager manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (manager != null && manager.canUseFullScreenIntent()) {
                Toast.makeText(this, "全屏提醒权限已允许", Toast.LENGTH_SHORT).show();
                return;
            }
            Intent intent = new Intent(Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT);
            intent.setData(Uri.parse("package:" + getPackageName()));
            if (startSafely(intent)) {
                return;
            }
        }
        openAppNotificationSettings();
    }

    private void requestOverlayPermission() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) {
            Toast.makeText(this, "当前系统不需要单独开启悬浮窗权限", Toast.LENGTH_SHORT).show();
            return;
        }
        if (Settings.canDrawOverlays(this)) {
            Toast.makeText(this, "悬浮窗权限已允许", Toast.LENGTH_SHORT).show();
            return;
        }
        Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION);
        intent.setData(Uri.parse("package:" + getPackageName()));
        if (!startSafely(intent)) {
            openAppDetails();
        }
    }

    private void openAppNotificationSettings() {
        Intent intent;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            intent = new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS);
            intent.putExtra(Settings.EXTRA_APP_PACKAGE, getPackageName());
        } else {
            intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
            intent.setData(Uri.parse("package:" + getPackageName()));
        }
        if (!startSafely(intent)) {
            openAppDetails();
        }
    }

    private void openHuaweiStartupManager() {
        ComponentName[] components = new ComponentName[]{
                new ComponentName("com.huawei.systemmanager", "com.huawei.systemmanager.startupmgr.ui.StartupNormalAppListActivity"),
                new ComponentName("com.huawei.systemmanager", "com.huawei.systemmanager.appcontrol.activity.StartupAppControlActivity"),
                new ComponentName("com.huawei.systemmanager", "com.huawei.systemmanager.optimize.bootstart.BootStartActivity")
        };
        for (ComponentName component : components) {
            Intent intent = new Intent();
            intent.setComponent(component);
            if (startSafely(intent)) {
                return;
            }
        }
        openAppDetails();
    }

    private void openAppDetails() {
        Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
        intent.setData(Uri.parse("package:" + getPackageName()));
        startSafely(intent);
    }

    private boolean startSafely(Intent intent) {
        try {
            startActivity(intent);
            return true;
        } catch (RuntimeException e) {
            return false;
        }
    }

    private void registerStatusReceiver() {
        IntentFilter filter = new IntentFilter(EyeCareService.ACTION_STATUS);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(statusReceiver, filter, Context.RECEIVER_NOT_EXPORTED);
        } else {
            registerReceiver(statusReceiver, filter);
        }
    }

    private LinearLayout card() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(dp(16), dp(16), dp(16), dp(16));
        GradientDrawable background = new GradientDrawable();
        background.setColor(CARD);
        background.setCornerRadius(dp(8));
        layout.setBackground(background);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
        );
        params.setMargins(0, 0, 0, dp(14));
        layout.setLayoutParams(params);
        return layout;
    }

    private TextView label(String text, int sp, boolean bold) {
        TextView view = new TextView(this);
        view.setText(text);
        view.setTextColor(TEXT);
        view.setTextSize(sp);
        view.setPadding(0, 0, 0, dp(10));
        if (bold) {
            view.setTypeface(Typeface.DEFAULT_BOLD);
        }
        return view;
    }

    private EditText numberEdit(String hint) {
        EditText editText = new EditText(this);
        editText.setHint(hint);
        editText.setInputType(InputType.TYPE_CLASS_NUMBER);
        editText.setSingleLine(true);
        editText.setTextColor(TEXT);
        editText.setHintTextColor(Color.rgb(118, 132, 125));
        editText.setPadding(0, dp(8), 0, dp(8));
        return editText;
    }

    private LinearLayout durationRow(String labelText, EditText editText, String unitText) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setPadding(0, dp(4), 0, dp(4));

        TextView name = new TextView(this);
        name.setText(labelText);
        name.setTextColor(TEXT);
        name.setTextSize(15);
        row.addView(name, new LinearLayout.LayoutParams(dp(92), LinearLayout.LayoutParams.WRAP_CONTENT));

        row.addView(editText, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        TextView unit = new TextView(this);
        unit.setText(unitText);
        unit.setTextColor(Color.rgb(88, 103, 96));
        unit.setTextSize(15);
        unit.setGravity(Gravity.END);
        row.addView(unit, new LinearLayout.LayoutParams(dp(44), LinearLayout.LayoutParams.WRAP_CONTENT));

        return row;
    }

    private Button button(String text) {
        Button button = new Button(this);
        button.setText(text);
        UiFeedback.applyButtonFeedback(button, PRIMARY, dp(8));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                dp(48)
        );
        params.setMargins(0, dp(8), 0, 0);
        button.setLayoutParams(params);
        return button;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
