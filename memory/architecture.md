# Architecture

This agent implements **iOS apps only** (Swift / SwiftUI, iOS 17+).

Use **MVVM-C**:
- View: SwiftUI screens, no networking
- ViewModel: `@Observable` or `ObservableObject`, screen state
- Coordinator / Router: navigation
- Model: `Codable` domain types
- Service: networking and persistence

UIKit only when a ticket or existing module already uses it.
