import Foundation
import ActivityKit

/// Manages the Live Activity shown in the Dynamic Island and Lock Screen.
/// Replaces the Android persistent status notification and quick-settings tile.
final class LiveActivityManager: @unchecked Sendable {
    static let shared = LiveActivityManager()

    private var currentActivity: Activity<EyeCareActivityAttributes>?

    private init() {}

    // MARK: - Start

    @MainActor
    func startIfNeeded(settings: AppSettings, remainingMs: Int64) {
        guard ActivityAuthorizationInfo().areActivitiesEnabled else { return }
        guard currentActivity == nil else {
            update(settings: settings, remainingMs: remainingMs)
            return
        }

        let state = settings.state
        let attributes = EyeCareActivityAttributes()
        let contentState = makeContentState(settings: settings, remainingMs: remainingMs)

        do {
            let activity = try Activity<EyeCareActivityAttributes>.request(
                attributes: attributes,
                contentState: contentState,
                pushType: nil
            )
            currentActivity = activity
        } catch {
            // Live Activity could not be started — non-critical.
        }
    }

    // MARK: - Update

    @MainActor
    func update(settings: AppSettings, remainingMs: Int64) {
        guard let activity = currentActivity else {
            startIfNeeded(settings: settings, remainingMs: remainingMs)
            return
        }

        let contentState = makeContentState(settings: settings, remainingMs: remainingMs)

        Task {
            await activity.update(using: contentState)
        }
    }

    // MARK: - End

    @MainActor
    func endAll() async {
        guard let activity = currentActivity else { return }
        let finalState = makeContentState(settings: AppSettings.shared, remainingMs: 0)
        await activity.end(using: finalState, dismissalPolicy: .immediate)
        currentActivity = nil
    }

    // MARK: - Helpers

    private func makeContentState(settings: AppSettings, remainingMs: Int64) -> EyeCareActivityAttributes.ContentState {
        let isResting: Bool
        let isWorking: Bool
        if case .resting = settings.state { isResting = true; isWorking = false }
        else if case .working = settings.state { isResting = false; isWorking = true }
        else { isResting = false; isWorking = false }

        return EyeCareActivityAttributes.ContentState(
            stateLabel: settings.stateLabel(settings.state),
            countdown: AppSettings.formatRemaining(remainingMs),
            isResting: isResting,
            isWorking: isWorking,
            workMinutes: settings.workMinutes,
            restSeconds: settings.restSeconds
        )
    }
}
