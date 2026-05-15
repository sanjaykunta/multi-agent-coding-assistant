from coding_assistant.config import Settings
from coding_assistant.llm.provider import LlmProvider, LocalDeterministicLlmProvider
from coding_assistant.llm.vertex import VertexGeminiProvider


def build_llm_provider(settings: Settings) -> LlmProvider:
    if settings.llm_provider == "vertex":
        return VertexGeminiProvider(settings)
    return LocalDeterministicLlmProvider()
