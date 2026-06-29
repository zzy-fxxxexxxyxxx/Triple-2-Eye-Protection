import Foundation

/// Port of AppPrefs.java — wraps UserDefaults for all app settings.
final class AppSettings {
    static let shared = AppSettings()

    enum State: String {
        case stopped
        case working
        case paused
        case resting
        case screenOff
    }

    // MARK: - Keys
    private let kEnabled = "enabled"
    private let kWorkMinutes = "work_minutes"
    private let kRestSeconds = "rest_seconds"
    private let kFadeSeconds = "fade_seconds"
    private let kVibrateOnRest = "vibrate_on_rest"
    private let kState = "state"
    private let kWorkEndAt = "work_end_at"
    private let kRestEndAt = "rest_end_at"
    private let kPauseRemainingMs = "pause_remaining_ms"
    private let kScreenOffAt = "screen_off_at"

    /// Uses App Group suite so the Widget can read the same data.
    /// Falls back to standard UserDefaults if the App Group is not configured.
    private let defaults = UserDefaults(suiteName: "group.com.triple2.eyeprotection") ?? UserDefaults.standard

    private init() {}

    // MARK: - Simple accessors
    var enabled: Bool { defaults.bool(forKey: kEnabled) }
    var workMinutes: Int { max(1, defaults.integer(key: kWorkMinutes, fallback: 20)) }
    var restSeconds: Int { max(1, defaults.integer(key: kRestSeconds, fallback: 20)) }
    var fadeSeconds: Float { clampFade(defaults.float(key: kFadeSeconds, fallback: 1.2)) }
    var vibrateOnRest: Bool { defaults.bool(forKey: kVibrateOnRest) }
    var state: State { State(rawValue: defaults.string(forKey: kState) ?? "") ?? .stopped }
    var workEndAt: Int64 { Int64(defaults.integer(key: kWorkEndAt, fallback: 0)) }
    var restEndAt: Int64 { Int64(defaults.integer(key: kRestEndAt, fallback: 0)) }
    var pauseRemainingMs: Int64 { Int64(defaults.integer(key: kPauseRemainingMs, fallback: 0)) }
    var screenOffAt: Int64 { Int64(defaults.integer(key: kScreenOffAt, fallback: 0)) }

    // MARK: - Computed helpers
    func remainingMs(now: Int64) -> Int64 {
        switch state {
        case .working:
            return max(0, workEndAt - now)
        case .resting:
            return max(0, restEndAt - now)
        case .paused, .screenOff:
            return max(0, pauseRemainingMs)
        case .stopped:
            return 0
        }
    }

    func stateLabel(_ s: State) -> String {
        switch s {
        case .working:   return "正在用眼"
        case .resting:   return "休息提醒中"
        case .paused:    return "已暂停"
        case .screenOff: return "屏幕已关闭"
        case .stopped:   return "未开启"
        }
    }

    static func formatRemaining(_ remainingMs: Int64) -> String {
        let totalSeconds = max(0, (remainingMs + 999) / 1000)
        let hours = totalSeconds / 3600
        let minutes = (totalSeconds % 3600) / 60
        let seconds = totalSeconds % 60
        if hours > 0 {
            return String(format: "%02d:%02d:%02d", hours, minutes, seconds)
        }
        return String(format: "%02d:%02d", minutes, seconds)
    }

    // MARK: - State transitions
    func startWorking(now: Int64) {
        let workEnd = now + Int64(workMinutes) * 60_000
        defaults.setValues([
            kEnabled: true,
            kState: State.working.rawValue,
            kWorkEndAt: workEnd,
            kRestEndAt: 0,
            kPauseRemainingMs: 0,
            kScreenOffAt: 0,
        ])
    }

    func startResting(now: Int64) {
        let restEnd = now + Int64(restSeconds) * 1_000
        defaults.setValues([
            kEnabled: true,
            kState: State.resting.rawValue,
            kRestEndAt: restEnd,
            kPauseRemainingMs: 0,
            kScreenOffAt: 0,
        ])
    }

    func pause(remainingMs: Int64) {
        defaults.setValues([
            kState: State.paused.rawValue,
            kPauseRemainingMs: max(0, remainingMs),
        ])
    }

    func resume(now: Int64) {
        let remaining = max(1_000, pauseRemainingMs)
        defaults.setValues([
            kState: State.working.rawValue,
            kWorkEndAt: now + remaining,
            kPauseRemainingMs: 0,
            kScreenOffAt: 0,
        ])
    }

    func enterScreenOff(now: Int64, remainingMs: Int64) {
        defaults.setValues([
            kState: State.screenOff.rawValue,
            kPauseRemainingMs: max(0, remainingMs),
            kScreenOffAt: now,
        ])
    }

    func stop() {
        defaults.setValues([
            kEnabled: false,
            kState: State.stopped.rawValue,
            kWorkEndAt: 0,
            kRestEndAt: 0,
            kPauseRemainingMs: 0,
            kScreenOffAt: 0,
        ])
    }

    func setDurations(workMinutes: Int, restSeconds: Int, fadeSeconds: Float, vibrate: Bool) {
        defaults.setValues([
            kWorkMinutes: max(1, workMinutes),
            kRestSeconds: max(1, restSeconds),
            kFadeSeconds: clampFade(fadeSeconds),
            kVibrateOnRest: vibrate,
        ])
    }

    func setVibrateOnRest(_ on: Bool) {
        defaults.set(kVibrateOnRest, to: on)
    }

    // MARK: - Private helpers
    private func clampFade(_ value: Float) -> Float { max(0, min(10, value)) }
}

// MARK: - UserDefaults helpers
private extension UserDefaults {
    func integer(key: String, fallback: Int) -> Int {
        dictionaryRepresentation()[key] == nil ? fallback : integer(forKey: key)
    }

    func float(key: String, fallback: Float) -> Float {
        dictionaryRepresentation()[key] == nil ? fallback : float(forKey: key)
    }

    func setValues(_ pairs: [String: Any]) {
        pairs.forEach { key, value in
            if let bool = value as? Bool {
                set(bool, forKey: key)
            } else if let int = value as? Int {
                set(int, forKey: key)
            } else if let int64 = value as? Int64 {
                set(Int(int64), forKey: key)
            } else if let str = value as? String {
                set(str, forKey: key)
            }
        }
    }

    func set(_ key: String, to value: Any) {
        setValues([key: value])
    }
}
