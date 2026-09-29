import SwiftUI

struct SearchFieldButton: View {
    let placeholder: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Text(placeholder)
                    .font(Theme.bodyFont())
                    .foregroundStyle(Theme.textSecondary)
                Spacer(minLength: 0)
                Image(systemName: "magnifyingglass")
                    .font(.body.weight(.semibold))
                    .foregroundStyle(Theme.primary)
            }
            .padding(.horizontal, Theme.spacing)
            .padding(.vertical, 14)
            .background(Theme.surface)
            .clipShape(RoundedRectangle(cornerRadius: Theme.cornerRadius, style: .continuous))
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Search movies")
        .accessibilityHint("Opens the search screen")
    }
}

#Preview {
    SearchFieldButton(placeholder: "Search movies") {}
        .padding()
        .background(Theme.background)
}
