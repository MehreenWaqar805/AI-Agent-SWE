import SwiftUI

/// SCRUM-1 / TM-201 — Home screen (Figma Movies app).
struct HomeView: View {
    @Environment(AppRouter.self) private var router
    @State private var viewModel = HomeViewModel()

    private let gridColumns = [
        GridItem(.flexible(), spacing: Theme.spacing),
        GridItem(.flexible(), spacing: Theme.spacing),
    ]

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: Theme.spacing) {
                    header
                    SearchFieldButton(placeholder: "Search movies") {
                        router.openSearch()
                    }
                    categorySection
                    trendingSection
                }
                .padding(.horizontal, Theme.spacing)
                .padding(.bottom, Theme.spacing)
            }
            .background(Theme.background)
            .navigationBarTitleDisplayMode(.inline)
            .toolbarBackground(Theme.background, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
            .task {
                await viewModel.loadTrending()
            }
            .refreshable {
                await viewModel.loadTrending()
            }
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("What do you want to watch?")
                .font(Theme.titleFont(size: 20))
                .foregroundStyle(Theme.textPrimary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.top, 8)
    }

    private var categorySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Category")
                .font(Theme.titleFont(size: 16))
                .foregroundStyle(Theme.textPrimary)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(viewModel.categories, id: \.self) { category in
                        categoryChip(category)
                    }
                }
            }
        }
    }

    private func categoryChip(_ category: String) -> some View {
        let isSelected = viewModel.selectedCategory == category
        return Button {
            viewModel.selectCategory(category)
        } label: {
            Text(category)
                .font(Theme.bodyFont(size: 14))
                .foregroundStyle(isSelected ? Theme.textPrimary : Theme.textSecondary)
                .padding(.horizontal, 20)
                .padding(.vertical, 10)
                .background(isSelected ? Theme.primary.opacity(0.25) : Theme.surface)
                .overlay {
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .stroke(isSelected ? Theme.primary : Theme.card, lineWidth: 1)
                }
                .clipShape(Capsule())
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(isSelected ? .isSelected : [])
    }

    @ViewBuilder
    private var trendingSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Trending")
                .font(Theme.titleFont(size: 16))
                .foregroundStyle(Theme.textPrimary)

            if viewModel.isLoading && viewModel.movies.isEmpty {
                ProgressView()
                    .tint(Theme.primary)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 40)
            } else if let errorMessage = viewModel.errorMessage {
                ContentUnavailableView {
                    Label("Could not load movies", systemImage: "wifi.exclamationmark")
                } description: {
                    Text(errorMessage)
                } actions: {
                    Button("Try again") {
                        Task { await viewModel.loadTrending() }
                    }
                    .tint(Theme.primary)
                }
            } else if viewModel.movies.isEmpty {
                ContentUnavailableView(
                    "No trending movies",
                    systemImage: "film",
                    description: Text("Pull to refresh.")
                )
            } else {
                LazyVGrid(columns: gridColumns, spacing: Theme.spacing) {
                    ForEach(viewModel.movies) { movie in
                        MoviePosterCard(movie: movie)
                    }
                }
            }
        }
    }
}

#Preview {
    HomeView()
        .environment(AppRouter())
}
