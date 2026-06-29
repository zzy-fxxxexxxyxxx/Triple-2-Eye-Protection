# Triple 2 Eye Protection

一个围绕 20-20-20 护眼习惯设计的双端提醒工具：Windows 端负责桌面长期运行、托盘提醒和使用统计；Android 端面向华为 P60 这类非纯血鸿蒙手机，使用原生前台服务来尽量保持后台倒计时可靠。

> 当前维护重点是三个平台：`Triple_2_Eyes_Protection_windows`、`Triple_2_Eyes_Protection_android` 和 `Triple_2_Eyes_Protection_ios`。

## 当前版本

| 平台 | 版本 | 技术栈 | 状态 |
| --- | --- | --- | --- |
| Windows | `2.0.8` | Python 3.10, PyQt6, pywin32, PyInstaller, Inno Setup | 日常可用 |
| Android | `0.1.9` | 原生 Android Java, Gradle | 测试版 |
| iOS | `0.1.0` | SwiftUI, ActivityKit, WidgetKit, Swift Charts | 开发版（GitHub Actions 构建） |

## 功能概览

| 功能 | Windows 端 | Android 端 |
| --- | --- | --- |
| 自定义用眼时长 `t1` | 支持 | 支持 |
| 自定义休息时长 `t2` | 支持 | 支持 |
| 到点休息提醒 | 弹窗、置顶、声音/模式设置 | 全屏提醒页、可选震动、通知 |
| 暂停 / 继续 / 重置 | 支持 | 支持 |
| 立即休息 | 支持 | 支持 |
| 熄屏/锁屏后重置逻辑 | Windows 锁屏/休眠/唤醒事件 + 兼容兜底 | 屏幕关闭/亮屏/解锁监听 |
| 后台入口 | 系统托盘菜单和倒计时 | 常驻通知倒计时、快捷设置开关 |
| 开机自启 | 注册表 Run + StartupApproved 状态修正 | BOOT_COMPLETED 广播恢复服务 |
| 使用记录统计 | 12h / 24h / 7天 / 1个月 / 6个月 / 1年 | 简单完成休息次数统计 |
| 单实例运行 | 支持 | Android 默认单任务入口 |

## 仓库结构

```text
.
├── Triple_2_Eyes_Protection_windows/       # Windows 桌面端主线源码（原 v2）
│   ├── main.pyw
│   ├── main_app.py
│   ├── reminder_window.py
│   ├── usage_query_window.py
│   ├── Triple 2 Eye Protection.spec
│   └── installer/
├── Triple_2_Eyes_Protection_android/       # Android 原生版
│   └── app/src/main/java/com/triple2/eyeprotection/
├── Triple_2_Eyes_Protection_ios/           # iOS 版（SwiftUI）
│   ├── Triple2EyeProtection/               # 主 App
│   │   ├── Models/      AppSettings + UsageStore + EyeCareManager
│   │   ├── Views/       ContentView + RestOverlay + StatsView + AppTheme
│   │   └── Services/    NotificationManager + LiveActivityManager
│   ├── EyeCareWidget/                      # 桌面小组件
│   ├── LiveActivity/                       # 灵动岛
│   └── project.yml                         # XcodeGen 项目定义
├── .github/workflows/ios-build.yml         # iOS CI/CD（GitHub Actions 自动构建 IPA）
├── releases/
└── vision.txt
```

## Windows 端运行

推荐使用 Python 3.10 环境：

```powershell
cd Triple_2_Eyes_Protection_windows
pip install -r requirements.txt
python main.pyw
```

Windows 端会在后台托盘运行。托盘菜单提供倒计时状态、显示设置、暂停/继续、重置、立即休息和退出。

## Windows 端打包

先用 PyInstaller 生成 onedir 目录：

```powershell
cd Triple_2_Eyes_Protection_windows
pyinstaller "Triple 2 Eye Protection.spec" --noconfirm
```

再使用 Inno Setup 生成安装包：

```powershell
powershell -ExecutionPolicy Bypass -File installer\build_installer.ps1
```

打包产物会生成在 `Triple_2_Eyes_Protection_windows/installer_output/`。已确认发布的 Windows 安装包会按版本归档到 `releases/windows/`。

## Android 端运行与打包

Android 端是原生 Java 工程，不依赖 Flutter。首次构建前需要在 `Triple_2_Eyes_Protection_android/local.properties` 写入本机 Android SDK 路径：

```properties
sdk.dir=C:\\path\\to\\Android\\Sdk
```

构建 release APK：

```powershell
cd Triple_2_Eyes_Protection_android
.\gradlew.bat assembleRelease
```

APK 会生成在：

```text
Triple_2_Eyes_Protection_android/app/build/outputs/apk/release/
```

当前 `release` 变体仍使用 debug 签名，适合个人测试。正式分发前应改为独立 release keystore，并把签名配置放到本地未提交文件中。

已归档的 Android 测试 APK 放在 `releases/android/`。每次发布新版 APK 时，需要递增 `versionCode` / `versionName`，并新增对应版本目录和说明。

## iOS 端构建与安装

iOS 项目无需 Mac 即可构建：推送代码后，GitHub Actions 自动使用 macOS runner 编译，生成 IPA 供下载。

### 自动构建

推送 `Triple_2_Eyes_Protection_ios/` 下的任何改动到 main 分支即触发构建。也可以手动触发：

> GitHub → Actions → Build iOS IPA → Run workflow

构建约 10 分钟，完成后在 Actions 页面的 Artifacts 下载 `Triple2EyeProtection-IPA`。

### 安装到 iPhone

使用 [AltStore](https://altstore.io) 或 [SideStore](https://sidestore.io) 将下载的 IPA 安装到 iPhone。

- 免费 Apple ID：签名有效期 7 天，AltStore 同 WiFi 下自动续签
- 付费 Apple Developer：在仓库 Secrets 中配置证书后可永久签名

### iOS 特有功能

| 功能 | 说明 |
| --- | --- |
| 灵动岛 (Dynamic Island) | Live Activity 实时显示倒计时，支持 compact/expanded/minimal 三种形态 |
| 桌面小组件 (Widget) | 5 种尺寸：small / medium / inline / circular / rectangular |
| 休息曲线图表 | 30 天柱状图（Swift Charts），Android/Windows 版尚未实现 |

### 技术栈

Swift 5.9 · SwiftUI · ActivityKit · WidgetKit · Swift Charts · XcodeGen · GitHub Actions (macos-14)

iOS 部署目标：17.0 ｜ 灵动岛需 iPhone 14 Pro+ ｜ Lock Screen Live Activity 适用于所有 iOS 17+ 设备

## 华为手机保活建议

Android 无法保证应用在所有系统策略下永久后台存活。华为 P60 上建议安装后完成这些设置：

- 允许通知权限
- 允许忽略电池优化
- 允许精确闹钟权限
- 允许悬浮窗/显示在其他应用上层
- 在应用启动管理中开启自启动、关联启动、后台活动
- 在多任务界面锁定应用

如果用户手动强行停止应用，系统通常不会允许它自动恢复。

## 设计原则

- 不把运行日志、PyInstaller/Gradle 构建目录提交到源码仓库
- Android APK 会按版本归档到 `releases/android/`
- Windows 安装包会按版本归档到 `releases/windows/`
- Windows 端优先稳定托盘常驻、单实例、错误日志和可诊断性
- Android 端优先使用系统认可的前台服务、通知、闹钟和开机广播路线
- 每次发布递增版本号，避免覆盖安装和问题定位混乱

## 隐私说明

应用不需要联网。使用记录保存在本机/手机本地，用于统计护眼状态，不会上传到服务器。
