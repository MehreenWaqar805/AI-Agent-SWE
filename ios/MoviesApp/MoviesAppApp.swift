import SwiftUI
import UIKit

@main
struct MoviesAppApp: App {
    init() {
        Self.applyTabBarAppearance()
    }

    var body: some Scene {
        WindowGroup {
            AppCoordinatorView()
                .preferredColorScheme(.dark)
        }
    }

    /// Figma `Tabbar14`: dark bar, primary selected tint, muted icons.
    private static func applyTabBarAppearance() {
        let appearance = UITabBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundColor = UIColor(Theme.surface)
        appearance.shadowColor = UIColor.black.withAlphaComponent(0.35)

        let normal = UIColor(Theme.iconMuted)
        let selected = UIColor(Theme.primary)
        [appearance.stackedLayoutAppearance, appearance.inlineLayoutAppearance, appearance.compactInlineLayoutAppearance]
            .forEach { item in
                item.normal.iconColor = normal
                item.normal.titleTextAttributes = [.foregroundColor: normal]
                item.selected.iconColor = selected
                item.selected.titleTextAttributes = [.foregroundColor: selected]
            }

        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
    }
}
