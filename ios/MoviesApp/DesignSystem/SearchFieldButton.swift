import SwiftUI

struct SearchFieldButton: View {
    let placeholder: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: "magnifyingglass")
                    .font(.body)
                    .foregroundStyle(Theme.iconMuted)
                Text(placeholder)
                    .font(Theme.poppins(size: 14))
                    .foregroundStyle(Theme.textSecondary)
                Spacer(minLength: 0)
            }
            .padding(.horizontal, Theme.spacing)
            .padding(.vertical, 12)
            .background(Theme.card)
            .clipShape(RoundedRectangle(cornerRadius: Theme.cornerRadius, style: .continuous))
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Search")
        .accessibilityHint("Opens the search screen")
    }
}

#Preview {
    SearchFieldButton(placeholder: "Search") {}
        .padding()
        .background(Theme.background)
}
