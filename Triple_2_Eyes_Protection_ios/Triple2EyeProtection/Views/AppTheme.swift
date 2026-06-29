import SwiftUI

/// Shared design constants — mirrors the Android color palette from MainActivity.java.
enum AppTheme {
    /// rgb(31, 122, 77) — the signature green
    static let primary = Color(red: 0.12, green: 0.48, blue: 0.30)
    /// rgb(245, 249, 247)
    static let background = Color(red: 0.96, green: 0.98, blue: 0.97)
    static let textPrimary = Color(red: 0.13, green: 0.15, blue: 0.14)
    static let textSecondary = Color(red: 0.35, green: 0.40, blue: 0.38)
    static let restBackground = Color(red: 0.94, green: 1.0, blue: 0.96)

    // MARK: - Button Styles

    struct PrimaryButton: ButtonStyle {
        func makeBody(configuration: Configuration) -> some View {
            configuration.label
                .font(.body.weight(.semibold))
                .foregroundColor(.white)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(primary)
                        .scaleEffect(configuration.isPressed ? 0.975 : 1.0)
                        .opacity(configuration.isPressed ? 0.85 : 1.0)
                )
                .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
        }
    }

    struct OutlineButton: ButtonStyle {
        func makeBody(configuration: Configuration) -> some View {
            configuration.label
                .font(.body.weight(.medium))
                .foregroundColor(primary)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(primary, lineWidth: 1.5)
                        .scaleEffect(configuration.isPressed ? 0.975 : 1.0)
                        .opacity(configuration.isPressed ? 0.7 : 1.0)
                )
                .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
        }
    }

    struct DangerButton: ButtonStyle {
        func makeBody(configuration: Configuration) -> some View {
            configuration.label
                .font(.body.weight(.medium))
                .foregroundColor(.red)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.red.opacity(0.5), lineWidth: 1.5)
                        .scaleEffect(configuration.isPressed ? 0.975 : 1.0)
                )
                .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
        }
    }

    struct RestDoneButton: ButtonStyle {
        func makeBody(configuration: Configuration) -> some View {
            configuration.label
                .font(.body.weight(.semibold))
                .foregroundColor(.white)
                .frame(height: 54)
                .frame(maxWidth: .infinity)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(primary)
                        .scaleEffect(configuration.isPressed ? 0.97 : 1.0)
                        .opacity(configuration.isPressed ? 0.85 : 1.0)
                )
                .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
        }
    }

    // Convenience
    static let primaryButton = PrimaryButton()
    static let outlineButton = OutlineButton()
    static let dangerButton = DangerButton()
    static let restDoneButton = RestDoneButton()
}
