# Windows Installer Changelog

## 2.0.6 - 2026-06-04

- 修复 Windows 开机自启状态判断：正确识别 `StartupApproved` 中的启用/禁用状态。
- 保留 `Run` 注册表自启入口，并修正启用时写入 `0x02`、禁用时写入 `0x03`。
- 继续使用精简后的 PyInstaller 打包配置，减少无关 Qt 模块和冲突 DLL。
- 安装时清理旧版 `_internal` 目录，避免旧 DLL 干扰新版运行。

Installer:

- `releases/windows/2.0.6/Triple2EyeProtection-Setup-2.0.6.exe`
