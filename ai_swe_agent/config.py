from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    atlassian_mcp_url: str = "https://mcp.atlassian.com/v2/mcp"

    figma_access_token: str = ""
    figma_mcp_url: str = "https://mcp.figma.com/mcp"

    github_token: str = ""
    github_default_remote: str = "origin"
    github_default_base: str = "main"
    github_mcp_url: str = "https://api.githubcopilot.com/mcp/"

    cursor_api_key: str = ""
    cursor_model: str = "composer-2.5"

    workspace_root: Path = Field(default_factory=lambda: Path.cwd())
    ios_app_path: Path = Field(default_factory=lambda: Path("ios"))
    ios_scheme: str = "MoviesApp"
    ios_destination: str = "platform=iOS Simulator,name=iPhone 16,OS=18.0"
    memory_dir: Path = Field(default_factory=lambda: Path("memory"))

    def resolved_workspace(self) -> Path:
        return self.workspace_root.expanduser().resolve()

    def resolved_ios_app(self) -> Path:
        path = self.ios_app_path
        if not path.is_absolute():
            path = self.resolved_workspace() / path
        return path

    def resolved_memory_dir(self) -> Path:
        path = self.memory_dir
        if not path.is_absolute():
            path = self.resolved_workspace() / path
        return path

    def jira_configured(self) -> bool:
        return bool(self.jira_base_url and self.jira_email and self.jira_api_token)

    def figma_configured(self) -> bool:
        return bool(self.figma_access_token)

    def github_configured(self) -> bool:
        return bool(self.github_token)

    def cursor_configured(self) -> bool:
        return bool(self.cursor_api_key)


def load_settings(**overrides: object) -> Settings:
    return Settings(**overrides)
