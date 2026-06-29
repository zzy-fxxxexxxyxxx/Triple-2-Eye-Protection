import Foundation

/// Port of UsageStore.java — tracks rest events for statistics.
final class UsageStore {
    static let shared = UsageStore()

    enum EventType: String {
        case restStarted = "rest_started"
        case restDone = "rest_done"
        case screenRest = "screen_rest"
    }

    private let kEvents = "usage_events"
    private let keepMs: Int64 = 370 * 24 * 60 * 60 * 1000 // 370 days

    private let defaults = UserDefaults(suiteName: "group.com.triple2.eyeprotection") ?? UserDefaults.standard

    private init() {}

    func record(_ type: EventType) {
        let now = Int64(Date().timeIntervalSince1970 * 1000)
        var events = loadEvents()
        let keepAfter = now - keepMs
        events = events.filter { $0.timestamp >= keepAfter }
        events.append((timestamp: now, type: type))
        saveEvents(events)
    }

    func countSince(_ sinceMs: Int64, type: EventType) -> Int {
        loadEvents().filter { $0.timestamp >= sinceMs && $0.type == type }.count
    }

    func summary() -> String {
        let now = Int64(Date().timeIntervalSince1970 * 1000)
        let hour: Int64 = 60 * 60 * 1000
        let day: Int64 = 24 * hour

        var lines: [(String, Int)] = []
        lines.append(("12h", countSince(now - 12 * hour, type: .restDone)))
        lines.append(("24h", countSince(now - day, type: .restDone)))
        lines.append(("7天", countSince(now - 7 * day, type: .restDone)))
        lines.append(("1个月", countSince(now - 30 * day, type: .restDone)))
        lines.append(("6个月", countSince(now - 180 * day, type: .restDone)))
        lines.append(("1年", countSince(now - 365 * day, type: .restDone)))

        return lines.map { "\($0.0)：完成休息 \($0.1) 次" }.joined(separator: "\n")
    }

    /// Returns daily rest counts for the last `days` days — used by the chart view.
    func dailyRestCounts(days: Int = 30) -> [(date: Date, count: Int)] {
        let now = Date()
        let calendar = Calendar.current
        var result: [(Date, Int)] = []
        let allEvents = loadEvents().filter { $0.type == .restDone }
        for offset in 0..<days {
            guard let dayStart = calendar.date(byAdding: .day, value: -offset, to: now)
                    .flatMap({ calendar.startOfDay(for: $0) }) else { continue }
            let dayEnd = calendar.date(byAdding: .day, value: 1, to: dayStart)!
            let startMs = Int64(dayStart.timeIntervalSince1970 * 1000)
            let endMs = Int64(dayEnd.timeIntervalSince1970 * 1000)
            let count = allEvents.filter { $0.timestamp >= startMs && $0.timestamp < endMs }.count
            result.append((dayStart, count))
        }
        return result.reversed()
    }

    // MARK: - Private
    private func loadEvents() -> [(timestamp: Int64, type: EventType)] {
        guard let raw = defaults.string(forKey: kEvents), !raw.isEmpty else { return [] }
        return raw.split(separator: ";").compactMap { part in
            let parts = part.split(separator: ",", maxSplits: 1)
            guard parts.count == 2,
                  let ts = Int64(parts[0]),
                  let type = EventType(rawValue: String(parts[1])) else { return nil }
            return (ts, type)
        }
    }

    private func saveEvents(_ events: [(timestamp: Int64, type: EventType)]) {
        let raw = events.map { "\($0.timestamp),\($0.type.rawValue)" }.joined(separator: ";")
        defaults.set(raw, forKey: kEvents)
    }
}
