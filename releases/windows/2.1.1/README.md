# Triple 2 Eye Protection Windows 2.1.1

Release date: 2026-07-06

## Artifact

- `Triple2EyeProtection-Setup-2.1.1.exe`
- SHA256: `FEA7C4C2481CFE9E2E9C6F5215B267FF5043921D126823BC8C61523C5EFA2786`

## Changes

- Fixed the Windows query curve chart plot area being filled with the gray `未记录` color.
- Confirmed the existing log format remains compatible:
  - `1` -> `使用中`
  - `0.3` -> `提醒未休息`
  - `0` -> `休息中`
  - `-1` -> `未记录`
- The plot area now explicitly uses a white background and resets the painter brush before drawing the border.
- Improved y-axis label layout so labels such as `未记录 y=-0.1` stay outside the plot area.
- Bumped Windows app and installer version to `2.1.1`.

## Notes

- This is a Windows query chart rendering fix. It does not rewrite or migrate existing `usage_logs/*.txt` files.
- Older installers remain archived in their existing `releases/windows/*` folders.
