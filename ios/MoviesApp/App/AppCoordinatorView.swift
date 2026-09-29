import SwiftUI

/// Root coordinator. The agent implements Jira screens as tab destinations.
struct AppCoordinatorView: View {
    @State private var router = AppRouter()

    var body: some View {
        TabView(selection: $router.selectedTab) {
            HomeView()
                .tabItem { Label("Home", systemImage: "house.fill") }
                .tag(AppTab.home)
            SearchView()
                .tabItem { Label("Search", systemImage: "magnifyingglass") }
                .tag(AppTab.search)
            WishlistView()
                .tabItem { Label("Saved", systemImage: "bookmark.fill") }
                .tag(AppTab.wishlist)
            RatingView()
                .tabItem { Label("Rating", systemImage: "star.fill") }
                .tag(AppTab.rating)
        }
        .tint(Theme.primary)
        .environment(router)
    }
}
