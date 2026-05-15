from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RetrievedDocument:
    path: Path
    content: str
    score: float


@dataclass(frozen=True)
class CodeArtifact:
    path: Path
    content: str
    purpose: str


@dataclass
class AssistantResult:
    requirement: str
    design: str
    context: list[RetrievedDocument] = field(default_factory=list)
    artifacts: list[CodeArtifact] = field(default_factory=list)
    tests: str = ""
    review: str = ""
    status: str = "completed"

