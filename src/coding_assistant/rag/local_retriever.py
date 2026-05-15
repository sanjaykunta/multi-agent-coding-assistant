from pathlib import Path

from coding_assistant.domain import RetrievedDocument
from coding_assistant.rag.embeddings import (
    EmbeddingProvider,
    HashEmbeddingProvider,
    cosine_similarity,
)

DEFAULT_EXTENSIONS = {".py", ".java", ".js", ".ts", ".md", ".yaml", ".yml", ".toml"}


class LocalCodeRetriever:
    """Small local RAG retriever for source files and docs.

    It uses local deterministic embeddings so the project runs without external
    infrastructure. The provider can later be replaced by Vertex embeddings and
    the in-memory search can be replaced by Vertex AI Vector Search or pgvector.
    """

    def __init__(
        self,
        root: Path,
        extensions: set[str] | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.root = root
        self.extensions = extensions or DEFAULT_EXTENSIONS
        self.embedding_provider = embedding_provider or HashEmbeddingProvider()

    def retrieve(self, query: str, *, limit: int = 5) -> list[RetrievedDocument]:
        if not self.root.exists():
            return []

        query_vector = self.embedding_provider.embed(query)
        scored: list[RetrievedDocument] = []
        for path, chunk in self._iter_chunks():
            score = cosine_similarity(query_vector, self.embedding_provider.embed(chunk))
            if score > 0.05:
                scored.append(RetrievedDocument(path=path, content=chunk, score=score))
        return sorted(scored, key=lambda doc: doc.score, reverse=True)[:limit]

    def _iter_chunks(self) -> list[tuple[Path, str]]:
        chunks: list[tuple[Path, str]] = []
        for path in self.root.rglob("*"):
            if not path.is_file() or path.suffix not in self.extensions or ".venv" in path.parts:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            chunks.extend((path, chunk) for chunk in self._chunk(content))
        return chunks

    @staticmethod
    def _chunk(text: str, *, max_chars: int = 4000) -> list[str]:
        paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip()
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = paragraph[:max_chars]
        if current:
            chunks.append(current)
        return chunks
