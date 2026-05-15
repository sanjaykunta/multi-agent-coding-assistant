from pathlib import Path


class RepositoryTool:
    """Safe file access layer for agent tools and the MCP server."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def list_files(self) -> list[str]:
        return sorted(
            str(path.relative_to(self.root))
            for path in self.root.rglob("*")
            if path.is_file() and ".venv" not in path.parts
        )

    def read_file(self, relative_path: str) -> str:
        path = self._resolve_safe(relative_path)
        return path.read_text(encoding="utf-8")

    def write_file(self, relative_path: str, content: str) -> str:
        path = self._resolve_safe(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path.relative_to(self.root))

    def _resolve_safe(self, relative_path: str) -> Path:
        path = (self.root / relative_path).resolve()
        if self.root not in path.parents and path != self.root:
            raise ValueError(f"Path escapes workspace root: {relative_path}")
        return path

