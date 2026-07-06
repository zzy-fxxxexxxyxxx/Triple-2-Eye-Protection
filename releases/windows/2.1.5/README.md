# Triple 2 Eye Protection Windows 2.1.5

Release date: 2026-07-06

## Artifact

- `Triple2EyeProtection-Setup-2.1.5.exe`
- SHA256: `7925797CE01B9B11B98C776DE2ABC18D3CB979E731F9C9E5F0B05B349C64C677`

## Changes

- Reworked curve chart time-axis labels so the first and last labels stay inside the chart width.
- Removed the extra-looking bottom border below time labels by separating the data plot area from the x-axis label area.
- Reduced the vertical gap below time labels while keeping a safe bottom margin inside the chart widget.
- Added width checks for curve chart time labels at common query window sizes.
- Bumped Windows app and installer version to `2.1.5`.

## Notes

- This release only changes Windows query chart rendering and layout. Existing `usage_logs/*.txt` files remain compatible and are not rewritten.
- Older installers remain archived in their existing `releases/windows/*` folders.
