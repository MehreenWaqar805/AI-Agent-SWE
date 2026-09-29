import SwiftUI

/// SCRUM-3 / TM-203 — implement from Figma Wishlist.
struct WishlistView: View {
    @State private var viewModel = WishlistViewModel()

    var body: some View {
        NavigationStack {
            ContentUnavailableView(
                "Wishlist",
                systemImage: "heart",
                description: Text("Implement SCRUM-3 from Figma.")
            )
            .navigationTitle("Wishlist")
        }
    }
}

#Preview {
    WishlistView()
}
