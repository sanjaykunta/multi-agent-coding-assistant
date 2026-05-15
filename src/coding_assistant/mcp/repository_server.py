from mcp.server.fastmcp import FastMCP

from coding_assistant.config import get_settings
from coding_assistant.tools.repository import RepositoryTool

settings = get_settings()
repository = RepositoryTool(settings.workspace_root)
mcp = FastMCP("coding-assistant-repository")


@mcp.tool()
def list_files() -> list[str]:
    """List files available inside the configured workspace root."""

    return repository.list_files()


@mcp.tool()
def read_file(relative_path: str) -> str:
    """Read a workspace file by relative path."""

    return repository.read_file(relative_path)


@mcp.tool()
def write_file(relative_path: str, content: str) -> str:
    """Write a workspace file by relative path and return the written path."""

    return repository.write_file(relative_path, content)


if __name__ == "__main__":
    mcp.run()

