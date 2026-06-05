# Android APK Changelog

## 0.1.3 - 2026-06-05

- 修复后台到点只震动、不弹出休息页的问题。
- 将常驻倒计时通知和休息全屏提醒通知拆成两个独立通知。
- 新增独立高优先级通知渠道 `休息全屏提醒`，到点时通过 full-screen intent 打开 `RestActivity`。
- 新增“打开全屏提醒权限”入口，便于在 Android/HarmonyOS 通知权限设置里允许后台全屏提醒。
- 版本号递增到 `versionCode 4` / `versionName 0.1.3`，可覆盖安装 `0.1.2`。

APK:

- `releases/android/0.1.3/Triple2EyeProtection-Android-0.1.3-release.apk`

## 0.1.2 - 2026-06-05

- 保留按钮视觉点击反馈：按下变暗、轻微缩小、松手回弹。
- 关闭按钮触感震动，避免每次点击都震动。
- 版本号递增到 `versionCode 3` / `versionName 0.1.2`，可覆盖安装 `0.1.1`。

APK:

- `releases/android/0.1.2/Triple2EyeProtection-Android-0.1.2-release.apk`
