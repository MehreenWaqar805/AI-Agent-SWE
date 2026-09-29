import SwiftUI

/// SCRUM-4 / TM-204 — implement from Figma Movie Rating.
struct RatingView: View {
    @State private var viewModel = RatingViewModel()

    var body: some View {
        NavigationStack {
            ContentUnavailableView(
                "Rating",
                systemImage: "star",
                description: Text("Implement SCRUM-4 from Figma.")
            )
            .navigationTitle("Rating")
        }
    }
}

#Preview {
    RatingView()
}
