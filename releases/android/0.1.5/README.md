# Triple 2 Eye Protection Android 0.1.5

发布时间：2026-06-07

## 安装包

- `Triple2EyeProtection-Android-0.1.5-release.apk`

## 版本信息

- 包名：`com.triple2.eyeprotection`
- `versionCode`：`6`
- `versionName`：`0.1.5`
- 签名：当前测试版使用 debug 签名

## 更新内容

- 修复点击“休息好了”后错误回到 Triple 2 Eye Protection 主界面的问题。
- 如果悬浮窗权限已开启，休息提醒只显示悬浮覆盖层，不再额外启动应用 Activity。
- 关闭悬浮覆盖层后，会回到弹出前正在使用的界面，例如 B 站、桌面或应用主界面。
- 设置区输入框新增明确标签和单位：
  - 用眼时间：分钟
  - 休息时间：秒
- 可直接覆盖安装 `0.1.4`。

## 测试建议

把用眼时长设为 `1` 分钟，点击“开启护眼”，切到 B 站等待到点。出现休息覆盖层后点击“休息好了”，预期应回到 B 站，而不是回到 Triple 2 Eye Protection 主界面。
