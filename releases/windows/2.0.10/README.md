# Triple 2 Eye Protection Windows 2.0.10

Release date: 2026-07-06

## Artifact

- `Triple2EyeProtection-Setup-2.0.10.exe`
- SHA256: `84A35FCD468D0DECE35DC311676537E732A26D9E4561416862E8EBF79B90D02A`

## Changes

- Moved `已用眼` above `已提醒` in the rest reminder window.
- Reworked the popup delay control from two separate widgets into one red integrated button.
- The delay button now displays `延时：xx分钟` with the editable minute value embedded inside the button, avoiding the disconnected external input box.
- The embedded value remains a one-time popup value and does not change the main screen's `默认延时 (min)` setting.
- The delay button is disabled once `开始休息` is clicked, while `已提醒` continues and `已用眼` stays frozen.
- Bumped Windows app and installer version to `2.0.10`.

## Notes

- The installer keeps the same application identity, so it can install over the previous Windows version.
- Older installers remain archived in their existing `releases/windows/*` folders.
