from __future__ import annotations

import sys

from ai_swe_agent.config import Settings
from ai_swe_agent.models import PipelineResult
from ai_swe_agent.tools.workspace import WorkspaceTools


class BuildPipeline:
    """iOS compile → unit tests → quality. Falls back to Python only for the agent repo."""

    def __init__(self, workspace: WorkspaceTools, settings: Settings | None = None) -> None:
        self.workspace = workspace
        self.settings = settings

    def run(self, *, skip_tests: bool = False) -> PipelineResult:
        commands: list[str] = []
        logs: list[str] = []
        compile_ok = True
        tests_ok = True
        quality_ok = True

        if self._xcode_project():
            compile_ok, tests_ok, quality_ok = self._run_ios(commands, logs, skip_tests=skip_tests)
        elif (self.workspace.root / "Package.swift").exists():
            compile_ok, tests_ok, quality_ok = self._run_swift_package(commands, logs, skip_tests=skip_tests)
        elif (self.workspace.root / "pyproject.toml").exists() or any(self.workspace.root.glob("*.py")):
            compile_ok, tests_ok, quality_ok = self._run_python(commands, logs, skip_tests=skip_tests)
        else:
            logs.append("No iOS toolchain found; skipped build.")

        return PipelineResult(
            compile_ok=compile_ok,
            tests_ok=tests_ok,
            quality_ok=quality_ok,
            commands=commands,
            logs="\n".join(logs),
        )

    def _xcode_project(self) -> str | None:
        projects = list(self.workspace.root.glob("*.xcodeproj"))
        if not projects:
            projects = list(self.workspace.root.rglob("*.xcodeproj"))
        return str(projects[0]) if projects else None

    def _run_ios(
        self, commands: list[str], logs: list[str], *, skip_tests: bool
    ) -> tuple[bool, bool, bool]:
        project = self._xcode_project()
        if not project:
            return True, True, True
        scheme = self.settings.ios_scheme if self.settings else "MoviesApp"
        destination = (
            self.settings.ios_destination
            if self.settings
            else "platform=iOS Simulator,name=iPhone 16"
        )
        build = [
            "xcodebuild",
            "-project",
            project,
            "-scheme",
            scheme,
            "-destination",
            destination,
            "-quiet",
            "build",
        ]
        compile_ok = self._ok(build, commands, logs)
        tests_ok = True
        if not skip_tests:
            test = build[:-1] + ["test"]
            tests_ok = self._ok(test, commands, logs)
        return compile_ok, tests_ok, compile_ok

    def _run_swift_package(
        self, commands: list[str], logs: list[str], *, skip_tests: bool
    ) -> tuple[bool, bool, bool]:
        compile_ok = self._ok(["swift", "build"], commands, logs)
        tests_ok = True
        if not skip_tests:
            tests_ok = self._ok(["swift", "test"], commands, logs)
        return compile_ok, tests_ok, compile_ok

    def _run_python(
        self, commands: list[str], logs: list[str], *, skip_tests: bool
    ) -> tuple[bool, bool, bool]:
        python = sys.executable
        compile_ok = True
        if (self.workspace.root / "ai_swe_agent").exists():
            compile_ok = self._ok([python, "-m", "compileall", "ai_swe_agent"], commands, logs)
        tests_ok = True
        if not skip_tests and (self.workspace.root / "tests").exists():
            tests_ok = self._ok([python, "-m", "pytest", "-q"], commands, logs)
        return compile_ok, tests_ok, True

    def _ok(self, args: list[str], commands: list[str], logs: list[str]) -> bool:
        commands.append(" ".join(args))
        result = self.workspace.run_command(args, timeout=300)
        output = (result.stdout or "") + (result.stderr or "")
        logs.append(f"$ {' '.join(args)}\n{output}")
        return result.returncode == 0
