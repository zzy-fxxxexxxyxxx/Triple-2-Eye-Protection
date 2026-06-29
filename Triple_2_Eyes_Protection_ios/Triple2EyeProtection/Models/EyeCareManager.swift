import Foundation
import Combine
import SwiftUI
import ActivityKit

/// Port of EyeCareService.java — core state machine and timer.
/// On iOS we cannot run a persistent background service, so we:
/// - Drive a Timer while the app is in the foreground
/// - Schedule UNNotificationRequest for work-end / rest-end alerts
/// - Update a Live Activity (Dynamic Island) for at-a-glance status
@MainActor
final class EyeCareManager: ObservableObject {
    static let shared = EyeCareManager()

    private let settings = AppSettings.shared
    private let usageStore = UsageStore.shared

    @Published var currentState: AppSettings.State = .stopped
    @Published var remainingMs: Int64 = 0
    @Published var formattedRemaining: String = "00:00"
    @Published var statsSummary: String = ""

    private var timer: AnyCancellable?
    private var phaseTask: Task<Void, Never>?

    private init() {
        refreshFromPrefs()
    }

    // MARK: - Public commands

    func start() {
        let now = nowMs()
        cancelRestAlert()
        settings.startWorking(now: now)
        scheduleNotification(at: settings.workEndAt, title: "休息时间到了", body: "请离开屏幕，远望6米外")
        publishState()
    }

    func pause() {
        guard case .working = currentState else { return }
        settings.pause(remainingMs: remainingMs)
        cancelAlarm()
        publishState()
    }

    func resume() {
        guard case .paused = currentState else { return }
        cancelRestAlert()
        let now = nowMs()
        settings.resume(now: now)
        scheduleNotification(at: settings.workEndAt, title: "休息时间到了", body: "请离开屏幕，远望6米外")
        publishState()
    }

    func reset() {
        cancelAlarm()
        cancelRestAlert()
        let now = nowMs()
        settings.startWorking(now: now)
        scheduleNotification(at: settings.workEndAt, title: "休息时间到了", body: "请离开屏幕，远望6米外")
        publishState()
    }

    func stop() {
        cancelAlarm()
        cancelRestAlert()
        settings.stop()
        Task { await LiveActivityManager.shared.endAll() }
        publishState()
    }

    func restNow() {
        cancelAlarm()
        let now = nowMs()
        usageStore.record(.restStarted)
        settings.startResting(now: now)
        scheduleNotification(at: settings.restEndAt, title: "休息完成", body: "可以开始下一轮了，点击\"休息好了\"")
        NotificationManager.shared.postImmediateAlert(
            title: "休息时间到了",
            body: "请离开屏幕，远望6米外",
            identifier: "rest_alert_\(now)"
        )
        publishState()
    }

    func restDone() {
        guard case .resting = currentState else { return }
        usageStore.record(.restDone)
        cancelRestAlert()
        let now = nowMs()
        settings.startWorking(now: now)
        scheduleNotification(at: settings.workEndAt, title: "休息时间到了", body: "请离开屏幕，远望6米外")
        publishState()
    }

    // MARK: - Scene phase handling (like screen on/off on Android)

    func sceneDidEnterBackground() {
        // Reschedule notifications for background delivery
        switch currentState {
        case .working:
            scheduleNotification(at: settings.workEndAt, title: "休息时间到了", body: "请离开屏幕，远望6米外")
        case .resting:
            scheduleNotification(at: settings.restEndAt, title: "休息完成", body: "可以开始下一轮了")
        default:
            break
        }
        timer?.cancel()
        timer = nil
    }

    func sceneWillEnterForeground() {
        checkDue()
        rescheduleForCurrentState()
        startTimerIfNeeded()
        publishState()
    }

    func sceneDidBecomeActive() {
        // Equivalent to onScreenActive() — check if we should resume from "screen off"
        if case .screenOff = currentState {
            let now = nowMs()
            let inactiveMs = max(0, now - settings.screenOffAt)
            let requiredRestMs = Int64(settings.restSeconds) * 1000
            if inactiveMs >= requiredRestMs {
                usageStore.record(.screenRest)
                usageStore.record(.restDone)
                cancelRestAlert()
                settings.startWorking(now: now)
            } else {
                settings.resume(now: now)
            }
            scheduleNotification(at: settings.workEndAt, title: "休息时间到了", body: "请离开屏幕，远望6米外")
            publishState()
        }
    }

    func sceneWillResignActive() {
        // Equivalent to onScreenOff()
        if case .working = currentState {
            let now = nowMs()
            settings.enterScreenOff(now: now, remainingMs: settings.remainingMs(now: now))
            cancelAlarm()
            publishState()
        }
    }

    // MARK: - Internal tick

    private func startTimerIfNeeded() {
        timer?.cancel()
        timer = Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in self?.onTick() }
    }

    private func onTick() {
        let now = nowMs()
        checkDue()
        remainingMs = settings.remainingMs(now: now)
        formattedRemaining = AppSettings.formatRemaining(remainingMs)

        // Update Live Activity every 5 ticks to avoid excessive updates
        if now % 5 == 0 {
            Task { await LiveActivityManager.shared.update(settings: settings, remainingMs: remainingMs) }
        }

        objectWillChange.send()
    }

    private func checkDue() {
        let now = nowMs()
        if case .working = currentState, settings.remainingMs(now: now) <= 0 {
            restNow() // enter rest
        }
    }

    private func rescheduleForCurrentState() {
        switch currentState {
        case .working:
            scheduleNotification(at: settings.workEndAt, title: "休息时间到了", body: "请离开屏幕，远望6米外")
        case .resting:
            scheduleNotification(at: settings.restEndAt, title: "休息完成", body: "可以开始下一轮了")
        default:
            cancelAlarm()
        }
    }

    private func publishState() {
        let now = nowMs()
        currentState = settings.state
        remainingMs = settings.remainingMs(now: now)
        formattedRemaining = AppSettings.formatRemaining(remainingMs)
        statsSummary = usageStore.summary()
        startTimerIfNeeded()
        Task { await LiveActivityManager.shared.update(settings: settings, remainingMs: remainingMs) }
        objectWillChange.send()
    }

    func refreshFromPrefs() {
        publishState()
        if settings.enabled, case .stopped = currentState {
            // Boot-like restore: if enabled but unknown state, start working
            let now = nowMs()
            settings.startWorking(now: now)
            scheduleNotification(at: settings.workEndAt, title: "休息时间到了", body: "请离开屏幕，远望6米外")
            publishState()
        }
    }

    // MARK: - Notification helpers

    private func scheduleNotification(at triggerMs: Int64, title: String, body: String) {
        guard triggerMs > 0 else { return }
        let triggerDate = Date(timeIntervalSince1970: TimeInterval(triggerMs) / 1000.0)
        NotificationManager.shared.schedule(title: title, body: body, at: triggerDate)
    }

    private func cancelAlarm() { NotificationManager.shared.cancelAll() }
    private func cancelRestAlert() { NotificationManager.shared.cancelWithPrefix("rest_alert_") }

    private func nowMs() -> Int64 { Int64(Date().timeIntervalSince1970 * 1000) }
}

// MARK: - Settings helpers (bridged for views)
extension EyeCareManager {
    var workMinutes: Int {
        get { settings.workMinutes }
        set { settings.setDurations(workMinutes: newValue, restSeconds: settings.restSeconds, fadeSeconds: settings.fadeSeconds, vibrate: settings.vibrateOnRest) }
    }
    var restSeconds: Int {
        get { settings.restSeconds }
        set { settings.setDurations(workMinutes: settings.workMinutes, restSeconds: newValue, fadeSeconds: settings.fadeSeconds, vibrate: settings.vibrateOnRest) }
    }
    var fadeSeconds: Float {
        get { settings.fadeSeconds }
        set { settings.setDurations(workMinutes: settings.workMinutes, restSeconds: settings.restSeconds, fadeSeconds: newValue, vibrate: settings.vibrateOnRest) }
    }
    var vibrateOnRest: Bool {
        get { settings.vibrateOnRest }
        set { settings.setVibrateOnRest(newValue) }
    }
    var workEndAtMs: Int64 { settings.workEndAt }
    var restEndAtMs: Int64 { settings.restEndAt }
}
