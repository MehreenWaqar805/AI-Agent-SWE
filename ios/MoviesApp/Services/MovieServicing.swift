import Foundation

protocol MovieServicing: Sendable {
    func trending() async throws -> [Movie]
    func search(query: String) async throws -> [Movie]
}

struct PreviewMovieService: MovieServicing {
    func trending() async throws -> [Movie] {
        [
            Movie(
                id: 1,
                title: "Dune: Part Two",
                overview: "Paul Atreides unites with the Fremen.",
                posterPath: nil,
                voteAverage: 8.7
            ),
            Movie(
                id: 2,
                title: "Oppenheimer",
                overview: "The story of American scientist J. Robert Oppenheimer.",
                posterPath: nil,
                voteAverage: 8.4
            ),
            Movie(
                id: 3,
                title: "Poor Things",
                overview: "The incredible tale of Bella Baxter.",
                posterPath: nil,
                voteAverage: 8.0
            ),
            Movie(
                id: 4,
                title: "The Batman",
                overview: "Batman ventures into Gotham's underworld.",
                posterPath: nil,
                voteAverage: 7.8
            ),
            Movie(
                id: 5,
                title: "Barbie",
                overview: "Barbie suffers a crisis that leads her to question her world.",
                posterPath: nil,
                voteAverage: 7.2
            ),
            Movie(
                id: 6,
                title: "Killers of the Flower Moon",
                overview: "Members of the Osage tribe are murdered under mysterious circumstances.",
                posterPath: nil,
                voteAverage: 7.7
            ),
        ]
    }

    func search(query: String) async throws -> [Movie] {
        let all = try await trending()
        guard !query.isEmpty else { return all }
        return all.filter { $0.title.localizedCaseInsensitiveContains(query) }
    }
}
