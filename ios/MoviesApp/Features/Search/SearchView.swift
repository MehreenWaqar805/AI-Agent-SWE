import SwiftUI

/// SCRUM-2 / TM-202 — implement from Figma Search.
struct SearchView: View {
    @State private var viewModel = SearchViewModel()

    var body: some View {
        NavigationStack {
            ContentUnavailableView(
                "Search",
                systemImage: "magnifyingglass",
                description: Text("Implement SCRUM-2 from Figma.")
            )
            .navigationTitle("Search")
        }
    }
}

#Preview {
    SearchView()
}
