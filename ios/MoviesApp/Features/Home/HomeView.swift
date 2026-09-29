import SwiftUI

/// LOCAL-0 — Home screen with exact Figma Movies app posters.
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
                VStack(alignment: .leading, spacing: 24) {
                    header
                    SearchFieldButton(placeholder: "Search") {
                        router.openSearch()
                    }
                    featuredSection
                    categorySection
                    catalogSection
                }
                .padding(.horizontal, Theme.spacing)
                .padding(.bottom, Theme.spacing)
            }
            .background(Theme.background)
            .navigationBarHidden(true)
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
                .font(Theme.poppins(size: 18, weight: .semibold))
                .foregroundStyle(Theme.textPrimary)
                .accessibilityAddTraits(.isHeader)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.top, 12)
        .padding(.bottom, 4)
    }

    @ViewBuilder
    private var featuredSection: some View {
        if !viewModel.featuredMovies.isEmpty {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(alignment: .bottom, spacing: 24) {
                    ForEach(Array(viewModel.featuredMovies.enumerated()), id: \.element.id) { index, movie in
                        featuredCard(movie, rank: index + 1)
                    }
                }
                .padding(.leading, 12)
                .padding(.trailing, Theme.spacing)
                .padding(.bottom, 12)
            }
            .padding(.horizontal, -Theme.spacing)
        }
    }

    private func featuredCard(_ movie: Movie, rank: Int) -> some View {
        ZStack(alignment: .bottomLeading) {
            MoviePosterImage(movie: movie)
                .frame(width: 145, height: 210)
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            Text("\(rank)")
                .font(Theme.montserrat(size: 72, weight: .bold))
                .foregroundStyle(Theme.background)
                .overlay {
                    Text("\(rank)")
                        .font(Theme.montserrat(size: 72, weight: .bold))
                        .foregroundStyle(.clear)
                        .shadow(color: Theme.textSecondary.opacity(0.9), radius: 0.5)
                }
                .offset(x: -18, y: 22)
        }
        .frame(width: 145, height: 232, alignment: .top)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(rank). \(movie.title)")
    }

    private var categorySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Category")
                .font(Theme.poppins(size: 16, weight: .semibold))
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
                .font(Theme.poppins(size: 14, weight: isSelected ? .semibold : .regular))
                .foregroundStyle(isSelected ? Theme.textPrimary : Theme.textSecondary)
                .padding(.horizontal, 20)
                .padding(.vertical, 10)
                .background(isSelected ? Theme.primary : Theme.surface)
                .overlay {
                    if !isSelected {
                        Capsule(style: .continuous)
                            .stroke(Theme.card, lineWidth: 1)
                    }
                }
                .clipShape(Capsule())
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(isSelected ? .isSelected : [])
    }

    @ViewBuilder
    private var catalogSection: some View {
        VStack(alignment: .leading, spacing: 12) {
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
                    "No movies",
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
