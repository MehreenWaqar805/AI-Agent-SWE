import SwiftUI

enum Theme {
    // Figma Movies app (Community) tokens
    static let primary = Color(red: 2 / 255, green: 150 / 255, blue: 229 / 255) // #0296e5
    static let accent = primary
    static let background = Color(red: 36 / 255, green: 42 / 255, blue: 50 / 255) // #242a32
    static let surface = Color(red: 37 / 255, green: 40 / 255, blue: 54 / 255) // #252836
    static let card = Color(red: 58 / 255, green: 63 / 255, blue: 71 / 255) // #3a3f47
    static let textPrimary = Color.white
    static let textSecondary = Color(red: 146 / 255, green: 146 / 255, blue: 157 / 255) // #92929d
    static let ratingStar = Color(red: 251 / 255, green: 199 / 255, blue: 0 / 255) // #fbc700

    static let cornerRadius: CGFloat = 16
    static let spacing: CGFloat = 16
    static let posterCornerRadius: CGFloat = 12

    static func titleFont(size: CGFloat = 18) -> Font {
        .system(size: size, weight: .semibold, design: .rounded)
    }

    static func bodyFont(size: CGFloat = 14) -> Font {
        .system(size: size, weight: .regular, design: .rounded)
    }

    static func captionFont(size: CGFloat = 12) -> Font {
        .system(size: size, weight: .medium, design: .rounded)
    }
}
