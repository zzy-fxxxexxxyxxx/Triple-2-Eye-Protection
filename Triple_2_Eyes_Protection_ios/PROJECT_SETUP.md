# Triple 2 Eye Protection — iOS Version

## Port Summary
This is a direct port of the Android (Java) eye-care app to iOS (Swift/SwiftUI),
with two iOS-only additions: Dynamic Island (Live Activity) and Home Screen Widget.

| Android Component          | iOS Equivalent                        |
|----------------------------|---------------------------------------|
| MainActivity.java          | ContentView.swift                     |
| EyeCareService.java        | EyeCareManager.swift (ObservableObject)|
| AppPrefs.java              | AppSettings.swift (UserDefaults)      |
| UsageStore.java            | UsageStore.swift (UserDefaults)       |
| AlarmReceiver.java         | UNNotification scheduling             |
| BootReceiver.java          | App.init() + scene phase              |
| RestActivity.java          | RestOverlayView.swift                 |
| EyeCareTileService.java    | LiveActivityManager.swift             |
| status notification        | Widget + Live Activity                |

---

## 方法一：GitHub Actions 自动构建（无需 Mac）

### 1. 触发构建

Workflow 文件位于仓库根目录 `.github/workflows/ios-build.yml`，GitHub 会自动识别。

- **自动触发**: 推送 `Triple_2_Eyes_Protection_ios/` 下的改动到 main 分支时自动构建
- **手动触发**: GitHub → Actions → Build iOS IPA → Run workflow

### 2. 下载 IPA
构建完成后（约 8-12 分钟），在 Actions 页面的 Artifacts 区域下载 `Triple2EyeProtection-IPA.zip`，解压得到 `.ipa` 文件。

### 3. 安装到 iPhone（Sideload）

#### 方案 A：AltStore（推荐，免费）
1. 在 iPhone 上安装 [AltStore](https://altstore.io)（需要电脑端 AltServer 配合）
2. 将下载的 IPA 文件 AirDrop/传送到 iPhone
3. 用 AltStore 打开 IPA → 输入你的 Apple ID → 签名并安装
4. **限制**：免费 Apple ID 签名有效期 7 天，AltStore 会在同一 WiFi 下自动续签

#### 方案 B：SideStore（完全脱离电脑）
1. 安装 [SideStore](https://sidestore.io)
2. 配置后可直接在手机上签名安装 IPA
3. 同样 7 天限制，但无需电脑续签

#### 方案 C：TrollStore（仅限 iOS 15.0-17.0 特定版本）
如果你的 iPhone 系统版本在支持范围内，[TrollStore](https://github.com/opa334/TrollStore) 可以永久签名，不受 7 天限制。

#### 方案 D：付费 Apple Developer（$99/年）
如果需要永久签名 + 灵动岛推送功能，需要付费开发者账号。配置好证书后，GitHub Actions 可以构建完整签名的 IPA。

### 4. 设置签名（可选，付费账号）
在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 |
|---|---|
| `APPLE_CERTIFICATE_BASE64` | Apple Distribution 证书的 Base64 |
| `APPLE_CERTIFICATE_PASSWORD` | 证书密码 |
| `PROVISIONING_PROFILE_BASE64` | Provisioning Profile 的 Base64 |
| `KEYCHAIN_PASSWORD` | 临时 Keychain 密码（任意设） |
| `DEVELOPMENT_TEAM` | Apple Developer Team ID |

然后在 Actions 中选择 `build-type: signed`。

---

## 方法二：有 Mac 时本地构建

### Requirements
- Xcode 15+
- iOS 16.0+ deployment target

### Build with XcodeGen
```bash
brew install xcodegen
cd Triple_2_Eyes_Protection_ios
xcodegen generate
open Triple2EyeProtection.xcodeproj
# Cmd+R to build and run
```

---

## Architecture Notes

- **No persistent background service**: iOS does not allow indefinite background execution.
  Instead, the app schedules local notifications and uses Live Activity to show the
  countdown in the Dynamic Island / Lock Screen. When the app is in the foreground,
  a Timer drives per-second UI updates.

- **ScenePhase replaces screen on/off**: iOS uses `scenePhase` transitions
  (`.active` / `.inactive` / `.background`) to detect user presence, similar to
  Android's `ACTION_SCREEN_ON` / `ACTION_SCREEN_OFF`.

- **Usage storage**: Uses the same compact `timestamp,type;timestamp,type` CSV-in-UserDefaults
  format as the Android `UsageStore.java`, keeping the data lightweight and easily
  shareable with the Widget via App Groups.

- **App Groups**: `group.com.triple2.eyeprotection` is used to share UserDefaults
  between the main app and the Widget extension.

## New iOS Features

1. **Dynamic Island (灵动岛)** — Live Activity shows countdown in the Dynamic Island
   with compact (icon + timer), expanded (full status), and minimal presentations.

2. **Home Screen Widget (桌面组件)** — Widget shows current countdown and today's
   rest count. Supports small, medium, inline, circular, and rectangular families.

3. **Rest Curve Chart (使用曲线)** — 30-day bar chart of daily rest counts using
   Swift Charts (iOS 16+), a feature not yet present in the Android version.

## Limitation Notes (vs Android)

- iOS does not allow persistent background services like Android's foreground service.
  Notifications take over when the app is backgrounded.
- Full-screen lock-screen overlay is replaced by a native SwiftUI fullScreenCover.
- Dynamic Island requires iPhone 14 Pro or later. Lock Screen Live Activity works on
  all iOS 16+ devices.
- Unsigned IPA needs sideloading (AltStore etc.) and re-signs every 7 days.
