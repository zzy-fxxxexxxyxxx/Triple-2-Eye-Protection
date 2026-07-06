# Windows 2.1.3 查询页曲线边界与拐点修复

## 背景

Windows 2.1.2 修复了曲线图的渐变跳变线和时间轴色块高度，但在较紧凑窗口中仍可能出现两个问题：

- 曲线图底部时间刻度贴近或超出 `状态曲线` 区域下边界。
- 部分状态转折处只有直角跳变，没有圆点标记。

这两个问题都属于查询页曲线图绘制和布局问题，不涉及日志数据格式。

## 原因分析

- 旧实现把时间刻度画在数据绘图区外侧，依赖固定底部留白。如果外层布局压缩图表控件，就容易出现底部文字被裁切的视觉问题。
- 圆点只在状态段起点绘制。状态段终点、垂直跳变另一端，以及同一秒连续记录造成的零时长状态，都可能没有圆点。
- `UsagePlotWidget` 最小高度设为 `380px` 后，默认查询窗口中控件总高度偏紧，外层窗口更容易出现视觉裁切。

## 修改内容

- 曲线图布局
  - 将曲线图内部划分为数据区和时间刻度区。
  - 时间刻度固定绘制在白色图表内部底部，而不是绘图区外侧。
  - 对 `plot_bottom` 做边界保护，避免父布局压缩时计算出控件外坐标。

- 拐点圆点
  - 状态段起点和终点都绘制圆点。
  - 原始日志记录点也绘制圆点。
  - 同一秒内连续写入不同状态时，即使中间状态没有形成可见时长，也能显示对应圆点。
  - 圆点统一在所有线条绘制完成后再绘制，避免被后续线条遮住。

- 窗口适配
  - 将图表控件最小高度从 `380px` 调整为 `320px`。
  - 保留时间轴色块的动态高度逻辑，避免回到旧版固定窄条。

## 涉及文件

- `Triple_2_Eyes_Protection_windows/usage_query_window.py`
- `Triple_2_Eyes_Protection_windows/main.pyw`
- `Triple_2_Eyes_Protection_windows/installer/Triple2EyeProtection.iss`
- `README.md`
- `releases/windows/CHANGELOG.md`
- `releases/windows/2.1.3/README.md`
- `docs/windows-2.1.3-usage-query-curve-bounds.md`

## 验证

- 使用 `python -m py_compile` 编译 Windows 端 Python 源文件。
- 使用 Qt offscreen 检查默认 `1060x760` 查询窗口中图表控件不会超出窗口可见区域。
- 使用 Qt offscreen 渲染曲线图并检查：
  - 时间刻度文字位于图表控件内部。
  - 长时间 `未记录` 仍为连续灰色实线。
  - 状态段起点、终点和同秒记录点均有圆点。
- 使用 PyInstaller 重新构建 Windows onedir 程序。
- 使用 Inno Setup 生成 `Triple2EyeProtection-Setup-2.1.3.exe`。
