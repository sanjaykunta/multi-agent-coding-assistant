from pathlib import Path

from coding_assistant.mcp.repository_client import RepositoryMcpClient


def test_repository_mcp_client_writes_file(tmp_path: Path) -> None:
    client = RepositoryMcpClient(tmp_path)

    written = client.write_file("generated/example.py", "VALUE = 42\n")

    assert written == "generated/example.py"
    assert (tmp_path / "generated" / "example.py").read_text() == "VALUE = 42\n"

