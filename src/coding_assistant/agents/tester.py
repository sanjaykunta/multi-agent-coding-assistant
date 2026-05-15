from pathlib import Path

from coding_assistant.agents.base import Agent
from coding_assistant.agents.coder import CODE_BLOCK_RE
from coding_assistant.domain import CodeArtifact


class TestingAgent(Agent):
    def test_plan(self, requirement: str, artifacts: list[CodeArtifact]) -> str:
        artifact_text = "\n\n".join(
            f"File: {artifact.path}\n{artifact.content}" for artifact in artifacts
        )
        return self.ask(
            "You are a Testing Agent. Write tests and a test strategy for this generated code.\n"
            "Call out missing edge cases.\n\n"
            f"Requirement:\n{requirement}\n\nArtifacts:\n{artifact_text}",
            temperature=0.1,
        )

    def passes_quality_gate(self, artifacts: list[CodeArtifact]) -> bool:
        combined = "\n".join(artifact.content for artifact in artifacts)
        return "@app.post" in combined and "TestClient" in combined

    def generate_tests(self, requirement: str, artifacts: list[CodeArtifact]) -> list[CodeArtifact]:
        artifact_text = "\n\n".join(
            f"File: {artifact.path}\n{artifact.content}" for artifact in artifacts
        )
        raw = self.ask(
            "You are a Testing Agent. Write pytest code for this generated FastAPI code.\n"
            "Return one Python code block only.\n\n"
            f"Requirement:\n{requirement}\n\nArtifacts:\n{artifact_text}",
            temperature=0.1,
        )
        match = CODE_BLOCK_RE.search(raw)
        content = match.group("code").strip() + "\n" if match else raw + "\n"
        return [
            CodeArtifact(
                path=Path("generated/test_feature.py"),
                content=content,
                purpose="Generated pytest coverage",
            )
        ]
