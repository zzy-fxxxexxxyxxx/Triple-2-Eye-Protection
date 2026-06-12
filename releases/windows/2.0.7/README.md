# Triple 2 Eye Protection Windows 2.0.7

Release date: 2026-06-12

## Artifact

- `Triple2EyeProtection-Setup-2.0.7.exe`

## Changes

- Added a configurable rest reminder fade-in duration to the main control panel.
- The fade duration supports decimal seconds, so millisecond-level values such as `0.300` or `1.250` can be used.
- The rest reminder window now uses a linear opacity transition instead of appearing suddenly.
- Bumped Windows app and installer version to `2.0.7`.

## Notes

- The installer keeps the same application identity, so it can install over the previous Windows version.
- The PyInstaller package no longer includes old runtime usage logs.
