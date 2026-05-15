from dataclasses import dataclass

from coding_assistant.llm.provider import LlmProvider


@dataclass
class Agent:
    name: str
    llm: LlmProvider

    def ask(self, prompt: str, *, temperature: float = 0.2) -> str:
        return self.llm.generate(prompt, temperature=temperature).text.strip()

