# Windows 2.1.5 查询页时间轴标签修复

## 背景

Windows 2.1.4 修复了查询页全屏时 `状态曲线` 图表穿出组框底边的问题，但曲线图底部时间标签仍存在两个视觉问题：

- 首尾时间标签按固定宽度绘制，右侧标签在宽屏或全屏下可能被截断。
- 时间标签被放进内部白色图框后，标签下方还会出现一条图框底边，看起来像多余的线，并且标签距离图框下沿偏远。

这些问题属于图表绘制布局问题，不涉及使用记录格式，旧日志数据不需要迁移。

## 实现思路

将曲线图底部分成两个区域：

- 数据绘图区：只包含状态曲线、水平参考线、状态点和数据区域边框。
- x 轴标签区：位于数据绘图区下方，仅绘制刻度线和时间文本，不再被内部矩形边框包住。

时间标签使用字体度量结果计算真实宽度，首尾标签会被限制在图表宽度内，避免向左右溢出。

## 修改内容

- `UsagePlotWidget.draw_time_ticks()`
  - 取消固定 `x - 30` 和 `86px` 文本框。
  - 使用 `fontMetrics().horizontalAdvance()` 计算每个时间标签实际宽度。
  - 首尾标签根据图表左右边界自动内收。
  - 根据可用宽度动态减少刻度数量，避免标签互相挤压。

- `UsagePlotWidget.draw_curve()`
  - 数据绘图区边框只画到 x 轴位置。
  - 时间标签区不再被内部边框包住，去掉标签下方多余的线。
  - 将时间标签底部安全留白收紧到稳定的内部边距，使标签更贴近图表底部。
  - 根据最长时间标签为右侧预留空间，降低末尾标签被裁切的概率。

## 涉及文件

- `Triple_2_Eyes_Protection_windows/usage_query_window.py`
- `Triple_2_Eyes_Protection_windows/main.pyw`
- `Triple_2_Eyes_Protection_windows/installer/Triple2EyeProtection.iss`
- `README.md`
- `releases/windows/CHANGELOG.md`
- `docs/windows-2.1.5-usage-query-time-axis.md`
- `releases/windows/2.1.5/README.md`

## 验证

- 使用 `python -m py_compile` 编译 Windows 端 Python 源文件。
- 使用 Qt offscreen 检查 `1060x360`、`1400x420`、`2048x520` 三种绘图尺寸：
  - 首尾时间标签均在图表宽度内。
  - 标签底部与控件底部保持稳定安全距离。
  - x 轴位置仍保留足够数据绘图区高度。
- 使用 PyInstaller 重新构建 Windows onedir 程序。
- 使用 Inno Setup 生成 `Triple2EyeProtection-Setup-2.1.5.exe`。
