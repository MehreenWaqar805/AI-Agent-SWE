import Foundation

protocol MovieServicing: Sendable {
    func trending() async throws -> [Movie]
    func search(query: String) async throws -> [Movie]
}

/// LOCAL-0 — catalog built from exact Figma Movies app (Community) posters.
struct PreviewMovieService: MovieServicing {
    func trending() async throws -> [Movie] {
        FigmaHomeCatalog.movies
    }

    func search(query: String) async throws -> [Movie] {
        let all = try await trending()
        guard !query.isEmpty else { return all }
        return all.filter { $0.title.localizedCaseInsensitiveContains(query) }
    }
}

enum FigmaHomeCatalog {
    static let nowPlaying = "Now playing"
    static let upcoming = "Upcoming"
    static let topRated = "Top rated"
    static let popular = "Popular"

    static let categories = [nowPlaying, upcoming, topRated, popular]

    static let movies: [Movie] = [
        Movie(
            id: 1,
            title: "Jurassic World Dominion",
            overview: "Four years after Isla Nublar, dinosaurs now live alongside humans.",
            posterPath: nil,
            posterAssetName: "PosterJurassicWorld",
            voteAverage: 7.0,
            categories: [nowPlaying, upcoming, topRated]
        ),
        Movie(
            id: 2,
            title: "Spider-Man: No Way Home",
            overview: "Peter Parker seeks Doctor Strange's help after his identity is revealed.",
            posterPath: nil,
            posterAssetName: "PosterSpidermanNoWayHome",
            voteAverage: 8.3,
            categories: [nowPlaying, topRated, popular]
        ),
        Movie(
            id: 3,
            title: "Sonic the Hedgehog 2",
            overview: "Sonic teams up with Tails to stop Dr. Robotnik and Knuckles.",
            posterPath: nil,
            posterAssetName: "PosterSonic2",
            voteAverage: 6.8,
            categories: [upcoming, popular]
        ),
        Movie(
            id: 4,
            title: "Doctor Strange in the Multiverse of Madness",
            overview: "Doctor Strange walks a dangerous path in the multiverse.",
            posterPath: nil,
            posterAssetName: "PosterDoctorStrange",
            voteAverage: 7.0,
            categories: [nowPlaying, topRated]
        ),
        Movie(
            id: 5,
            title: "Avengers: Endgame",
            overview: "The Avengers assemble once more to reverse Thanos' snap.",
            posterPath: nil,
            posterAssetName: "PosterAvengersEndgame",
            voteAverage: 8.4,
            categories: [nowPlaying, topRated, popular]
        ),
        Movie(
            id: 6,
            title: "Fantastic Beasts: The Secrets of Dumbledore",
            overview: "Dumbledore tasks Newt and his allies with a dangerous mission.",
            posterPath: nil,
            posterAssetName: "PosterSecretsOfDumbledore",
            voteAverage: 6.2,
            categories: [nowPlaying, upcoming]
        ),
        Movie(
            id: 7,
            title: "The Lost City",
            overview: "A reclusive author is swept into an adventure modeled on her novels.",
            posterPath: nil,
            posterAssetName: "PosterTheLostCity",
            voteAverage: 6.6,
            categories: [popular, upcoming]
        ),
        Movie(
            id: 8,
            title: "Shark Bait",
            overview: "A group of friends is hunted after a luxury yacht day goes wrong.",
            posterPath: nil,
            posterAssetName: "PosterSharkBait",
            voteAverage: 5.1,
            categories: [upcoming, popular]
        ),
        Movie(
            id: 9,
            title: "Dog",
            overview: "A soldier transports a military working dog on an unexpected road trip.",
            posterPath: nil,
            posterAssetName: "PosterDog",
            voteAverage: 7.2,
            categories: [nowPlaying, popular]
        ),
    ]
}
