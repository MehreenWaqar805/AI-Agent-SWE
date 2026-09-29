import Foundation

@Observable
final class HomeViewModel {
    var featuredMovies: [Movie] = []
    var movies: [Movie] = []
    var isLoading = false
    var errorMessage: String?
    var selectedCategory: String

    let categories: [String]

    private var catalog: [Movie] = []
    private let movieService: any MovieServicing
    private let featuredLimit = 3

    init(
        movieService: any MovieServicing = PreviewMovieService(),
        categories: [String] = FigmaHomeCatalog.categories
    ) {
        self.movieService = movieService
        self.categories = categories
        selectedCategory = categories.first ?? FigmaHomeCatalog.nowPlaying
    }

    @MainActor
    func loadTrending() async {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let all = try await movieService.trending()
            featuredMovies = Array(all.prefix(featuredLimit))
            catalog = all
            applyCategoryFilter()
        } catch {
            errorMessage = error.localizedDescription
            featuredMovies = []
            catalog = []
            movies = []
        }
    }

    func selectCategory(_ category: String) {
        selectedCategory = category
        applyCategoryFilter()
    }

    private func applyCategoryFilter() {
        movies = catalog.filter { movie in
            movie.categories.isEmpty || movie.categories.contains(selectedCategory)
        }
    }
}
