package com.triple2.eyeprotection;

import android.content.Intent;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.service.quicksettings.Tile;
import android.service.quicksettings.TileService;

public class EyeCareTileService extends TileService {
    private final Handler handler = new Handler(Looper.getMainLooper());

    @Override
    public void onStartListening() {
        super.onStartListening();
        updateTile();
    }

    @Override
    public void onClick() {
        super.onClick();
        boolean shouldStop = isProtectionEnabled();
        setTileActive(!shouldStop);
        sendServiceCommand(shouldStop ? EyeCareService.ACTION_STOP : EyeCareService.ACTION_START);
        handler.postDelayed(this::updateTile, 400L);
    }

    private boolean isProtectionEnabled() {
        return AppPrefs.enabled(this) && !AppPrefs.STATE_STOPPED.equals(AppPrefs.state(this));
    }

    private void sendServiceCommand(String action) {
        Intent intent = new Intent(this, EyeCareService.class);
        intent.setAction(action);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent);
        } else {
            startService(intent);
        }
    }

    private void updateTile() {
        setTileActive(isProtectionEnabled());
    }

    private void setTileActive(boolean active) {
        Tile tile = getQsTile();
        if (tile == null) {
            return;
        }
        tile.setState(active ? Tile.STATE_ACTIVE : Tile.STATE_INACTIVE);
        tile.setLabel("Triple 2 护眼");
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            tile.setSubtitle(active ? "运行中" : "未开启");
        }
        tile.updateTile();
    }
}
