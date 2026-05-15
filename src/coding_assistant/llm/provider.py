from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LlmResponse:
    text: str
    model: str


class LlmProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, *, temperature: float = 0.2) -> LlmResponse:
        """Generate text from a prompt."""


class LocalDeterministicLlmProvider(LlmProvider):
    """Deterministic provider used for local development and tests."""

    def generate(self, prompt: str, *, temperature: float = 0.2) -> LlmResponse:
        prompt_lower = prompt.lower()
        if "review the code" in prompt_lower:
            text = (
                "Review:\n"
                "- The generated code now exposes POST /tasks and GET /tasks endpoints.\n"
                "- Pydantic validates title length and priority bounds before business logic.\n"
                "- Tests cover success, validation failures, and task listing.\n"
                "- Replace in-memory storage with a database before production deployment.\n"
                "- Add authentication and request tracing if this API is exposed beyond localhost."
            )
        elif "system design" in prompt_lower:
            text = (
                "Design:\n"
                "- Build a FastAPI service with a clear application layer.\n"
                "- Add input validation with Pydantic models.\n"
                "- Keep business logic isolated from transport concerns.\n"
                "- Include unit tests for successful and invalid requests."
            )
        elif "write production-quality code" in prompt_lower:
            text = (
                "```python\n"
                "from typing import Literal\n\n"
                "from fastapi import FastAPI, status\n"
                "from pydantic import BaseModel, Field\n\n\n"
                "class CreateTaskRequest(BaseModel):\n"
                "    title: str = Field(min_length=1, max_length=120)\n"
                "    priority: int = Field(default=3, ge=1, le=5)\n\n"
                "\n"
                "class TaskResponse(BaseModel):\n"
                "    id: int\n"
                "    title: str\n"
                "    priority: int\n"
                "    status: Literal[\"open\"]\n\n\n"
                "app = FastAPI(title=\"Task Management API\")\n"
                "_tasks: list[TaskResponse] = []\n\n\n"
                "@app.post(\n"
                "    \"/tasks\",\n"
                "    response_model=TaskResponse,\n"
                "    status_code=status.HTTP_201_CREATED,\n"
                ")\n"
                "def create_task(payload: CreateTaskRequest) -> TaskResponse:\n"
                "    task = TaskResponse(\n"
                "        id=len(_tasks) + 1,\n"
                "        title=payload.title,\n"
                "        priority=payload.priority,\n"
                "        status=\"open\",\n"
                "    )\n"
                "    _tasks.append(task)\n"
                "    return task\n\n\n"
                "@app.get(\"/tasks\", response_model=list[TaskResponse])\n"
                "def list_tasks() -> list[TaskResponse]:\n"
                "    return _tasks\n"
                "```\n"
            )
        elif "write tests" in prompt_lower:
            text = (
                "Test plan:\n"
                "- POST /tasks returns 201 and a validated task response.\n"
                "- Empty titles are rejected with 422.\n"
                "- Priority values outside 1-5 are rejected with 422.\n"
                "- GET /tasks returns created tasks."
            )
        elif "write pytest code" in prompt_lower:
            text = (
                "```python\n"
                "from fastapi.testclient import TestClient\n\n"
                "from generated.feature import app, _tasks\n\n\n"
                "client = TestClient(app)\n\n\n"
                "def setup_function() -> None:\n"
                "    _tasks.clear()\n\n\n"
                "def test_create_task_success() -> None:\n"
                "    response = client.post(\n"
                "        \"/tasks\",\n"
                "        json={\"title\": \"Write tests\", \"priority\": 2},\n"
                "    )\n\n"
                "    assert response.status_code == 201\n"
                "    assert response.json() == {\n"
                "        \"id\": 1,\n"
                "        \"title\": \"Write tests\",\n"
                "        \"priority\": 2,\n"
                "        \"status\": \"open\",\n"
                "    }\n\n\n"
                "def test_create_task_rejects_empty_title() -> None:\n"
                "    response = client.post(\n"
                "        \"/tasks\",\n"
                "        json={\"title\": \"\", \"priority\": 2},\n"
                "    )\n\n"
                "    assert response.status_code == 422\n\n\n"
                "def test_create_task_rejects_invalid_priority() -> None:\n"
                "    response = client.post(\n"
                "        \"/tasks\",\n"
                "        json={\"title\": \"Bad priority\", \"priority\": 9},\n"
                "    )\n\n"
                "    assert response.status_code == 422\n\n\n"
                "def test_list_tasks_returns_created_tasks() -> None:\n"
                "    client.post(\"/tasks\", json={\"title\": \"First\", \"priority\": 1})\n\n"
                "    response = client.get(\"/tasks\")\n\n"
                "    assert response.status_code == 200\n"
                "    assert response.json()[0][\"title\"] == \"First\"\n"
                "```\n"
            )
        else:
            text = "I need a more specific prompt to produce a useful result."
        return LlmResponse(text=text, model="local-deterministic")


FakeLlmProvider = LocalDeterministicLlmProvider
