# Triple 2 Eye Protection

围绕 20-20-20 护眼法则设计的三端提醒工具：Windows 桌面托盘常驻 + Android 前台服务 + iOS 灵动岛/通知，帮助你在长时间用眼时定时休息远望。

> 当前维护：`Triple_2_Eyes_Protection_windows` · `Triple_2_Eyes_Protection_android` · `Triple_2_Eyes_Protection_ios`

## 当前版本

| 平台 | 版本 | 技术栈 | 构建方式 |
| --- | --- | --- | --- |
| Windows | `2.1.2` | Python 3.10 · PyQt6 · pywin32 · PyInstaller · Inno Setup | 本地 PyInstaller |
| Android | `0.1.9` | Java · Android SDK · Gradle | 本地 Gradle |
| iOS | `0.1.0` | Swift 5.9 · SwiftUI · ActivityKit · WidgetKit · Swift Charts | GitHub Actions (macOS runner) |

## 功能概览

| 功能 | Windows | Android | iOS |
| --- | --- | --- | --- |
| 自定义用眼时长 | 支持 (1–300 min) | 支持 | 支持 |
| 自定义休息时长 | 支持 (5–6000 s) | 支持 | 支持 |
| 可配置淡入动画 | 支持 (0–10 s) | 支持 (0–10 s) | 支持 (0–10 s) |
| 到点休息提醒 | 弹窗 + 声音/闪烁/置顶 | 全屏覆盖层 + 通知 + 可选震动 | 全屏覆盖层 + 通知 + 可选震动 |
| 暂停 / 继续 / 重置 | 支持 | 支持 | 支持 |
| 立即休息 | 支持 | 支持 | 支持 |
| 延时调整 | 支持（主界面默认延时、弹窗本次延时、正负秒数调整） | — | — |
| 熄屏/锁屏感知 | 锁屏/休眠/唤醒事件 + 兼容兜底 | 屏幕关闭/亮屏监听 | ScenePhase 前后台切换 |
| 息屏达标自动重置 | 支持 | 支持 | 支持 |
| 后台运行 | 系统托盘 | 前台服务常驻通知 | Live Activity + 本地通知 |
| 开机自启 | 注册表 Run + StartupApproved | BOOT_COMPLETED 广播 | scenePhase 自动恢复 |
| 快捷开关 | 托盘菜单 | 快捷设置 Tile | 灵动岛 + 桌面小组件 |
| 使用记录统计 | 12h / 24h / 7天 / 1个月 / 6个月 / 1年 + 时长占比 + 未记录 | 12h / 24h / 7天 / 1个月 / 6个月 / 1年 | 12h / 24h / 7天 / 1个月 / 6个月 / 1年 |
| 状态图表 | 曲线图 / 时间轴色块 + 可配置 y 值 | — | 30 天柱状图 (Swift Charts) |
| 灵动岛实时倒计时 | — | — | 支持 (compact / expanded / minimal) |
| 桌面小组件 | — | — | 5 种尺寸 (S / M / inline / circular / rectangular) |
| 华为保活指南 | — | 内置设置入口 | — |
| iOS 保活指南 | — | — | 内置设置入口 |
| 单实例运行 | 支持 | 默认 | 默认 |

## 仓库结构

```text
.
├── Triple_2_Eyes_Protection_windows/       # Windows 桌面端
│   ├── main.pyw                            入口 · 单实例 · 错误日志
│   ├── main_app.py                         主窗口 · 托盘 · 计时 · 锁屏/休眠
│   ├── reminder_window.py                  休息提醒窗口
│   ├── usage_query_window.py               使用记录查询页
│   ├── Triple 2 Eye Protection.spec        PyInstaller 打包配置
│   └── installer/                          Inno Setup 安装包脚本
│
├── Triple_2_Eyes_Protection_android/       # Android 端
│   └── app/src/main/java/com/triple2/eyeprotection/
│       ├── EyeCareService.java             前台服务 · 倒计时 · 闹钟 · 屏幕事件
│       ├── MainActivity.java               主界面 · 保活设置入口
│       ├── RestActivity.java               休息提醒全屏页
│       ├── EyeCareTileService.java         快捷设置开关
│       ├── AppPrefs.java                   配置存储
│       ├── UsageStore.java                 使用记录
│       ├── AlarmReceiver.java              闹钟广播
│       ├── BootReceiver.java               开机广播
│       └── UiFeedback.java                 按钮反馈
│
├── Triple_2_Eyes_Protection_ios/           # iOS 端
│   ├── Triple2EyeProtection/               主 App
│   │   ├── Models/                         数据层
│   │   │   ├── AppSettings.swift           UserDefaults 配置
│   │   │   ├── UsageStore.swift            使用记录
│   │   │   └── EyeCareManager.swift        核心状态机
│   │   ├── Views/                          UI 层
│   │   │   ├── ContentView.swift           主界面
│   │   │   ├── RestOverlayView.swift       全屏休息覆盖层
│   │   │   ├── StatsView.swift             30 天图表 + 统计
│   │   │   └── AppTheme.swift              绿色主题 + 按钮样式
│   │   └── Services/                       服务层
│   │       ├── NotificationManager.swift   本地通知
│   │       └── LiveActivityManager.swift   灵动岛管理
│   ├── EyeCareWidget/                      桌面小组件
│   │   ├── EyeCareWidget.swift             5 种尺寸小组件
│   │   └── EyeCareWidgetBundle.swift       入口
│   ├── LiveActivity/                       灵动岛
│   │   └── EyeCareLiveActivity.swift       UI 配置 (compact/expanded/minimal)
│   ├── project.yml                         XcodeGen 项目定义
│   ├── ExportOptions.plist                 IPA 导出配置
│   └── PROJECT_SETUP.md                    详细构建文档
│
├── .github/workflows/ios-build.yml         # iOS CI/CD（自动构建 IPA）
├── releases/                               # 已归档安装包
└── vision.txt                              # 原始需求与设计记录
```

---

## Windows 端

### 运行

```powershell
cd Triple_2_Eyes_Protection_windows
pip install -r requirements.txt
python main.pyw
```

程序在后台托盘运行，托盘菜单提供倒计时状态、暂停/继续、重置、立即休息、退出。

### 打包

```powershell
cd Triple_2_Eyes_Protection_windows
pyinstaller "Triple 2 Eye Protection.spec" --noconfirm
powershell -ExecutionPolicy Bypass -File installer\build_installer.ps1
```

产物生成在 `installer_output/`，正式发布版归档到 `releases/windows/`。

---

## Android 端

首次构建需在 `Triple_2_Eyes_Protection_android/local.properties` 写入 SDK 路径：

```properties
sdk.dir=C:\\path\\to\\Android\\Sdk
```

```powershell
cd Triple_2_Eyes_Protection_android
.\gradlew.bat assembleRelease
```

APK 生成在 `app/build/outputs/apk/release/`。当前 release 使用 debug 签名，适合个人测试。正式分发前应配置独立 keystore。

### 华为手机保活

- 允许通知 · 忽略电池优化 · 允许精确闹钟 · 允许悬浮窗
- 应用启动管理：开启自启动 · 关联启动 · 后台活动
- 多任务界面锁定应用

---

## iOS 端

无需 Mac 即可构建：GitHub Actions 自动编译，生成 IPA 后通过 AltStore 安装。

### 触发构建

推送 `Triple_2_Eyes_Protection_ios/` 下的改动即自动触发，也可手动：

> GitHub → Actions → **Build iOS IPA** → Run workflow

约 10 分钟，完成后在 Artifacts 下载 `Triple2EyeProtection-IPA`。

### 安装到 iPhone

使用 [AltStore](https://altstore.io) 或 [SideStore](https://sidestore.io) 安装 IPA。

| 账号类型 | 签名有效期 | 续签方式 |
| --- | --- | --- |
| 免费 Apple ID | 7 天 | AltStore 同 WiFi 自动续签 |
| 付费 Developer ($99/年) | 1 年 | GitHub Actions 完整签名 |

### 技术栈

**Swift 5.9 · SwiftUI · ActivityKit · WidgetKit · Swift Charts · XcodeGen · GitHub Actions (macos-14)**

部署目标 iOS 17.0 ｜ 灵动岛需 iPhone 14 Pro+ ｜ Lock Screen Live Activity 适用于所有 iOS 17+ 设备

---

## 设计原则

- 构建产物不入库（PyInstaller / Gradle / Xcode build）
- 各平台安装包按版本归档到 `releases/`
- Windows 优先托盘常驻、单实例、错误日志可诊断
- Android 优先系统认可的前台服务、通知、闹钟、开机广播路线
- iOS 优先 Live Activity + 本地通知，适应 iOS 后台约束
- 每次发布递增版本号

## 实现文档

- [Windows 2.1.2 查询页图表绘制修复](docs/windows-2.1.2-usage-query-chart-polish.md)
- [Windows 2.1.1 查询页曲线图灰底修复](docs/windows-2.1.1-usage-query-chart-fix.md)
- [Windows 2.1.0 查询页统计与状态图表](docs/windows-2.1.0-usage-query.md)
- [Windows 2.0.11 提醒弹窗 UI 收口](docs/windows-2.0.11-reminder-ui.md)

## 隐私说明

应用不需要联网。使用记录保存在本机本地，不会上传到服务器。
