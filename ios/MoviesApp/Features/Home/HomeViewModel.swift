import Foundation

@Observable
final class HomeViewModel {
    var movies: [Movie] = []
    var isLoading = false
    var errorMessage: String?
    var selectedCategory: String

    let categories: [String]

    private let movieService: any MovieServicing

    init(
        movieService: any MovieServicing = PreviewMovieService(),
        categories: [String] = ["Action", "Comedy", "Drama", "Horror"]
    ) {
        self.movieService = movieService
        self.categories = categories
        selectedCategory = categories.first ?? "Action"
    }

    @MainActor
    func loadTrending() async {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            movies = try await movieService.trending()
        } catch {
            errorMessage = error.localizedDescription
            movies = []
        }
    }

    func selectCategory(_ category: String) {
        selectedCategory = category
    }
}
