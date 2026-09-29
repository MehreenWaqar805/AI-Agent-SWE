from __future__ import annotations

import json
from datetime import datetime, timezone

from ai_swe_agent.config import Settings
from ai_swe_agent.models import MemorySnapshot

SEED_FILES = {
    "architecture.md": """# Architecture

This agent implements **iOS apps only** (Swift / SwiftUI, iOS 17+).

Use **MVVM-C**:
- View: SwiftUI screens, no networking
- ViewModel: `@Observable` or `ObservableObject`, screen state
- Coordinator / Router: navigation
- Model: `Codable` domain types
- Service: networking and persistence

UIKit only when a ticket or existing module already uses it.
""",
    "conventions.md": """# iOS coding conventions

- Swift 5.9+, SwiftUI first
- Files are `UpperCamelCase.swift`; views end in `View`, view models in `ViewModel`
- No force unwraps in production paths
- Async work uses `async`/`await`, not Combine unless the module already does
- Assets live in `Assets.xcassets`; colors and fonts go through `DesignSystem`
- Do not edit the Python agent, MCP servers, or `.env`
- Implement only under `ios/`
""",
    "project-structure.md": """# iOS project structure

```
ios/
  MoviesApp.xcodeproj
  MoviesApp/
    MoviesAppApp.swift
    App/                  # composition root, coordinator
    Features/
      Home/
      Search/
      Wishlist/
      Rating/
    Models/
    Services/
    DesignSystem/
    Resources/
  MoviesAppTests/
```

New Jira screens belong in `Features/<Name>/` as `*View.swift` + `*ViewModel.swift`.
""",
    "api-patterns.md": """# iOS networking

- One `MovieServicing` protocol; real and preview implementations
- `URLSession` + `async throws`
- Decode with `JSONDecoder` onto `Codable` models
- Errors map to user-facing messages on the view model
- No API keys hardcoded in Swift
""",
    "design-system.md": """# iOS design system

Map Figma tokens into `DesignSystem/Theme.swift`:
- Colors, typography, spacing, corner radius
- Reusable SwiftUI controls (poster card, rating stars, search field)

Match Figma layout: safe area, tab bar, navigation title, and dark/light if the file specifies both.
""",
}


class ProjectMemory:
    """File-backed iOS project knowledge base used during plan/verify/reflect."""

    def __init__(self, settings: Settings) -> None:
        self.root = settings.resolved_memory_dir()
        self.decisions_path = self.root / "decisions.jsonl"

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "runtime").mkdir(exist_ok=True)
        for name, body in SEED_FILES.items():
            path = self.root / name
            if not path.exists():
                path.write_text(body, encoding="utf-8")
        if not self.decisions_path.exists():
            self.decisions_path.write_text("", encoding="utf-8")

    def load(self) -> MemorySnapshot:
        self.ensure()
        return MemorySnapshot(
            architecture=self._read("architecture.md"),
            conventions=self._read("conventions.md"),
            project_structure=self._read("project-structure.md"),
            api_patterns=self._read("api-patterns.md"),
            design_system=self._read("design-system.md"),
            recent_decisions=self._recent_decisions(),
        )

    def remember(self, title: str, detail: str, ticket_key: str | None = None) -> None:
        self.ensure()
        record = {
            "at": datetime.now(timezone.utc).isoformat(),
            "title": title,
            "detail": detail,
            "ticket": ticket_key,
        }
        with self.decisions_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")

    def _read(self, name: str) -> str:
        path = self.root / name
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _recent_decisions(self, limit: int = 8) -> list[str]:
        if not self.decisions_path.exists():
            return []
        lines = [line for line in self.decisions_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        out: list[str] = []
        for line in lines[-limit:]:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            ticket = f" ({item['ticket']})" if item.get("ticket") else ""
            out.append(f"{item.get('title', 'decision')}{ticket}: {item.get('detail', '')}")
        return out
