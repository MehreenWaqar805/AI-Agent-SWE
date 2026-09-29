from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ai_swe_agent.config import Settings
from ai_swe_agent.models import CodebaseContext

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    "DerivedData",
    ".build",
}

LANGUAGE_MARKERS = {
    "py": "python",
    "ts": "typescript",
    "tsx": "typescript",
    "js": "javascript",
    "swift": "swift",
    "kt": "kotlin",
    "java": "java",
    "go": "go",
}


class WorkspaceTools:
    """Local workspace actions: read, write, search, modify, run, git."""

    def __init__(self, settings: Settings, root: Path | None = None) -> None:
        self.root = (root or settings.resolved_workspace()).resolve()

    def resolve(self, relative: str | Path) -> Path:
        path = (self.root / relative).resolve() if not Path(relative).is_absolute() else Path(relative).resolve()
        if path != self.root and self.root not in path.parents:
            raise ValueError(f"Path escapes workspace: {relative}")
        return path

    def read_file(self, relative: str) -> str:
        return self.resolve(relative).read_text(encoding="utf-8")

    def write_file(self, relative: str, content: str) -> str:
        path = self.resolve(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path.relative_to(self.root))

    def search_code(self, pattern: str, glob: str = "*") -> list[str]:
        compiled = re.compile(pattern)
        hits: list[str] = []
        for path in self.root.rglob(glob):
            if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for index, line in enumerate(text.splitlines(), start=1):
                if compiled.search(line):
                    rel = path.relative_to(self.root)
                    hits.append(f"{rel}:{index}:{line.strip()}")
                    if len(hits) >= 80:
                        return hits
        return hits

    def modify_code(self, relative: str, old: str, new: str) -> str:
        path = self.resolve(relative)
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise ValueError(f"Pattern not found in {relative}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return str(path.relative_to(self.root))

    def run_command(self, args: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
        if not args:
            raise ValueError("Command is empty")
        return subprocess.run(
            args,
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

    def inspect(self) -> CodebaseContext:
        if not self.root.exists():
            return CodebaseContext(
                workspace_root=str(self.root),
                notes="iOS app path does not exist yet",
            )
        top_level = sorted(
            path.name
            for path in self.root.iterdir()
            if path.name not in SKIP_DIRS and not path.name.startswith(".")
        )
        languages: set[str] = set()
        for path in self.root.rglob("*"):
            if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
                continue
            lang = LANGUAGE_MARKERS.get(path.suffix.lstrip("."))
            if lang:
                languages.add(lang)
        notes = []
        if any(self.root.glob("*.xcodeproj")) or any(self.root.rglob("*.xcodeproj")):
            notes.append("Xcode iOS app (Swift / SwiftUI)")
        if (self.root / "Package.swift").exists():
            notes.append("Swift package")
        if (self.root / "pyproject.toml").exists():
            notes.append("Python project (pyproject.toml)")
        if (self.root / "package.json").exists():
            notes.append("Node project (package.json)")
        return CodebaseContext(
            workspace_root=str(self.root),
            languages=sorted(languages),
            top_level=top_level,
            notes="; ".join(notes),
        )
