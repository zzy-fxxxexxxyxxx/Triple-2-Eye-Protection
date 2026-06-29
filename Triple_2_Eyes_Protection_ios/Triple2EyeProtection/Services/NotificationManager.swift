import Foundation
import UserNotifications

/// Manages local notification scheduling — equivalent to the Android notification
/// channels and AlarmManager-based notification delivery in EyeCareService.java.
final class NotificationManager: NSObject, @unchecked Sendable {
    static let shared = NotificationManager()

    private let center = UNUserNotificationCenter.current()

    private override init() {
        super.init()
        center.delegate = self
    }

    func requestAuthorization() async -> Bool {
        do {
            return try await center.requestAuthorization(options: [.alert, .sound, .badge])
        } catch {
            return false
        }
    }

    /// Schedule a timed local notification (replaces exact-alarm-driven delivery).
    func schedule(title: String, body: String, at date: Date, identifier: String? = nil) {
        guard date.timeIntervalSinceNow > 0 else { return }

        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.categoryIdentifier = "eye_care_reminder"
        content.interruptionLevel = .timeSensitive

        let components = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute, .second], from: date)
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: false)

        let id = identifier ?? "eye_care_\(Int(date.timeIntervalSince1970))"
        let request = UNNotificationRequest(identifier: id, content: content, trigger: trigger)
        center.add(request)
    }

    /// Post an immediate local notification (replaces the rest-alert channel).
    func postImmediateAlert(title: String, body: String, identifier: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.categoryIdentifier = "rest_alert"
        content.interruptionLevel = .critical

        let request = UNNotificationRequest(identifier: identifier, content: content, trigger: nil)
        center.add(request)
    }

    func cancelAll() { center.removeAllPendingNotificationRequests() }

    func cancelWithPrefix(_ prefix: String) {
        center.getPendingNotificationRequests { requests in
            let ids = requests.filter { $0.identifier.hasPrefix(prefix) }.map(\.identifier)
            UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ids)
        }
    }

    func removeDelivered(withPrefix prefix: String) {
        center.getDeliveredNotifications { notifications in
            let ids = notifications.filter { $0.request.identifier.hasPrefix(prefix) }.map(\.request.identifier)
            UNUserNotificationCenter.current().removeDeliveredNotifications(withIdentifiers: ids)
        }
    }

    /// Register notification categories with actions (replace notification action buttons).
    func registerCategories() {
        let restDoneAction = UNNotificationAction(
            identifier: "REST_DONE",
            title: "休息好了",
            options: .foreground
        )
        let restCategory = UNNotificationCategory(
            identifier: "rest_alert",
            actions: [restDoneAction],
            intentIdentifiers: [],
            options: []
        )
        let reminderCategory = UNNotificationCategory(
            identifier: "eye_care_reminder",
            actions: [restDoneAction],
            intentIdentifiers: [],
            options: []
        )
        center.setNotificationCategories([restCategory, reminderCategory])
    }
}

// MARK: - UNUserNotificationCenterDelegate
extension NotificationManager: UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification
    ) async -> UNNotificationPresentationOptions {
        [.banner, .sound, .list]
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        if response.actionIdentifier == "REST_DONE" {
            await MainActor.run { EyeCareManager.shared.restDone() }
        }
    }
}
