# Windows 2.1.2 查询页图表绘制修复

## 背景

Windows 2.1.0 引入查询页状态语义化、`未记录` 状态和图表呈现方式切换后，曲线图与时间轴色块仍有几个显示细节不符合旧版体验：

- 曲线图状态跳变线被画成灰色直线，而旧版是相邻状态颜色之间的渐变线。
- 长时间 `未记录` 被画成灰色虚线，视觉上像“缺失绘制”，不符合当前 `未记录` 已经是正式状态的语义。
- `未记录 y=-0.1` 接近曲线图底部，下方时间刻度和文字容易显得贴边。
- 时间轴色块高度固定为 `70px`，在较高窗口中显得过矮。

## 实现思路

- 曲线图仍然使用语义状态段绘制，但状态段之间的垂直跳变线恢复为 `QLinearGradient`。
- `未记录` 作为正式状态展示，横向状态段使用灰色实线，而不是虚线。
- 曲线图的 y 轴范围不再只给固定 `0.05` 的边距，而是按当前 y 值范围增加动态边距。
- 时间轴色块高度根据图表控件高度动态计算，并设置合理上下限。
- 图表控件最小高度从 `340px` 提高到 `380px`，给曲线底部刻度和色块展示留出更稳定空间。

## 修改内容

- `UsagePlotWidget.draw_curve()`
  - 使用 `QLinearGradient` 和 `QBrush` 绘制状态跳变线。
  - 将所有状态横线统一设为实线，包括 `未记录`。
  - 将顶部和底部边距调整为 `top=64`、`bottom=82`。
  - y 轴绘制范围使用动态 padding，避免底部状态过度贴近边界。

- `UsagePlotWidget.draw_timeline()`
  - 将时间轴色块高度从固定 `70px` 改为动态高度。
  - 默认在常见窗口高度下可达到约 `200px` 以上，最高限制为 `240px`。
  - 保留底部时间刻度空间，避免文字压到控件边界。

- `UsagePlotWidget`
  - 最小高度调整为 `380px`。

## 涉及文件

- `Triple_2_Eyes_Protection_windows/usage_query_window.py`
- `Triple_2_Eyes_Protection_windows/main.pyw`
- `Triple_2_Eyes_Protection_windows/installer/Triple2EyeProtection.iss`
- `README.md`
- `releases/windows/CHANGELOG.md`
- `releases/windows/2.1.2/README.md`
- `docs/windows-2.1.2-usage-query-chart-polish.md`

## 验证

- 使用 `python -m py_compile` 编译 Windows 端 Python 源文件。
- 使用 Qt offscreen 渲染曲线图并检查：
  - 状态跳变处存在彩色渐变像素。
  - 长时间 `未记录` 横线为连续灰色实线。
  - 底部时间刻度仍位于图表控件内部。
- 使用 Qt offscreen 渲染时间轴色块并检查：
  - 色块高度明显大于旧固定高度。
  - 色块区域不会压到底部时间刻度。
- 使用 PyInstaller 重新构建 Windows onedir 程序。
- 使用 Inno Setup 生成 `Triple2EyeProtection-Setup-2.1.2.exe`。
