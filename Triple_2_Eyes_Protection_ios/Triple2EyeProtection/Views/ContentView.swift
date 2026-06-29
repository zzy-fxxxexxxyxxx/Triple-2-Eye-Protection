import SwiftUI

struct ContentView: View {
    @EnvironmentObject var manager: EyeCareManager
    @State private var showRestOverlay = false
    @State private var showKeepAliveGuide = false

    var body: some View {
        NavigationStack {
            ZStack {
                ScrollView {
                    VStack(spacing: 16) {
                        headerSection
                        statusCard
                        settingsCard
                        controlCard
                        keepAliveCard
                        statsCard
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 24)
                    .padding(.bottom, 28)
                }
                .background(Color(.systemGroupedBackground).ignoresSafeArea())
                .onReceive(manager.objectWillChange) { _ in
                    showRestOverlay = manager.currentState == .resting
                }
                .onAppear {
                    showRestOverlay = manager.currentState == .resting
                }

                // Full-screen rest overlay
                if showRestOverlay {
                    RestOverlayView(isPresented: $showRestOverlay)
                        .transition(.opacity)
                }
            }
            .animation(.easeInOut(duration: TimeInterval(manager.fadeSeconds)), value: showRestOverlay)
        }
    }

    // MARK: - Header

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Triple 2 Eye Protection")
                .font(.title.weight(.bold))
                .foregroundColor(.primary)
            Text("护眼倒计时会通过通知与灵动岛在后台运行")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    // MARK: - Status Card

    private var statusCard: some View {
        card {
            VStack(spacing: 4) {
                Text(AppSettings.shared.stateLabel(manager.currentState))
                    .font(.headline.weight(.bold))
                    .foregroundColor(.primary)
                Text(manager.formattedRemaining)
                    .font(.system(size: 52, design: .monospaced).bold())
                    .foregroundColor(AppTheme.primary)
                    .frame(maxWidth: .infinity, alignment: .center)
            }
            .padding(.vertical, 8)
        }
    }

    // MARK: - Settings Card

    @State private var workMinutesText: String = ""
    @State private var restSecondsText: String = ""
    @State private var fadeSecondsText: String = ""

    private var settingsCard: some View {
        card {
            Text("设置")
                .font(.headline.weight(.bold))
                .frame(maxWidth: .infinity, alignment: .leading)

            HStack(spacing: 12) {
                Text("用眼时间：")
                    .frame(width: 92, alignment: .leading)
                TextField("20", text: $workMinutesText)
                    .keyboardType(.numberPad)
                    .textFieldStyle(.roundedBorder)
                Text("分钟")
                    .frame(width: 44, alignment: .trailing)
                    .foregroundColor(.secondary)
            }
            .onAppear { workMinutesText = String(manager.workMinutes) }

            HStack(spacing: 12) {
                Text("休息时间：")
                    .frame(width: 92, alignment: .leading)
                TextField("20", text: $restSecondsText)
                    .keyboardType(.numberPad)
                    .textFieldStyle(.roundedBorder)
                Text("秒")
                    .frame(width: 44, alignment: .trailing)
                    .foregroundColor(.secondary)
            }
            .onAppear { restSecondsText = String(manager.restSeconds) }

            HStack(spacing: 12) {
                Text("过渡时间：")
                    .frame(width: 92, alignment: .leading)
                TextField("1.2", text: $fadeSecondsText)
                    .keyboardType(.decimalPad)
                    .textFieldStyle(.roundedBorder)
                Text("s")
                    .frame(width: 44, alignment: .trailing)
                    .foregroundColor(.secondary)
            }
            .onAppear { fadeSecondsText = formatFade(manager.fadeSeconds) }

            Button(action: saveSettings) {
                Text("保存设置")
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
            }
            .buttonStyle(AppTheme.primaryButton)
        }
    }

    // MARK: - Control Card

    private var controlCard: some View {
        card {
            Text("控制")
                .font(.headline.weight(.bold))
                .frame(maxWidth: .infinity, alignment: .leading)

            Toggle("休息时震动", isOn: Binding(
                get: { manager.vibrateOnRest },
                set: { manager.vibrateOnRest = $0 }
            ))

            let isStopped = manager.currentState == .stopped
            let isPaused = manager.currentState == .paused
            let isActive = manager.currentState == .working || isPaused

            Button(action: { isStopped ? manager.start() : manager.reset() }) {
                Text(isStopped ? "开启护眼" : "重新开始")
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
            }
            .buttonStyle(AppTheme.primaryButton)

            Button(action: {
                if isPaused { manager.resume() }
                else { manager.pause() }
            }) {
                Text(isPaused ? "继续" : "暂停")
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
            }
            .buttonStyle(AppTheme.outlineButton)
            .disabled(!isActive)

            Button(action: { manager.reset() }) {
                Text("重置")
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
            }
            .buttonStyle(AppTheme.outlineButton)

            Button(action: { manager.restNow() }) {
                Text("立即休息")
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
            }
            .buttonStyle(AppTheme.primaryButton)

            Button(action: { manager.stop() }) {
                Text("关闭服务")
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
            }
            .buttonStyle(AppTheme.dangerButton)
        }
    }

    // MARK: - Keep-Alive Card (iOS-specific)

    private var keepAliveCard: some View {
        card {
            Text("iOS 保活指南")
                .font(.headline.weight(.bold))
                .frame(maxWidth: .infinity, alignment: .leading)

            Text("为确保护眼提醒正常工作，请：\n• 允许通知权限\n• 关闭低功耗模式\n• 在专注模式中将本 App 加入白名单\n• 定期打开 App 以保持后台活动")
                .font(.subheadline)
                .foregroundColor(.secondary)

            Button(action: { showKeepAliveGuide = true }) {
                Text("打开系统设置")
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
            }
            .buttonStyle(AppTheme.outlineButton)
        }
        .alert("打开设置", isPresented: $showKeepAliveGuide) {
            Button("打开通知设置") {
                if let url = URL(string: UIApplication.openNotificationSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            }
            Button("取消", role: .cancel) {}
        } message: {
            Text("请确保通知权限已开启，以接收休息提醒。")
        }
    }

    // MARK: - Stats Card

    private var statsCard: some View {
        card {
            HStack {
                Text("休息统计")
                    .font(.headline.weight(.bold))
                Spacer()
                NavigationLink(destination: StatsView()) {
                    Text("查看详情")
                        .font(.subheadline)
                }
            }
            Text(manager.statsSummary)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    // MARK: - Helpers

    private func card<Content: View>(@ViewBuilder content: () -> Content) -> some View {
        VStack(spacing: 10) {
            content()
        }
        .padding(16)
        .background(Color(.systemBackground))
        .cornerRadius(8)
    }

    private func saveSettings() {
        guard let wm = Int(workMinutesText), wm > 0,
              let rs = Int(restSecondsText), rs > 0,
              let fs = Float(fadeSecondsText.replacingOccurrences(of: ",", with: ".")), fs >= 0, fs <= 10
        else {
            return
        }
        manager.workMinutes = wm
        manager.restSeconds = rs
        manager.fadeSeconds = fs
    }

    private func formatFade(_ value: Float) -> String {
        if abs(value - round(value)) < 0.0005 {
            return String(Int(round(value)))
        }
        let s = String(format: "%.3f", value)
        return s.replacingOccurrences(of: "0+$", with: "", options: .regularExpression)
            .replacingOccurrences(of: "\\.$", with: "", options: .regularExpression)
    }
}
