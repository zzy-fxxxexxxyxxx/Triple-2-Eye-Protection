# Triple 2 Eye Protection Windows 2.1.7

Release date: 2026-07-12

## Artifact

- `Triple2EyeProtection-Setup-2.1.7.exe`
- SHA256: `7916C7ADE1F33F7D7B00ABECC1DC3CE1D0DC75E72D7EAB74AE790A75AE8E1C54`

## Changes

- Replaced the glossy gradient/card-heavy main window with a restrained flat desktop-tool layout.
- Made the main window responsive to the current screen's available logical resolution instead of using a fixed `430x740` size.
- Kept the complete panel visible at `420x496` and larger, covering MateBook 14 at 250% Windows scaling.
- Added an internal vertical scroll fallback for smaller logical screens without horizontal scrolling.
- Compressed the seven main actions into a stable three-row grid while preserving all existing behavior.
- Bumped Windows app and installer version to `2.1.7`.

## Notes

- Existing settings and usage logs remain compatible and are not rewritten.
- Older installers remain archived in their existing `releases/windows/*` folders.
