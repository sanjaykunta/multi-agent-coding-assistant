from coding_assistant.agents.base import Agent
from coding_assistant.domain import RetrievedDocument


class ArchitectAgent(Agent):
    def design(self, requirement: str, context: list[RetrievedDocument]) -> str:
        context_text = "\n\n".join(f"File: {doc.path}\n{doc.content}" for doc in context)
        return self.ask(
            "You are an Architect Agent. Create a concise system design for this requirement.\n"
            "Mention endpoints, data models, risks, and tests.\n\n"
            f"Requirement:\n{requirement}\n\n"
            f"Retrieved context:\n{context_text or 'No existing code context found.'}",
        )

