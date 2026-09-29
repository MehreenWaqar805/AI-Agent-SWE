import Foundation

struct Movie: Identifiable, Hashable, Codable {
    let id: Int
    var title: String
    var overview: String
    var posterPath: String?
    var voteAverage: Double
}
