# Triple 2 Eye Protection Android 0.1.9

Release date: 2026-06-16

## Artifact

- `Triple2EyeProtection-Android-0.1.9-release.apk`

## Changes

- Changed the foreground-service status notification to a new visible notification channel.
- The running service should now show a top status-bar icon more reliably on Huawei/Android systems.
- The status notification remains silent and non-vibrating.
- Bumped Android version to `versionCode 10` / `versionName 0.1.9`.

## Notes

- Android notification channel importance is sticky once created, so this release uses a new channel id for the status notification.
- If the status icon still does not appear, check system notification settings for Triple 2 Eye Protection and allow the `护眼倒计时` notification category.
