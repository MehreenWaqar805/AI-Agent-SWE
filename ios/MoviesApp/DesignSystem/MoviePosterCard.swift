import SwiftUI

struct MoviePosterCard: View {
    let movie: Movie

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            poster
            Text(movie.title)
                .font(Theme.bodyFont(size: 14))
                .foregroundStyle(Theme.textPrimary)
                .lineLimit(2)
                .multilineTextAlignment(.leading)
            HStack(spacing: 4) {
                Image(systemName: "star.fill")
                    .font(.caption2)
                    .foregroundStyle(Theme.ratingStar)
                Text(String(format: "%.1f", movie.voteAverage))
                    .font(Theme.captionFont())
                    .foregroundStyle(Theme.textSecondary)
            }
        }
    }

    private var poster: some View {
        RoundedRectangle(cornerRadius: Theme.posterCornerRadius, style: .continuous)
            .fill(
                LinearGradient(
                    colors: [Theme.card, Theme.surface],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .aspectRatio(2 / 3, contentMode: .fit)
            .overlay {
                Image(systemName: "film")
                    .font(.title2)
                    .foregroundStyle(Theme.textSecondary.opacity(0.6))
            }
            .accessibilityLabel("\(movie.title) poster")
    }
}

#Preview {
    MoviePosterCard(
        movie: Movie(id: 1, title: "Dune: Part Two", overview: "", posterPath: nil, voteAverage: 8.7)
    )
    .frame(width: 160)
    .padding()
    .background(Theme.background)
}
