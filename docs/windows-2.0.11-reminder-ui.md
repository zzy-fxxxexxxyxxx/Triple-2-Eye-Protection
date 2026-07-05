# Windows 2.0.11 提醒弹窗 UI 收口

## 背景

Windows 2.0.10 已经把弹窗中的延时输入合并进红色按钮，但按钮尺寸仍大于 `开始休息` 和 `休息好了`，视觉重心不够统一。同时，`已用眼` 的颜色仍然使用橙色，与红色延时按钮的警示语义不一致。

## 实现思路

- 保留 2.0.10 的一体化延时控件，不退回到独立输入框。
- 将延时控件固定为 `140x40`，与 `开始休息` 和 `休息好了` 的尺寸完全一致。
- 收紧按钮内部布局：缩小左右边距、字体和数字编辑区宽度，让 `延时：xx分钟` 在 140 像素宽度内保持整体感。
- 继续隐藏 `QSpinBox` 的上下箭头，让分钟值看起来嵌在按钮文案中，而不是独立表单控件。
- 将 `已用眼` 的强调色改为延时按钮同色系红色 `#D64545`，让“用眼过久”和“延时继续用眼”的警示关系更一致。

## 修改内容

- `InlineDelayButton`
  - 尺寸从 `240x54` 调整为 `140x40`。
  - 内边距从 `24/20` 缩小为 `8/8`。
  - `延时：`、分钟数字、`分钟` 三段文本压缩为紧凑布局。
  - 数字编辑区宽度从 `70` 缩小为 `42`。
  - 标签字体从 `17px` 调整为 `14px`，数字字体从 `18px` 调整为 `15px`。

- `ReminderWindow`
  - `已用眼` 标签颜色从 `#C65F22` 改为 `#D64545`。
  - 保持 `已用眼` 位于 `已提醒` 上方。
  - 保持 `开始休息` 后禁用延时控件的行为。

- 发布资料
  - Windows 版本号递增到 `2.0.11`。
  - 更新根目录 `README.md` 当前 Windows 版本。
  - 更新 Windows changelog。
  - 新增 `releases/windows/2.0.11/README.md`。

## 涉及文件

- `Triple_2_Eyes_Protection_windows/reminder_window.py`
- `Triple_2_Eyes_Protection_windows/main.pyw`
- `Triple_2_Eyes_Protection_windows/installer/Triple2EyeProtection.iss`
- `README.md`
- `releases/windows/CHANGELOG.md`
- `releases/windows/2.0.11/README.md`
- `docs/windows-2.0.11-reminder-ui.md`

## 验证

- 使用 `python -m py_compile` 编译 Windows 端 Python 源文件。
- 使用 Qt offscreen 小测试验证：
  - 延时按钮尺寸为 `140x40`。
  - 延时按钮仍可通过内部数字值发出延时分钟数。
  - `已用眼` 使用红色 `#D64545`。
  - `开始休息` 后延时按钮禁用。
- 使用 PyInstaller 构建 Windows onedir 程序。
- 使用 Inno Setup 生成 `Triple2EyeProtection-Setup-2.0.11.exe`。
