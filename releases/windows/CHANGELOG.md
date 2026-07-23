# Windows Installer Changelog

## 2.1.8 - 2026-07-23

- Replaced the single reminder-popup delay control with three red delay buttons in the first button row.
- The three delay buttons default to the main default delay value, `20` minutes, and `30` minutes, so a fresh install shows `10/20/30`.
- Kept each delay value editable inside its own button for the current popup only.
- Preserved the existing delay behavior: clicking a delay button closes the reminder, continues eye use, and does not reset the accumulated `已用眼` time.
- Bumped Windows app and installer version to `2.1.8`.

Installer:

- `releases/windows/2.1.8/Triple2EyeProtection-Setup-2.1.8.exe`

## 2.1.7 - 2026-07-12

- Replaced the glossy gradient/card-heavy main window with a restrained flat desktop-tool layout.
- Made the main window size responsive to the current screen's available logical resolution instead of using a fixed `430x740` size.
- Kept the complete panel visible at `420x496` and larger, covering MateBook 14 at 250% Windows scaling.
- Added an internal vertical scroll fallback for smaller logical screens without horizontal scrolling.
- Compressed the seven main actions into a stable three-row grid while preserving all existing behavior.
- Bumped Windows app and installer version to `2.1.7`.

Installer:

- `releases/windows/2.1.7/Triple2EyeProtection-Setup-2.1.7.exe`

## 2.1.6 - 2026-07-06

- Redesigned the Windows main settings window into a modern control panel with a gradient header, card sections, compact parameter grid, and integrated status/action panel.
- Added a countdown progress bar that follows the remaining reminder time.
- Added visual status badges for running, paused, warning, and alert states.
- Added system icons to the main action buttons, including pause/resume icon switching.
- Bumped Windows app and installer version to `2.1.6`.

Installer:

- `releases/windows/2.1.6/Triple2EyeProtection-Setup-2.1.6.exe`

## 2.1.5 - 2026-07-06

- Reworked curve chart time-axis labels so the first and last labels stay inside the chart width.
- Removed the extra-looking bottom border below time labels by separating the data plot area from the x-axis label area.
- Reduced the vertical gap below time labels while keeping a safe bottom margin inside the chart widget.
- Added width checks for curve chart time labels at common query window sizes.
- Bumped Windows app and installer version to `2.1.5`.

Installer:

- `releases/windows/2.1.5/Triple2EyeProtection-Setup-2.1.5.exe`

## 2.1.4 - 2026-07-06

- Added explicit bottom padding inside the `状态曲线` group so the chart widget no longer visually covers the group border in full screen.
- Kept curve chart time ticks inside the white plot area with a larger internal bottom safety band.
- Reduced the plot widget minimum height to fit the default query window while preserving full-screen expansion.
- Added full-screen geometry and curve-rendering checks for the query chart.
- Bumped Windows app and installer version to `2.1.4`.

Installer:

- `releases/windows/2.1.4/Triple2EyeProtection-Setup-2.1.4.exe`

## 2.1.3 - 2026-07-06

- Moved curve chart time ticks into an internal bottom band so they no longer overflow the `状态曲线` area.
- Reduced the chart widget minimum height to avoid the default query window being forced beyond its visible bounds.
- Added markers for both segment start and segment end points.
- Added markers for raw log record points, including same-second state changes that do not create visible duration segments.
- Bumped Windows app and installer version to `2.1.3`.

Installer:

- `releases/windows/2.1.3/Triple2EyeProtection-Setup-2.1.3.exe`

## 2.1.2 - 2026-07-06

- Restored gradient transition lines between curve chart states.
- Changed long `未记录` curve segments from gray dashed lines to gray solid lines.
- Increased the timeline color block height and made it scale with the chart widget height.
- Added more curve chart vertical padding so the bottom state line and time labels stay inside the `状态曲线` area.
- Bumped Windows app and installer version to `2.1.2`.

Installer:

- `releases/windows/2.1.2/Triple2EyeProtection-Setup-2.1.2.exe`

## 2.1.1 - 2026-07-06

- Fixed the Windows query curve chart being filled with the gray `未记录` color after drawing the legend.
- The chart plot area now explicitly uses a white background and resets the painter brush before drawing the border.
- Improved the curve chart y-axis label layout so labels such as `未记录 y=-0.1` stay outside the plot area.
- Bumped Windows app and installer version to `2.1.1`.

Installer:

- `releases/windows/2.1.1/Triple2EyeProtection-Setup-2.1.1.exe`

## 2.1.0 - 2026-07-06

- Added a fourth query state, `未记录`, for offline/locked/unknown periods.
- Query statistics now show `absolute duration + percentage`, and the four state percentages are adjusted to add up to `100.0%`.
- Kept legacy log values unchanged; old `0.3` records are mapped to `提醒未休息`, which now defaults to display at `y=0.7`.
- Added configurable chart y-values for `使用中`, `提醒未休息`, `休息中`, and `未记录`.
- Added a chart display switch between `时间轴色块` and `曲线图`.
- Added `未记录` to the curve/timeline display with default `y=-0.1`.
- Renamed the query custom range button from `Apply` to `应用`.
- Bumped Windows app and installer version to `2.1.0`.

Installer:

- `releases/windows/2.1.0/Triple2EyeProtection-Setup-2.1.0.exe`

## 2.0.11 - 2026-07-06

- Resized the integrated red `延时` control to `140x40`, matching `开始休息` and `休息好了`.
- Kept the delay minutes editable inside the compact button without using a separate external input box.
- Changed the `已用眼` label color to the same red family as the delay button.
- Bumped app and installer version to `2.0.11`.

Installer:

- `releases/windows/2.0.11/Triple2EyeProtection-Setup-2.0.11.exe`

## 2.0.10 - 2026-07-06

- Moved `已用眼` above `已提醒` in the rest reminder window.
- Replaced the separate delay-minute spin box plus delay button with one integrated red delay button.
- The new delay button embeds the minute value directly inside the button as `延时：xx分钟`, keeping the value editable for the current popup.
- Disabled the delay control after `开始休息`, matching the existing behavior that delay is only available before rest starts.
- Bumped app and installer version to `2.0.10`.

Installer:

- `releases/windows/2.0.10/Triple2EyeProtection-Setup-2.0.10.exe`

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
