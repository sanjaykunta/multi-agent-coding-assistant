import os
import sys
from datetime import timedelta
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class RepositoryMcpClient:
    """MCP client for repository file operations."""

    def __init__(self, workspace_root: Path, *, server_cwd: Path | None = None) -> None:
        self.workspace_root = workspace_root.resolve()
        self.server_cwd = server_cwd or Path.cwd()

    def write_file(self, relative_path: str, content: str) -> str:
        return anyio.run(self._write_file, relative_path, content)

    async def _write_file(self, relative_path: str, content: str) -> str:
        env = os.environ.copy()
        env["WORKSPACE_ROOT"] = str(self.workspace_root)

        server = StdioServerParameters(
            command=sys.executable,
            args=["-m", "coding_assistant.mcp.repository_server"],
            env=env,
            cwd=str(self.server_cwd),
        )

        with open(os.devnull, "w") as errlog:
            async with (
                stdio_client(server, errlog=errlog) as (read_stream, write_stream),
                ClientSession(read_stream, write_stream) as session,
            ):
                await session.initialize()
                result = await session.call_tool(
                    "write_file",
                    {"relative_path": relative_path, "content": content},
                    read_timeout_seconds=timedelta(seconds=30),
                )

        if result.isError:
            message = result.content[0].text if result.content else "Unknown MCP tool error"
            raise RuntimeError(message)
        return result.content[0].text if result.content else relative_path
