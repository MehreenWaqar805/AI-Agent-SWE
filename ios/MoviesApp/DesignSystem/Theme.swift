import SwiftUI

enum Theme {
    // Figma Movies app (Community) — SCRUM-1 / TM-201
    static let primary = Color(red: 2 / 255, green: 150 / 255, blue: 229 / 255) // #0296e5
    static let accent = primary
    static let headerBackground = Color(red: 20 / 255, green: 20 / 255, blue: 43 / 255) // #14142b
    static let background = Color(red: 36 / 255, green: 42 / 255, blue: 50 / 255) // #242a32
    static let surface = Color(red: 37 / 255, green: 40 / 255, blue: 54 / 255) // #252836
    static let card = Color(red: 58 / 255, green: 63 / 255, blue: 71 / 255) // #3a3f47
    static let iconMuted = Color(red: 103 / 255, green: 104 / 255, blue: 109 / 255) // #67686d
    static let textPrimary = Color.white // #ffffff
    static let textSecondary = Color(red: 146 / 255, green: 146 / 255, blue: 157 / 255) // #92929d
    static let ratingStar = Color(red: 251 / 255, green: 199 / 255, blue: 0 / 255) // #fbc700

    static let cornerRadius: CGFloat = 16
    static let spacing: CGFloat = 16
    static let posterCornerRadius: CGFloat = 12
    static let tabBarHeight: CGFloat = 72

    /// Poppins (Figma) — system rounded substitute until custom fonts are bundled.
    static func poppins(size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .rounded)
    }

    /// Montserrat (Figma) — used for large display numerics in rating flows.
    static func montserrat(size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .default)
    }

    static func titleFont(size: CGFloat = 18) -> Font {
        poppins(size: size, weight: .semibold)
    }

    static func bodyFont(size: CGFloat = 14) -> Font {
        poppins(size: size, weight: .regular)
    }

    static func captionFont(size: CGFloat = 12) -> Font {
        poppins(size: size, weight: .medium)
    }
}
