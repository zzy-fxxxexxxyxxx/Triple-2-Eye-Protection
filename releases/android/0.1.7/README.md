# Triple 2 Eye Protection Android 0.1.7

Release date: 2026-06-12

## Artifact

- `Triple2EyeProtection-Android-0.1.7-release.apk`

## Changes

- Added a `休息时震动` switch in the Control section.
- Rest reminder vibration is now optional and defaults to off when no previous preference exists.
- The switch is saved immediately when toggled, and the background service reads it before vibrating.
- Bumped Android version to `versionCode 8` / `versionName 0.1.7`.

## Notes

- This APK keeps the same application id and debug signing setup as previous test builds, so it can upgrade compatible earlier test versions directly.
- If Android refuses to install over an older package, uninstall the older debug-signed build first.
