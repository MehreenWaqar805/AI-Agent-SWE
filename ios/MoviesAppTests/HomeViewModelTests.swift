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
        XCTAssertTrue(viewModel.featuredMovies.isEmpty)
        XCTAssertNotNil(viewModel.errorMessage)
        XCTAssertFalse(viewModel.isLoading)
    }

    func testSelectCategoryUpdatesSelection() {
        let viewModel = HomeViewModel(categories: ["Action", "Comedy"])

        viewModel.selectCategory("Comedy")

        XCTAssertEqual(viewModel.selectedCategory, "Comedy")
    }

    func testLoadTrendingSkipsWhenAlreadyLoading() async {
        let slow = SlowMovieService(delayNanoseconds: 200_000_000)
        let viewModel = HomeViewModel(movieService: slow)

        async let first: Void = viewModel.loadTrending()
        async let second: Void = viewModel.loadTrending()
        await first
        await second

        let fetchCount = await slow.fetchCount
        XCTAssertEqual(fetchCount, 1)
    }

    func testLoadTrendingPopulatesFeaturedFromFigmaOrder() async {
        let catalog = (1...5).map { index in
            Movie(id: index, title: "M\(index)", overview: "", posterPath: nil, voteAverage: 8)
        }
        let viewModel = HomeViewModel(movieService: StubMovieService(result: .success(catalog)))

        await viewModel.loadTrending()

        XCTAssertEqual(viewModel.featuredMovies.map(\.id), [1, 2, 3])
    }

    func testSelectCategoryFiltersCatalog() async {
        let catalog = [
            Movie(
                id: 1,
                title: "Now",
                overview: "",
                posterPath: nil,
                posterAssetName: "PosterJurassicWorld",
                voteAverage: 7,
                categories: ["Now playing"]
            ),
            Movie(
                id: 2,
                title: "Later",
                overview: "",
                posterPath: nil,
                posterAssetName: "PosterSonic2",
                voteAverage: 6,
                categories: ["Upcoming"]
            ),
        ]
        let viewModel = HomeViewModel(
            movieService: StubMovieService(result: .success(catalog)),
            categories: ["Now playing", "Upcoming"]
        )

        await viewModel.loadTrending()
        XCTAssertEqual(viewModel.movies.map(\.id), [1])

        viewModel.selectCategory("Upcoming")
        XCTAssertEqual(viewModel.movies.map(\.id), [2])
    }

    func testFigmaCatalogSuppliesExactPosterAssets() async throws {
        let movies = try await PreviewMovieService().trending()

        XCTAssertFalse(movies.isEmpty)
        XCTAssertTrue(movies.allSatisfy { movie in
            guard let name = movie.posterAssetName else { return false }
            return name.hasPrefix("Poster")
        })
        XCTAssertEqual(movies.prefix(3).compactMap(\.posterAssetName), [
            "PosterJurassicWorld",
            "PosterSpidermanNoWayHome",
            "PosterSonic2",
        ])
    }
}

private actor SlowMovieService: MovieServicing {
    private(set) var fetchCount = 0
    let delayNanoseconds: UInt64

    init(delayNanoseconds: UInt64) {
        self.delayNanoseconds = delayNanoseconds
    }

    func trending() async throws -> [Movie] {
        fetchCount += 1
        try await Task.sleep(nanoseconds: delayNanoseconds)
        return [Movie(id: 1, title: "Slow", overview: "", posterPath: nil, voteAverage: 7)]
    }

    func search(query: String) async throws -> [Movie] {
        try await trending()
    }
}
