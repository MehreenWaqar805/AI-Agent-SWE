from ai_swe_agent.config import Settings
from ai_swe_agent.memory.store import ProjectMemory


def test_memory_round_trip(tmp_path) -> None:
    settings = Settings(workspace_root=tmp_path, memory_dir=tmp_path / "memory")
    store = ProjectMemory(settings)
    store.remember("chose MVVM", "View models own screen state", "SCRUM-1")
    snapshot = store.load()
    assert snapshot.architecture
    assert "MVVM-C" in snapshot.architecture
    assert "iOS" in snapshot.architecture
    assert any("chose MVVM" in item for item in snapshot.recent_decisions)
