import hashlib
import math
import re
from abc import ABC, abstractmethod

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CAMEL_RE = re.compile(r"(?<!^)(?=[A-Z])")


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Convert text into a numeric vector for similarity search."""


class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministic local embedding provider.

    This avoids external services for tests and demos while preserving the same
    retrieval shape used by real embedding models.
    """

    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in self._tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], byteorder="big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        return self._normalize(vector)

    def _tokens(self, text: str) -> list[str]:
        normalized: list[str] = []
        for raw_token in TOKEN_RE.findall(text):
            for piece in raw_token.replace("_", " ").split():
                normalized.extend(part.lower() for part in CAMEL_RE.split(piece) if part)
        return [self._stem(token) for token in normalized]

    @staticmethod
    def _stem(token: str) -> str:
        if len(token) > 3 and token.endswith("s"):
            return token[:-1]
        return token

    @staticmethod
    def _normalize(vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(
        left_value * right_value
        for left_value, right_value in zip(left, right, strict=True)
    )
