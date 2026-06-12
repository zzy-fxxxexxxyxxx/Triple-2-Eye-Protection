# Triple 2 Eye Protection Android 0.1.6

Release date: 2026-06-12

## Artifact

- `Triple2EyeProtection-Android-0.1.6-release.apk`

## Changes

- Added a configurable rest reminder fade-in duration in the Control section.
- The fade duration supports decimal seconds, so millisecond-level values such as `0.300` or `1.250` can be used.
- Applied the same linear fade-in to both the foreground rest page and the overlay reminder shown above other apps.
- Bumped Android version to `versionCode 7` / `versionName 0.1.6`.

## Notes

- This APK keeps the same application id and debug signing setup as previous test builds, so it can upgrade compatible earlier test versions directly.
- If Android refuses to install over an older package, uninstall the older debug-signed build first.
