# Triple 2 Eye Protection Windows 2.0.9

Release date: 2026-07-05

## Artifact

- `Triple2EyeProtection-Setup-2.0.9.exe`
- SHA256: `8EEC29656F57778002E6BE4BE1CF741A3A69A1A9DBE74065F1A9E985D1154CCC`

## Changes

- Added `默认延时 (min)` to the main settings window. The default value is `10`.
- Added `已用眼` to the rest reminder window. It tracks total eye-use time since the previous completed rest.
- Added a per-popup `延时：xx分钟` action. The value starts from the main default delay and can be changed inside the popup for that one delay only.
- Delaying a reminder closes the popup and continues the same eye-use session, so the next popup keeps the accumulated `已用眼` time.
- `已提醒` is counted per popup. It resets on each new reminder and continues after `开始休息`.
- After `开始休息`, `已用眼` freezes while the rest reminder remains open.
- Bumped Windows app and installer version to `2.0.9`.

## Notes

- The installer keeps the same application identity, so it can install over the previous Windows version.
- Older installers remain archived in their existing `releases/windows/*` folders.
