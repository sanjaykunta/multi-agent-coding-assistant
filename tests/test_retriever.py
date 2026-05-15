from pathlib import Path

from coding_assistant.rag.local_retriever import LocalCodeRetriever


def test_retriever_returns_relevant_files(tmp_path: Path) -> None:
    (tmp_path / "tasks.py").write_text("class TaskService:\n    def create_task(self): pass\n")
    (tmp_path / "billing.py").write_text("class InvoiceService:\n    def charge_card(self): pass\n")

    docs = LocalCodeRetriever(tmp_path).retrieve("create task endpoint")

    assert docs
    assert docs[0].path.name == "tasks.py"

