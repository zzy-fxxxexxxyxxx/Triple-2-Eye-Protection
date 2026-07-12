# Windows 2.1.7 主界面高 DPI 自适应重构

## 背景

Windows 2.1.6 将主窗口改成了渐变头部和卡片式控制面板，但存在两个明显问题：

- 渐变、大圆角、彩色卡片和强调按钮叠加后，视觉上偏厚重，带有较强的塑料感，不符合常驻桌面工具应有的克制风格。
- 主窗口固定为 `430x740`。华为 MateBook 14 在 Windows 250% 缩放下，逻辑可用高度通常只有约 500 像素，窗口底部操作区会超出屏幕。

本次重构只修改 Windows 主窗口的布局和样式，不改变计时、暂停、重置、延时、立即休息、查询记录、托盘运行和退出逻辑。

## 实现思路

主窗口改为紧凑的桌面工具布局：

- 使用白色标题栏、浅灰窗口背景、细分隔线和小圆角，取消渐变头部和大面积卡片。
- 将当前状态放在内容区顶部，用低饱和绿色背景和 4px 进度条表达状态。
- 参数区继续使用双列网格，但进一步压缩字段高度和间距。
- 七个快捷操作改为三列、三行的稳定网格，减少纵向占用。
- 根据当前屏幕的可用逻辑分辨率计算窗口尺寸，并保留纵向滚动兜底。

## 自适应策略

主窗口不再调用 `setFixedSize()`，而是读取 `QScreen.availableGeometry()`：

- 目标宽度限制在 `320~420px`。
- 目标高度限制在 `380~560px`，并从可用屏幕高度中预留 `56px` 给系统窗口边框和安全空间。
- 常规 MateBook 14 250% 缩放场景下，窗口约为 `420x496~520`。
- 高度小于约 `488px` 时，纵向滚动条才会按需出现。
- 水平滚动始终关闭，避免表单左右晃动。

## 修改内容

- `EyeCarePro.apply_main_window_style()`
  - 移除渐变、大圆角和高饱和按钮。
  - 改用白灰底、细边框、`4~6px` 小圆角和低饱和状态色。
  - 将倒计时进度条压缩为 4px 的状态线。
  - 增加窄型纵向滚动条样式。

- `EyeCarePro.create_section()`
  - 用无边框分区替代卡片容器。
  - 分区只保留标题和紧凑间距。

- `EyeCarePro.init_ui()`
  - 根据屏幕可用尺寸动态调整主窗口。
  - 新增 `QScrollArea` 作为小屏兜底。
  - 将标题栏、状态区、参数区和操作区重新排序。
  - 将七个操作按钮压缩为三列网格。

- `EyeCarePro.update_countdown_display()`
  - 倒计时文本改为单独显示 `MM:SS`，由界面中的“下次提醒”标签提供语义。

## 涉及文件

- `Triple_2_Eyes_Protection_windows/main_app.py`
- `Triple_2_Eyes_Protection_windows/main.pyw`
- `Triple_2_Eyes_Protection_windows/installer/Triple2EyeProtection.iss`
- `README.md`
- `releases/windows/CHANGELOG.md`
- `docs/windows-2.1.7-main-window-high-dpi-redesign.md`
- `releases/windows/2.1.7/README.md`

## 验证

- 使用 `python -m py_compile` 编译 Windows 端 Python 源文件。
- 使用 `QT_SCALE_FACTOR=2.5` 和 PyQt6 offscreen 检查：
  - `420x520`：无滚动、无文字溢出。
  - `400x500`：无滚动、无文字溢出。
  - `420x496`：无滚动，可完整显示主面板。
  - `360x420`：仅出现纵向滚动兜底，无水平滚动和文字溢出。
- 使用 PyInstaller 重新构建 Windows onedir 程序。
- 使用 Inno Setup 生成 `Triple2EyeProtection-Setup-2.1.7.exe`。
