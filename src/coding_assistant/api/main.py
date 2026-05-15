from fastapi import FastAPI
from pydantic import BaseModel, Field

from coding_assistant.config import get_settings
from coding_assistant.graph import CodingAssistantGraph
from coding_assistant.llm.factory import build_llm_provider


class AssistRequest(BaseModel):
    requirement: str = Field(min_length=10, max_length=5000)


class AssistResponse(BaseModel):
    status: str
    design: str
    artifacts: dict[str, str]
    tests: str
    review: str
    retrieved_context: list[str]


app = FastAPI(
    title="Multi-Agent Coding Assistant",
    version="0.1.0",
    description="LangGraph-based coding assistant with RAG and MCP-ready repository tooling.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/assist", response_model=AssistResponse)
def assist(request: AssistRequest) -> AssistResponse:
    settings = get_settings()
    graph = CodingAssistantGraph(settings=settings, llm=build_llm_provider(settings))
    result = graph.run(request.requirement)
    return AssistResponse(
        status=result.status,
        design=result.design,
        artifacts={str(artifact.path): artifact.content for artifact in result.artifacts},
        tests=result.tests,
        review=result.review,
        retrieved_context=[str(doc.path) for doc in result.context],
    )

