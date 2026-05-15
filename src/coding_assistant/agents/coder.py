import re
from pathlib import Path

from coding_assistant.agents.base import Agent
from coding_assistant.domain import CodeArtifact, RetrievedDocument

CODE_BLOCK_RE = re.compile(r"```(?:python)?\n(?P<code>.*?)```", re.DOTALL)


class CodingAgent(Agent):
    def implement(
        self, requirement: str, design: str, context: list[RetrievedDocument]
    ) -> list[CodeArtifact]:
        context_text = "\n\n".join(f"File: {doc.path}\n{doc.content}" for doc in context)
        raw = self.ask(
            "You are a Coding Agent. Write production-quality code for the requirement.\n"
            "Return one Python code block only. Prefer simple, testable application logic.\n\n"
            f"Requirement:\n{requirement}\n\nDesign:\n{design}\n\nContext:\n{context_text}",
            temperature=0.1,
        )
        match = CODE_BLOCK_RE.search(raw)
        content = match.group("code").strip() + "\n" if match else raw + "\n"
        return [
            CodeArtifact(
                path=Path("generated/feature.py"),
                content=content,
                purpose="Generated application code",
            )
        ]

