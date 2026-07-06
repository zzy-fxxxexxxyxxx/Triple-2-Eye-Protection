# Windows 2.1.1 查询页曲线图灰底修复

## 问题背景

Windows 2.1.0 查询页新增了 `未记录` 状态和可配置 y 值后，曲线图模式中可能出现整块绘图区被灰色填满的问题。用户提供的日志仍然是兼容格式，例如：

- `1` 表示 `使用中`
- `0.3` 表示 `提醒未休息`
- `0` 表示 `休息中`
- `-1` 表示 `未记录`

因此问题不是历史数据格式不兼容，而是曲线图绘制代码的 bug。

## 原因分析

`UsagePlotWidget.draw_legend()` 在绘制图例时会设置 `QPainter` 的 brush。图例最后一个状态是 `未记录`，颜色为灰色。

在 2.1.0 的 `draw_curve()` 中，绘制图例后紧接着调用 `painter.drawRect(left, top, width, height)` 绘制曲线图边框，但没有先把 brush 重置为 `NoBrush`。Qt 的 `QPainter` 会保留上一次设置的 brush，因此 `drawRect()` 不只画边框，还用灰色 brush 填充了整个绘图区。

## 修改内容

- 在 `draw_curve()` 中先用白色显式填充绘图区，避免继承旧的绘制状态。
- 在绘制图表边框前调用 `painter.setBrush(Qt.BrushStyle.NoBrush)`，确保 `drawRect()` 只画边框。
- 根据 y 轴标签文本宽度动态计算左侧边距，避免 `未记录 y=-0.1` 等长标签压进绘图区。
- 将 y 轴标签改为在绘图区外侧右对齐显示，减少文字和曲线区域的重叠。
- Windows 版本号从 `2.1.0` 升级到 `2.1.1`。

## 涉及文件

- `Triple_2_Eyes_Protection_windows/usage_query_window.py`
- `Triple_2_Eyes_Protection_windows/main.pyw`
- `Triple_2_Eyes_Protection_windows/installer/Triple2EyeProtection.iss`
- `README.md`
- `releases/windows/CHANGELOG.md`
- `releases/windows/2.1.1/README.md`
- `docs/windows-2.1.1-usage-query-chart-fix.md`

## 验证

- 使用 `python -m py_compile` 编译 Windows 端 Python 源文件。
- 使用 Qt offscreen 脚本渲染包含 `未记录` 图例的曲线图。
- 检查绘图区中心像素不再是 `未记录` 的灰色。
- 检查曲线图仍能显示四种状态，并保留 `0.3` 到 `提醒未休息`、`-1` 到 `未记录` 的兼容映射。
- 使用 PyInstaller 重新构建 Windows onedir 程序。
- 使用 Inno Setup 生成 `Triple2EyeProtection-Setup-2.1.1.exe`。
