import SwiftUI
import AudioToolbox

/// Port of RestActivity.java + the overlay in EyeCareService.java.
/// Full-screen rest reminder with countdown, fade-in, and "done" action.
struct RestOverlayView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject var manager: EyeCareManager

    @State private var opacity: Double = 0
    @State private var localRemaining: String = "00:00"

    private let timer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        ZStack {
            AppTheme.restBackground.ignoresSafeArea()

            VStack(spacing: 0) {
                Spacer()

                Image(systemName: "eyes")
                    .font(.system(size: 48))
                    .foregroundColor(AppTheme.primary)
                    .padding(.bottom, 24)

                Text("休息时间到了")
                    .font(.system(size: 30).weight(.bold))
                    .foregroundColor(AppTheme.primary)

                Text(restMessage)
                    .font(.system(size: 18))
                    .foregroundColor(AppTheme.textSecondary)
                    .padding(.top, 22)
                    .padding(.bottom, 18)

                Text(localRemaining)
                    .font(.system(size: 64, design: .monospaced).bold())
                    .foregroundColor(AppTheme.primary)

                Spacer()

                Button(action: {
                    vibrate()
                    manager.restDone()
                    isPresented = false
                }) {
                    Text("休息好了")
                }
                .buttonStyle(AppTheme.restDoneButton)
                .padding(.horizontal, 24)

                Spacer()
            }
            .padding(.horizontal, 24)
        }
        .opacity(opacity)
        .onAppear {
            localRemaining = manager.formattedRemaining
            withAnimation(.easeInOut(duration: TimeInterval(manager.fadeSeconds))) {
                opacity = 1
            }
        }
        .onReceive(timer) { _ in
            if manager.currentState != .resting {
                withAnimation(.easeOut(duration: 0.3)) { opacity = 0 }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { isPresented = false }
                return
            }
            localRemaining = manager.formattedRemaining
        }
    }

    private var restMessage: String {
        if manager.remainingMs <= 0 {
            return "休息时间已到，可以开始下一轮"
        }
        return "请离开屏幕，远望 6 米外"
    }

    private func vibrate() {
        guard manager.vibrateOnRest else { return }
        AudioServicesPlaySystemSound(kSystemSoundID_Vibrate)
    }
}
