# iOS coding conventions

- Swift 5.9+, SwiftUI first
- Files are `UpperCamelCase.swift`; views end in `View`, view models in `ViewModel`
- No force unwraps in production paths
- Async work uses `async`/`await`, not Combine unless the module already does
- Assets live in `Assets.xcassets`; colors and fonts go through `DesignSystem`
- Do not edit the Python agent, MCP servers, or `.env`
- Implement only under `ios/`
