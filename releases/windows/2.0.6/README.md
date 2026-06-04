# Triple 2 Eye Protection Windows 2.0.6

发布时间：2026-06-04

## 安装包

- `Triple2EyeProtection-Setup-2.0.6.exe`

## 版本信息

- 平台：Windows x64 compatible
- 应用版本：`2.0.6`
- 打包方式：PyInstaller onedir + Inno Setup installer

## 更新内容

- 修复开机自启状态识别和写入逻辑。
- 改进安装清理逻辑，安装新版时删除旧 `_internal` 运行时目录。
- 保留此前的单实例启动、托盘倒计时、锁屏/休眠/唤醒事件监听、查询页快捷范围、错误日志增强等能力。

## 安装说明

双击安装包即可安装。若原软件未卸载，安装程序会使用同一应用目录并清理旧运行时文件。
