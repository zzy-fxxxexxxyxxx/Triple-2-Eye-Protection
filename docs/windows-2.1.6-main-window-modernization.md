# Windows 2.1.6 主界面现代化改造

## 背景

旧版 Windows 主界面使用系统默认控件纵向堆叠，功能完整但视觉层级较弱：参数、状态和操作按钮都处在同一个平面里，整体像传统表单，不够现代，也不利于快速识别当前计时状态。

本次改造只调整主窗口 UI 表现和状态展示，不改变护眼计时、提醒弹窗、延时、锁屏检测、托盘运行、使用记录等核心逻辑。

## 实现思路

主界面改为轻量控制台结构：

- 顶部品牌区：使用渐变背景、应用图标和产品标题建立第一视觉信号。
- 参数配置区：使用双列紧凑参数网格，减少纵向堆叠带来的朴素感和空间浪费。
- 当前状态区：合并倒计时、进度条和快捷操作，让用户打开窗口后先看到状态，再执行操作。
- 操作按钮：区分主操作、警示操作、柔和操作和危险操作，增强按钮的语义层级。

## 修改内容

- `EyeCarePro.apply_main_window_style()`
  - 新增主窗口 QSS 主题。
  - 统一窗口背景、卡片、输入框、复选框、进度条、按钮、状态徽标等样式。
  - 使用青绿色作为主色，同时加入蓝色进度和黄色警示按钮，避免单一配色。

- `EyeCarePro.init_ui()`
  - 将窗口尺寸调整为 `430x740`。
  - 新增渐变品牌头部。
  - 将参数配置改为双列网格：用眼时长、默认延时、远望时长、过渡时间。
  - 将提醒方式和开机自启动保留在参数卡片中。
  - 将当前状态、倒计时进度条、快捷操作合并为一个控制面板。

- 状态展示
  - 新增 `update_countdown_display()`，集中更新倒计时文本和进度条。
  - 新增 `set_status_visual_state()`，根据状态颜色同步状态徽标。
  - 新增 `restore_running_status()`，用于临时状态提示后恢复默认运行状态。

- 操作按钮
  - 新增 `get_standard_icon()` 和 `create_action_button()`，为按钮补充 Qt 系统图标。
  - 新增 `update_pause_button_visual()`，暂停/继续按钮会同步切换文字和图标。

## 涉及文件

- `Triple_2_Eyes_Protection_windows/main_app.py`
- `Triple_2_Eyes_Protection_windows/main.pyw`
- `Triple_2_Eyes_Protection_windows/installer/Triple2EyeProtection.iss`
- `README.md`
- `releases/windows/CHANGELOG.md`
- `docs/windows-2.1.6-main-window-modernization.md`
- `releases/windows/2.1.6/README.md`

## 验证

- 使用 `python -m py_compile` 编译 Windows 端 Python 源文件。
- 使用 PyQt6 offscreen 实例化主窗口并检查：
  - 所有关键控件宽高大于 0。
  - 控件没有越出主窗口边界。
  - 主要标签和按钮文字没有超出控件宽度。
  - 暂停/继续按钮文字和图标切换无运行时报错。
- 使用 PyInstaller 重新构建 Windows onedir 程序。
- 使用 Inno Setup 生成 `Triple2EyeProtection-Setup-2.1.6.exe`。