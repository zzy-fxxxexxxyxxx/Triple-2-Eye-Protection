package com.triple2.eyeprotection;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (!AppPrefs.enabled(context)) {
            return;
        }
        Intent serviceIntent = new Intent(context, EyeCareService.class);
        serviceIntent.setAction(EyeCareService.ACTION_BOOT);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(serviceIntent);
        } else {
            context.startService(serviceIntent);
        }
    }
}
