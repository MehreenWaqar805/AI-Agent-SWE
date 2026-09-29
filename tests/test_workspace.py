import pytest

from ai_swe_agent.config import Settings
from ai_swe_agent.tools.workspace import WorkspaceTools


def test_read_write_search_and_escape(tmp_path) -> None:
    settings = Settings(workspace_root=tmp_path, memory_dir=tmp_path / "memory")
    tools = WorkspaceTools(settings)
    tools.write_file("src/app.py", "def hello():\n    return 1\n")
    assert "return 1" in tools.read_file("src/app.py")
    hits = tools.search_code(r"def hello")
    assert hits and "src/app.py" in hits[0]
    tools.modify_code("src/app.py", "return 1", "return 2")
    assert "return 2" in tools.read_file("src/app.py")
    with pytest.raises(ValueError):
        tools.resolve("../outside.txt")
