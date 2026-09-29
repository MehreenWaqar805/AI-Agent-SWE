import SwiftUI

struct MoviePosterImage: View {
    let movie: Movie

    var body: some View {
        Group {
            if let name = movie.posterAssetName, !name.isEmpty {
                Image(name)
                    .resizable()
                    .scaledToFill()
            } else {
                RoundedRectangle(cornerRadius: Theme.posterCornerRadius, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [Theme.card, Theme.surface],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .overlay {
                        Image(systemName: "film")
                            .font(.title2)
                            .foregroundStyle(Theme.textSecondary.opacity(0.6))
                    }
            }
        }
        .accessibilityLabel("\(movie.title) poster")
    }
}

struct MoviePosterCard: View {
    let movie: Movie

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            MoviePosterImage(movie: movie)
                .aspectRatio(2 / 3, contentMode: .fit)
                .clipShape(RoundedRectangle(cornerRadius: Theme.posterCornerRadius, style: .continuous))
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
}

#Preview {
    MoviePosterCard(
        movie: Movie(
            id: 1,
            title: "Spider-Man: No Way Home",
            overview: "",
            posterPath: nil,
            posterAssetName: "PosterSpidermanNoWayHome",
            voteAverage: 8.3
        )
    )
    .frame(width: 160)
    .padding()
    .background(Theme.background)
}
