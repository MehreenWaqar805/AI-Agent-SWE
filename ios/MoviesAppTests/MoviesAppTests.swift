import XCTest
@testable import MoviesApp

final class MoviesAppTests: XCTestCase {
    func testMovieIdentity() {
        let movie = Movie(id: 42, title: "Dune", overview: "", posterPath: nil, voteAverage: 8.5)
        XCTAssertEqual(movie.id, 42)
        XCTAssertEqual(movie.title, "Dune")
    }
}
