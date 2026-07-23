# Windows 2.1.8 提醒弹窗三档延时按钮

## 背景

Windows 2.0.10 和 2.0.11 已经把提醒弹窗里的延时输入整合为红色内联按钮，避免独立输入框破坏弹窗视觉。但弹窗第一行仍然只有一个 `延时：xx分钟` 控件，用户如果想临时选择更长延时，需要先编辑数字再点击按钮。

本次升级只调整提醒弹窗第一行的延时按钮布局，不改变 `已用眼`、`已提醒`、`开始休息`、`休息好了`、淡入动画、主计时器和日志记录逻辑。

## 实现思路

- 保留 `InlineDelayButton` 的红色按钮内编辑方式，让每个延时值仍可在弹窗内临时修改。
- 将原来的单个延时按钮拆成三个并排按钮。
- 第一个按钮继续使用主界面的 `默认延时 / min` 配置值，默认安装状态下为 `10`。
- 第二、第三个按钮默认分别为 `20` 和 `30` 分钟。
- 点击任意一个延时按钮都会发出对应分钟数，关闭弹窗并继续当前用眼 session。
- 点击 `开始休息` 后同时禁用三个延时按钮，保持原有“休息中不能再延时”的行为。

## 修改内容

- `InlineDelayButton`
  - 新增 `width` 和 `show_prefix` 参数，支持在单排三按钮布局中压缩控件宽度。
  - 保留 `延时：xx分钟` 的整体文案和按钮内 `QSpinBox` 编辑能力。

- `ReminderWindow`
  - 新增 `delay_buttons` 列表，创建三枚延时按钮。
  - 三枚按钮默认值为 `[默认延时, 20, 30]`，默认配置下显示为 `10/20/30`。
  - `on_delay_requested()` 改为接收被点击的按钮，并读取该按钮当前值。
  - `on_start_rest()` 改为禁用所有延时按钮。

- 发布资料
  - Windows 版本号递增到 `2.1.8`。
  - 更新根目录 `README.md` 当前 Windows 版本和功能描述。
  - 更新 Windows changelog。
  - 新增 `releases/windows/2.1.8/README.md`。

## 涉及文件

- `Triple_2_Eyes_Protection_windows/reminder_window.py`
- `Triple_2_Eyes_Protection_windows/main.pyw`
- `Triple_2_Eyes_Protection_windows/installer/Triple2EyeProtection.iss`
- `README.md`
- `releases/windows/CHANGELOG.md`
- `releases/windows/2.1.8/README.md`
- `docs/windows-2.1.8-reminder-delay-presets.md`

## 验证

- 使用 `python -m py_compile` 编译 Windows 端 Python 源文件。
- 使用 Qt offscreen 测试验证：
  - 提醒弹窗有三枚延时按钮。
  - 默认按钮值为 `10/20/30`。
  - 点击第二枚按钮会发出 `20` 分钟延时请求。
  - 修改第三枚按钮值后，点击按钮会发出修改后的分钟数。
  - 点击 `开始休息` 后三枚延时按钮全部禁用。
- 使用 PyInstaller 重新构建 Windows onedir 程序。
- 使用 Inno Setup 生成 `Triple2EyeProtection-Setup-2.1.8.exe`。
