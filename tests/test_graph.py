from pathlib import Path

from coding_assistant.config import Settings
from coding_assistant.graph import CodingAssistantGraph
from coding_assistant.llm.provider import LocalDeterministicLlmProvider


def test_graph_runs_end_to_end(tmp_path: Path) -> None:
    settings = Settings(workspace_root=tmp_path, llm_provider="local")
    graph = CodingAssistantGraph(settings=settings, llm=LocalDeterministicLlmProvider())

    result = graph.run("Create a task management endpoint with validation and tests.")

    assert result.status == "completed"
    assert result.design
    assert len(result.artifacts) == 2
    assert "@app.post" in result.artifacts[0].content
    assert "TestClient" in result.artifacts[1].content
    assert result.tests
    assert result.review
    assert (tmp_path / "generated" / "feature.py").exists()
    assert (tmp_path / "generated" / "test_feature.py").exists()
    assert "@app.post" in (tmp_path / "generated" / "feature.py").read_text()
    assert "TestClient" in (tmp_path / "generated" / "test_feature.py").read_text()
