from pathlib import Path

import pytest

from coding_assistant.tools.repository import RepositoryTool


def test_repository_tool_prevents_path_escape(tmp_path: Path) -> None:
    tool = RepositoryTool(tmp_path)

    with pytest.raises(ValueError):
        tool.write_file("../escape.py", "bad")


def test_repository_tool_reads_and_lists_files(tmp_path: Path) -> None:
    tool = RepositoryTool(tmp_path)

    written = tool.write_file("src/example.py", "print('hello')\n")

    assert written == "src/example.py"
    assert tool.read_file("src/example.py") == "print('hello')\n"
    assert tool.list_files() == ["src/example.py"]

