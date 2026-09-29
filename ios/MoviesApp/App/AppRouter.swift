import Foundation

enum AppTab: Hashable {
    case home
    case search
    case wishlist
    case rating
}

@Observable
final class AppRouter {
    var selectedTab: AppTab = .home

    func openSearch() {
        selectedTab = .search
    }
}
