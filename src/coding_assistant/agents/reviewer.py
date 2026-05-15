from coding_assistant.agents.base import Agent
from coding_assistant.domain import CodeArtifact


class ReviewAgent(Agent):
    def review(
        self,
        requirement: str,
        design: str,
        artifacts: list[CodeArtifact],
        tests: str,
    ) -> str:
        artifact_text = "\n\n".join(
            f"File: {artifact.path}\n{artifact.content}" for artifact in artifacts
        )
        return self.ask(
            "You are a senior Review Agent. Review the code for correctness, security, "
            "maintainability, and production readiness.\n\n"
            f"Requirement:\n{requirement}\n\nDesign:\n{design}\n\nArtifacts:\n{artifact_text}\n\nTests:\n{tests}",
            temperature=0.1,
        )
