import SwiftUI

@main
struct Triple2EyeProtectionApp: App {
    @Environment(\.scenePhase) private var scenePhase
    @StateObject private var eyeCareManager = EyeCareManager.shared

    init() {
        // Register notification categories on launch
        NotificationManager.shared.registerCategories()
        // Request notification authorization
        Task {
            _ = await NotificationManager.shared.requestAuthorization()
        }
        // Restore state on boot (equivalent to BootReceiver + ACTION_BOOT)
        EyeCareManager.shared.refreshFromPrefs()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(eyeCareManager)
                .onAppear {
                    eyeCareManager.refreshFromPrefs()
                }
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            switch newPhase {
            case .active:
                eyeCareManager.sceneDidBecomeActive()
            case .inactive:
                eyeCareManager.sceneWillResignActive()
            case .background:
                eyeCareManager.sceneDidEnterBackground()
            @unknown default:
                break
            }
        }
    }
}
