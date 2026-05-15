from collections.abc import Callable
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from coding_assistant.agents.architect import ArchitectAgent
from coding_assistant.agents.coder import CodingAgent
from coding_assistant.agents.reviewer import ReviewAgent
from coding_assistant.agents.tester import TestingAgent
from coding_assistant.config import Settings
from coding_assistant.domain import AssistantResult, CodeArtifact, RetrievedDocument
from coding_assistant.llm.provider import LlmProvider
from coding_assistant.mcp.repository_client import RepositoryMcpClient
from coding_assistant.rag.local_retriever import LocalCodeRetriever


class AssistantState(TypedDict, total=False):
    requirement: str
    context: list[RetrievedDocument]
    design: str
    artifacts: list[CodeArtifact]
    tests: str
    review: str
    iteration: int
    quality_passed: bool
    saved_files: list[str]
    result: AssistantResult


class CodingAssistantGraph:
    def __init__(
        self,
        settings: Settings,
        llm: LlmProvider,
        *,
        persist_artifacts: bool = True,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        self.settings = settings
        self.persist_artifacts = persist_artifacts
        self.progress_callback = progress_callback
        self.retriever = LocalCodeRetriever(settings.workspace_root)
        self.repository_client = RepositoryMcpClient(settings.workspace_root)
        self.architect = ArchitectAgent(name="architect", llm=llm)
        self.coder = CodingAgent(name="coder", llm=llm)
        self.tester = TestingAgent(name="tester", llm=llm)
        self.reviewer = ReviewAgent(name="reviewer", llm=llm)
        self.graph = self._build_graph()

    def run(self, requirement: str) -> AssistantResult:
        final_state = self.graph.invoke({"requirement": requirement, "iteration": 0})
        return final_state["result"]

    def _build_graph(self):
        builder = StateGraph(AssistantState)
        builder.add_node("retrieve_context", self._retrieve_context)
        builder.add_node("design_solution", self._design_solution)
        builder.add_node("write_code", self._write_code)
        builder.add_node("write_tests", self._write_tests)
        builder.add_node("review_code", self._review_code)
        builder.add_node("aggregate", self._aggregate)

        builder.add_edge(START, "retrieve_context")
        builder.add_edge("retrieve_context", "design_solution")
        builder.add_edge("design_solution", "write_code")
        builder.add_edge("write_code", "write_tests")
        builder.add_conditional_edges(
            "write_tests",
            self._route_after_tests,
            {"retry": "write_code", "review": "review_code"},
        )
        builder.add_edge("review_code", "aggregate")
        builder.add_edge("aggregate", END)
        return builder.compile()

    def _retrieve_context(self, state: AssistantState) -> AssistantState:
        self._progress("Retrieving local code context")
        return {"context": self.retriever.retrieve(state["requirement"])}

    def _design_solution(self, state: AssistantState) -> AssistantState:
        self._progress("Architect Agent is designing the solution")
        return {"design": self.architect.design(state["requirement"], state.get("context", []))}

    def _write_code(self, state: AssistantState) -> AssistantState:
        self._progress("Coding Agent is generating implementation code")
        next_iteration = state.get("iteration", 0) + 1
        artifacts = self.coder.implement(
            state["requirement"], state["design"], state.get("context", [])
        )
        return {"artifacts": artifacts, "iteration": next_iteration}

    def _write_tests(self, state: AssistantState) -> AssistantState:
        self._progress("Testing Agent is generating tests and running quality gate")
        artifacts = state.get("artifacts", [])
        test_artifacts = self.tester.generate_tests(state["requirement"], artifacts)
        all_artifacts = [*artifacts, *test_artifacts]
        return {
            "artifacts": all_artifacts,
            "tests": self.tester.test_plan(state["requirement"], artifacts),
            "quality_passed": self.tester.passes_quality_gate(all_artifacts),
        }

    def _route_after_tests(self, state: AssistantState) -> str:
        if state.get("quality_passed"):
            return "review"
        if state.get("iteration", 0) < self.settings.max_agent_iterations:
            return "retry"
        return "review"

    def _review_code(self, state: AssistantState) -> AssistantState:
        self._progress("Review Agent is reviewing production readiness")
        return {
            "review": self.reviewer.review(
                state["requirement"],
                state["design"],
                state.get("artifacts", []),
                state.get("tests", ""),
            )
        }

    def _aggregate(self, state: AssistantState) -> AssistantState:
        self._progress("Saving generated artifacts")
        status = "completed" if state.get("quality_passed") else "completed_with_warnings"
        artifacts = state.get("artifacts", [])
        saved_files = self._persist_artifacts(artifacts) if self.persist_artifacts else []
        return {
            "result": AssistantResult(
                requirement=state["requirement"],
                design=state["design"],
                context=state.get("context", []),
                artifacts=artifacts,
                tests=state.get("tests", ""),
                review=state.get("review", ""),
                status=status,
            ),
            "saved_files": saved_files,
        }

    def _persist_artifacts(self, artifacts: list[CodeArtifact]) -> list[str]:
        return [
            self.repository_client.write_file(str(artifact.path), artifact.content)
            for artifact in artifacts
        ]

    def _progress(self, message: str) -> None:
        if self.progress_callback:
            self.progress_callback(message)
