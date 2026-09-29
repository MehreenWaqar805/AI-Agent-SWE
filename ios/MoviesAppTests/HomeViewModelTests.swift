import XCTest
@testable import MoviesApp

private struct StubMovieService: MovieServicing {
    let result: Result<[Movie], Error>

    func trending() async throws -> [Movie] {
        try result.get()
    }

    func search(query: String) async throws -> [Movie] {
        try await trending()
    }
}

@MainActor
final class HomeViewModelTests: XCTestCase {
    func testLoadTrendingPopulatesMovies() async {
        let expected = [
            Movie(id: 1, title: "Dune", overview: "", posterPath: nil, voteAverage: 8.5),
        ]
        let viewModel = HomeViewModel(movieService: StubMovieService(result: .success(expected)))

        await viewModel.loadTrending()

        XCTAssertEqual(viewModel.movies, expected)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }

    func testLoadTrendingSetsErrorOnFailure() async {
        let viewModel = HomeViewModel(
            movieService: StubMovieService(result: .failure(URLError(.notConnectedToInternet)))
        )

        await viewModel.loadTrending()

        XCTAssertTrue(viewModel.movies.isEmpty)
        XCTAssertNotNil(viewModel.errorMessage)
        XCTAssertFalse(viewModel.isLoading)
    }

    func testSelectCategoryUpdatesSelection() {
        let viewModel = HomeViewModel(categories: ["Action", "Comedy"])

        viewModel.selectCategory("Comedy")

        XCTAssertEqual(viewModel.selectedCategory, "Comedy")
    }
}
