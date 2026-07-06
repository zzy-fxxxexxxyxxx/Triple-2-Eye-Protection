# Windows 2.1.4 查询页全屏边界修复

## 背景

Windows 2.1.3 已将曲线图时间刻度移入图表内部，并补齐拐点圆点。但在全屏窗口中，`状态曲线` 组框底边仍可能被图表子控件的白底和内部图框视觉上压住，看起来像曲线图下边沿穿过了 `状态曲线` 的下边框。

这个问题不是日志数据问题，而是 Qt 布局边距与绘图边界共同导致的显示问题。

## 原因分析

- `QGroupBox` 的边框不是自动裁切子控件绘制内容的硬边界。
- 图表子控件贴近 `QGroupBox` 底部时，子控件背景和内部图框会视觉上覆盖或压住组框底边。
- 之前的验证只检查了 plot widget 没有超出主窗口，没有检查 plot widget 与 `状态曲线` 组框底边之间的安全间距。

## 修改内容

- `状态曲线` 组框布局
  - 为 `chart_layout` 设置显式内容边距：左、上、右、下分别为 `18, 28, 18, 34`。
  - 设置控件间距为 `10`。
  - 图表控件以 stretch 方式加入布局，允许全屏时扩展，但始终保留底部安全边距。

- 曲线图内部边界
  - 将内部底部安全边距调整为 `44px`。
  - 将时间刻度区高度调整为 `44px`。
  - 时间刻度文字保持在白色图表区域内部，不再贴近子控件底部。

- 默认窗口适配
  - 将 `UsagePlotWidget` 最小高度调整为 `280px`，避免默认查询窗口被图表控件撑得过紧。
  - 全屏时图表仍可随窗口扩展。

## 涉及文件

- `Triple_2_Eyes_Protection_windows/usage_query_window.py`
- `Triple_2_Eyes_Protection_windows/main.pyw`
- `Triple_2_Eyes_Protection_windows/installer/Triple2EyeProtection.iss`
- `README.md`
- `releases/windows/CHANGELOG.md`
- `releases/windows/2.1.4/README.md`
- `docs/windows-2.1.4-usage-query-fullscreen-bounds.md`

## 验证

- 使用 `python -m py_compile` 编译 Windows 端 Python 源文件。
- 使用 Qt offscreen 在 `1060x760`、`2048x900`、`2048x1152` 尺寸下检查：
  - plot widget 与 `状态曲线` 组框底边之间至少保留 `30px` 安全距离。
  - plot widget 不超出主窗口可见范围。
- 使用 Qt offscreen 渲染全屏曲线图并检查：
  - 曲线图内部图框底边与 plot widget 底部保持安全距离。
  - 时间刻度位于图表内部。
  - 同秒状态变化的圆点仍然正常显示。
- 使用 PyInstaller 重新构建 Windows onedir 程序。
- 使用 Inno Setup 生成 `Triple2EyeProtection-Setup-2.1.4.exe`。
