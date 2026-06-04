package com.triple2.eyeprotection;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class RestActivity extends Activity {
    private static final int PRIMARY = Color.rgb(31, 122, 77);
    private TextView countdownText;
    private TextView messageText;
    private final Handler handler = new Handler(Looper.getMainLooper());

    private final BroadcastReceiver statusReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            refresh();
        }
    };

    private final Runnable refreshRunnable = new Runnable() {
        @Override
        public void run() {
            refresh();
            handler.postDelayed(this, 1000L);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true);
            setTurnScreenOn(true);
        }
        getWindow().addFlags(
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
                        | WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED
                        | WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
                        | WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD
        );
        buildUi();
        sendCommand(EyeCareService.ACTION_CHECK);
    }

    @Override
    protected void onResume() {
        super.onResume();
        registerStatusReceiver();
        handler.post(refreshRunnable);
        refresh();
    }

    @Override
    protected void onPause() {
        handler.removeCallbacks(refreshRunnable);
        unregisterReceiver(statusReceiver);
        super.onPause();
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setPadding(dp(24), dp(48), dp(24), dp(36));
        root.setBackgroundColor(Color.rgb(240, 255, 245));

        TextView title = new TextView(this);
        title.setText("休息时间到了");
        title.setTextColor(PRIMARY);
        title.setTextSize(30);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setGravity(Gravity.CENTER);
        root.addView(title);

        messageText = new TextView(this);
        messageText.setText("请离开屏幕，远望 6 米外");
        messageText.setTextColor(Color.rgb(54, 74, 64));
        messageText.setTextSize(18);
        messageText.setGravity(Gravity.CENTER);
        messageText.setPadding(0, dp(22), 0, dp(18));
        root.addView(messageText);

        countdownText = new TextView(this);
        countdownText.setText("00:00");
        countdownText.setTextColor(PRIMARY);
        countdownText.setTextSize(64);
        countdownText.setTypeface(Typeface.MONOSPACE, Typeface.BOLD);
        countdownText.setGravity(Gravity.CENTER);
        root.addView(countdownText);

        Button doneButton = new Button(this);
        doneButton.setText("休息好了");
        UiFeedback.applyButtonFeedback(doneButton, PRIMARY, dp(8));
        doneButton.setOnClickListener(v -> {
            sendCommand(EyeCareService.ACTION_REST_DONE);
            finish();
        });
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                dp(54)
        );
        params.setMargins(0, dp(36), 0, 0);
        root.addView(doneButton, params);

        setContentView(root);
    }

    private void refresh() {
        String state = AppPrefs.state(this);
        long remaining = AppPrefs.remainingMs(this, System.currentTimeMillis());
        countdownText.setText(AppPrefs.formatRemaining(remaining));
        if (AppPrefs.STATE_RESTING.equals(state)) {
            if (remaining <= 0L) {
                messageText.setText("休息时间已到，可以开始下一轮");
            } else {
                messageText.setText("请离开屏幕，远望 6 米外");
            }
        } else {
            finish();
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

    private void registerStatusReceiver() {
        IntentFilter filter = new IntentFilter(EyeCareService.ACTION_STATUS);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(statusReceiver, filter, Context.RECEIVER_NOT_EXPORTED);
        } else {
            registerReceiver(statusReceiver, filter);
        }
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
