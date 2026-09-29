import Foundation

@Observable
final class SearchViewModel {
    var query = ""
    var results: [Movie] = []
    var isLoading = false
}
