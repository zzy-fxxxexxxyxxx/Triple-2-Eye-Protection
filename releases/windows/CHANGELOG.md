# Windows Installer Changelog

## 2.0.9 - 2026-07-05

- Added a `默认延时 (min)` setting on the Windows main screen, defaulting to `10`.
- Added `已用眼` to the rest reminder window so the popup shows total eye-use time since the last completed rest.
- Added a per-popup `延时：xx分钟` action; changing `xx` inside the reminder only affects that reminder and does not overwrite the default delay setting.
- Delayed reminders now preserve the original eye-use session, while `已提醒` starts fresh for each popup.
- Starting a rest keeps `已提醒` running but freezes `已用眼`.
- Bumped app and installer version to `2.0.9`.

Installer:

- `releases/windows/2.0.9/Triple2EyeProtection-Setup-2.0.9.exe`

## 2.0.8 - 2026-06-15

- Fixed an intermittent duplicate rest-popup issue after clicking `休息好了`.
- The reminder now notifies the main timer to finish and reset the round before the window is destroyed.
- Kept the destroy-time reset as a fallback for abnormal close paths.
- Bumped app and installer version to `2.0.8`.

Installer:

- `releases/windows/2.0.8/Triple2EyeProtection-Setup-2.0.8.exe`

## 2.0.7 - 2026-06-12

- Added a configurable fade-in duration for the rest reminder window.
- The input accepts decimal seconds, allowing millisecond-level values such as `0.300` or `1.250`.
- The reminder window now uses a linear opacity transition from transparent to opaque.
- Bumped app and installer version to `2.0.7`.

Installer:

- `releases/windows/2.0.7/Triple2EyeProtection-Setup-2.0.7.exe`

## 2.0.6 - 2026-06-04

- 修复 Windows 开机自启状态判断：正确识别 `StartupApproved` 中的启用/禁用状态。
- 保留 `Run` 注册表自启入口，并修正启用时写入 `0x02`、禁用时写入 `0x03`。
- 继续使用精简后的 PyInstaller 打包配置，减少无关 Qt 模块和冲突 DLL。
- 安装时清理旧版 `_internal` 目录，避免旧 DLL 干扰新版运行。

Installer:

- `releases/windows/2.0.6/Triple2EyeProtection-Setup-2.0.6.exe`
