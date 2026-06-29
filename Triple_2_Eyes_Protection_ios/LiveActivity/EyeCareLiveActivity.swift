import ActivityKit
import WidgetKit
import SwiftUI

// MARK: - Activity Attributes

struct EyeCareActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var stateLabel: String
        var countdown: String
        var isResting: Bool
        var isWorking: Bool
        var workMinutes: Int
        var restSeconds: Int
    }
}

// MARK: - Live Activity Configuration

struct EyeCareLiveActivity: Widget {
    private let primaryColor = Color(red: 0.12, green: 0.48, blue: 0.30)

    var body: some WidgetConfiguration {
        ActivityConfiguration(for: EyeCareActivityAttributes.self) { context in
            // Lock Screen / Banner
            HStack(spacing: 12) {
                Image(systemName: context.state.isResting ? "eye" : "eyes")
                    .font(.title)
                    .foregroundColor(primaryColor)

                VStack(alignment: .leading, spacing: 2) {
                    Text(context.state.stateLabel)
                        .font(.headline)
                        .foregroundColor(.primary)
                    Text(context.state.isResting
                         ? "请远望6米外放松双眼"
                         : "护眼倒计时进行中")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Text(context.state.countdown)
                    .font(.system(.title, design: .monospaced).bold())
                    .foregroundColor(primaryColor)
            }
            .padding()
            .activityBackgroundTint(Color(.systemGray6))
            .activitySystemActionForegroundColor(.white)

        } dynamicIsland: { context in
            DynamicIsland {
                // Expanded — when user long-presses
                DynamicIslandExpandedRegion(.leading) {
                    HStack(spacing: 4) {
                        Image(systemName: context.state.isResting ? "eye" : "eyes")
                            .foregroundColor(primaryColor)
                        Text(context.state.stateLabel)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text(context.state.countdown)
                        .font(.system(.title3, design: .monospaced).bold())
                        .foregroundColor(primaryColor)
                }
                DynamicIslandExpandedRegion(.center) {
                    if context.state.isResting {
                        Label("远望放松中", systemImage: "figure.mind.and.body")
                            .font(.caption)
                    } else {
                        Label("用眼中·\(context.state.workMinutes)分钟", systemImage: "timer")
                            .font(.caption)
                    }
                }
                DynamicIslandExpandedRegion(.bottom) {
                    HStack(spacing: 16) {
                        Label("工作 \(context.state.workMinutes)min", systemImage: "deskclock")
                        Label("休息 \(context.state.restSeconds)s", systemImage: "bed.double")
                    }
                    .font(.caption2)
                    .foregroundColor(.secondary)
                }
            } compactLeading: {
                // Compact leading — icon + countdown
                HStack(spacing: 2) {
                    Image(systemName: context.state.isResting ? "eye" : "eyes")
                        .font(.caption2)
                        .foregroundColor(primaryColor)
                    Text(context.state.countdown)
                        .font(.caption2)
                        .monospacedDigit()
                }
            } compactTrailing: {
                // Compact trailing — progress indicator
                ProgressView(value: context.state.isResting ? 1 : 0.5, total: 1.0)
                    .progressViewStyle(.circular)
                    .tint(context.state.isResting ? .orange : primaryColor)
                    .scaleEffect(0.7)
            } minimal: {
                // Minimal — just an icon
                Image(systemName: context.state.isResting ? "eye" : "eyes")
                    .foregroundColor(context.state.isResting ? .orange : primaryColor)
            }
        }
    }
}
