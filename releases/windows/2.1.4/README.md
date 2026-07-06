# Triple 2 Eye Protection Windows 2.1.4

Release date: 2026-07-06

## Artifact

- `Triple2EyeProtection-Setup-2.1.4.exe`
- SHA256: `301A7A21974618F23B5058791A6896428A56A50AFBFF89A039FB23DC47A066E1`

## Changes

- Added explicit bottom padding inside the `状态曲线` group so the chart widget no longer visually covers the group border in full screen.
- Kept curve chart time ticks inside the white plot area with a larger internal bottom safety band.
- Reduced the plot widget minimum height to fit the default query window while preserving full-screen expansion.
- Added full-screen geometry and curve-rendering checks for the query chart.
- Bumped Windows app and installer version to `2.1.4`.

## Notes

- This release only changes Windows query chart layout and rendering. Existing `usage_logs/*.txt` files remain compatible and are not rewritten.
- Older installers remain archived in their existing `releases/windows/*` folders.
