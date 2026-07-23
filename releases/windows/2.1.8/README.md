# Triple 2 Eye Protection Windows 2.1.8

Release date: 2026-07-23

## Artifact

- `Triple2EyeProtection-Setup-2.1.8.exe`
- SHA256: `8245E2E6FC7143B2BB1F68A54B81A3C9C666AD84033777CB5DE004065DE210F9`

## Changes

- Replaced the single reminder-popup delay control with three red delay buttons in the first button row.
- The three delay buttons default to the main default delay value, `20` minutes, and `30` minutes, so the default configuration shows `10/20/30`.
- Each delay value remains editable inside its own button and only affects the current reminder popup.
- Clicking any delay button still closes the popup, continues the same eye-use session, and keeps accumulated `已用眼` time.
- `已提醒`, `已用眼`, `开始休息`, `休息好了`, fade-in behavior, and usage log compatibility remain unchanged.
- Bumped Windows app and installer version to `2.1.8`.

## Notes

- Existing settings and usage logs remain compatible and are not rewritten.
- Older installers remain archived in their existing `releases/windows/*` folders.
