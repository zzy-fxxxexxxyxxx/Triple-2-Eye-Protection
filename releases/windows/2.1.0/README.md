# Triple 2 Eye Protection Windows 2.1.0

Release date: 2026-07-06

## Artifact

- `Triple2EyeProtection-Setup-2.1.0.exe`
- SHA256: `A864AF78704C559CA7B68BEA34BE1B7CA7B5F6AF9DE08BBC28897393D0D478F9`

## Changes

- Added `未记录` to the usage query statistics and chart display.
- Statistics now show both absolute duration and percentage, for example `03:01:49 (25.3%)`.
- Percentages for `使用中`, `提醒未休息`, `休息中`, and `未记录` are adjusted to add up to `100.0%`.
- Kept historical log files unchanged. Legacy `0.3` records are interpreted as `提醒未休息`, while the chart now displays that state at configurable `y=0.7` by default.
- Added chart settings for each state's y-value:
  - `使用中`: `1.0`
  - `提醒未休息`: `0.7`
  - `休息中`: `0.0`
  - `未记录`: `-0.1`
- Added a display mode switch between `时间轴色块` and `曲线图`.
- Renamed the custom range button from `Apply` to `应用`.
- Bumped Windows app and installer version to `2.1.0`.

## Notes

- The installer keeps the same application identity, so it can install over the previous Windows version.
- Older installers remain archived in their existing `releases/windows/*` folders.
