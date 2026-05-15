from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions

from coding_assistant.config import Settings
from coding_assistant.llm.provider import LlmProvider, LlmResponse


class VertexGeminiProvider(LlmProvider):
    """Google Gen AI SDK provider configured for Vertex AI Gemini."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.gemini_model
        self._client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
            http_options=HttpOptions(
                api_version="v1",
                timeout=settings.llm_timeout_seconds * 1000,
            ),
        )

    def generate(self, prompt: str, *, temperature: float = 0.2) -> LlmResponse:
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=GenerateContentConfig(
                temperature=temperature,
                candidate_count=1,
                max_output_tokens=2048,
            ),
        )
        return LlmResponse(text=response.text or "", model=self._model)
