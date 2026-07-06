# Triple 2 Eye Protection Windows 2.1.3

Release date: 2026-07-06

## Artifact

- `Triple2EyeProtection-Setup-2.1.3.exe`
- SHA256: `374A90ED8EDBFA5C0ED17664311D1EDEFBBD7BD1851D3AE3A420A2655355089B`

## Changes

- Moved curve chart time ticks into an internal bottom band so they no longer overflow the `状态曲线` area.
- Reduced the chart widget minimum height to avoid the default query window being forced beyond its visible bounds.
- Added markers for both segment start and segment end points.
- Added markers for raw log record points, including same-second state changes that do not create visible duration segments.
- Bumped Windows app and installer version to `2.1.3`.

## Notes

- This release only changes Windows query chart rendering. Existing `usage_logs/*.txt` files remain compatible and are not rewritten.
- Older installers remain archived in their existing `releases/windows/*` folders.
