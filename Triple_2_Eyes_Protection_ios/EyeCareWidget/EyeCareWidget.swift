import WidgetKit
import SwiftUI

/// Home-screen / Lock-screen widget showing current eye-care status.
/// Replaces the Android persistent notification's at-a-glance function.
///
/// NOTE: In Xcode, add AppSettings.swift and UsageStore.swift to the Widget target's
/// Target Membership (both App and Widget targets) so the widget can read shared data.
/// The models use an App Group UserDefaults suite for cross-target sharing.
struct EyeCareWidget: Widget {
    private let kind = "com.triple2.eyeprotection.widget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: EyeCareTimelineProvider()) { entry in
            EyeCareWidgetView(entry: entry)
                .containerBackground(.fill.tertiary, for: .widget)
        }
        .configurationDisplayName("护眼状态")
        .description("查看当前护眼倒计时状态和休息统计。")
        .supportedFamilies([.systemSmall, .systemMedium, .accessoryInline, .accessoryCircular, .accessoryRectangular])
    }
}

// MARK: - Widget Color (self-contained, no dependency on AppTheme)

private enum WidgetColor {
    static let primary = Color(red: 0.12, green: 0.48, blue: 0.30) // rgb(31, 122, 77)
}

// MARK: - Timeline Provider

struct EyeCareTimelineProvider: TimelineProvider {
    typealias Entry = EyeCareWidgetEntry

    func placeholder(in context: Context) -> EyeCareWidgetEntry {
        EyeCareWidgetEntry(date: Date(), stateLabel: "未开启", countdown: "00:00", isActive: false, restCount24h: 0)
    }

    func getSnapshot(in context: Context, completion: @escaping (EyeCareWidgetEntry) -> Void) {
        completion(makeEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<EyeCareWidgetEntry>) -> Void) {
        let entry = makeEntry()
        let nextUpdate = Date().addingTimeInterval(5 * 60)
        let timeline = Timeline(entries: [entry], policy: .after(nextUpdate))
        completion(timeline)
    }

    private func makeEntry() -> EyeCareWidgetEntry {
        let settings = AppSettings.shared
        let now = Int64(Date().timeIntervalSince1970 * 1000)
        let remainingMs = settings.remainingMs(now: now)
        let count24h = UsageStore.shared.countSince(now - 24 * 60 * 60 * 1000, type: .restDone)
        let isActive = settings.enabled && settings.state != .stopped

        return EyeCareWidgetEntry(
            date: Date(),
            stateLabel: settings.stateLabel(settings.state),
            countdown: AppSettings.formatRemaining(remainingMs),
            isActive: isActive,
            restCount24h: count24h
        )
    }
}

// MARK: - Entry

struct EyeCareWidgetEntry: TimelineEntry {
    let date: Date
    let stateLabel: String
    let countdown: String
    let isActive: Bool
    let restCount24h: Int
}

// MARK: - Widget Views

struct EyeCareWidgetView: View {
    var entry: EyeCareWidgetEntry
    @Environment(\.widgetFamily) private var family

    var body: some View {
        switch family {
        case .systemSmall:
            smallView
        case .systemMedium:
            mediumView
        case .accessoryInline:
            inlineView
        case .accessoryCircular:
            circularView
        case .accessoryRectangular:
            rectangularView
        @unknown default:
            smallView
        }
    }

    private var smallView: some View {
        VStack(spacing: 6) {
            Image(systemName: entry.isActive ? "eyes" : "eye.slash")
                .font(.title)
                .foregroundColor(WidgetColor.primary)
            Text(entry.countdown)
                .font(.system(.title2, design: .monospaced).bold())
                .foregroundColor(WidgetColor.primary)
            Text(entry.stateLabel)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }

    private var mediumView: some View {
        HStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 4) {
                Text("Triple 2 Eye Protection")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.secondary)
                Text(entry.countdown)
                    .font(.system(.largeTitle, design: .monospaced).bold())
                    .foregroundColor(WidgetColor.primary)
                Text(entry.stateLabel)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 4) {
                Text("今日休息")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Text("\(entry.restCount24h)")
                    .font(.title.bold())
                    .foregroundColor(WidgetColor.primary)
                Text("次")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.horizontal, 4)
    }

    private var inlineView: some View {
        HStack(spacing: 4) {
            Image(systemName: entry.isActive ? "eyes" : "eye.slash")
            Text("\(entry.countdown) · \(entry.stateLabel)")
        }
    }

    private var circularView: some View {
        Gauge(value: entry.isActive ? 0.5 : 0, in: 0...1) {
            Image(systemName: "eyes")
        } currentValueLabel: {
            Text(entry.countdown)
                .font(.system(size: 8, design: .monospaced))
        }
        .gaugeStyle(.accessoryCircular)
        .tint(WidgetColor.primary)
    }

    private var rectangularView: some View {
        HStack(spacing: 8) {
            VStack(alignment: .leading, spacing: 2) {
                Text(entry.stateLabel)
                    .font(.headline)
                Text(entry.countdown)
                    .font(.title2.monospaced())
                    .foregroundColor(WidgetColor.primary)
            }
            Spacer()
            Text("今日\(entry.restCount24h)次")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}
