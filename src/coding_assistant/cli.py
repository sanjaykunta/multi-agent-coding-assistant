import typer
from rich.console import Console
from rich.panel import Panel

from coding_assistant.config import get_settings
from coding_assistant.graph import CodingAssistantGraph
from coding_assistant.llm.factory import build_llm_provider

app = typer.Typer(help="Run the multi-agent coding assistant from your terminal.")
console = Console()


@app.callback()
def main() -> None:
    """Multi-agent coding assistant command line tools."""


@app.command()
def run(requirement: str) -> None:
    """Generate a design, code artifact, tests, and review for a requirement."""

    settings = get_settings()
    graph = CodingAssistantGraph(
        settings=settings,
        llm=build_llm_provider(settings),
        progress_callback=lambda message: console.print(f"[dim]{message}...[/dim]"),
    )
    result = graph.run(requirement)

    console.print(Panel(result.design, title="Architect Agent"))
    for artifact in result.artifacts:
        console.print(Panel(artifact.content, title=f"Coding Agent: {artifact.path}"))
    console.print(Panel(result.tests, title="Testing Agent"))
    console.print(Panel(result.review, title="Review Agent"))
    console.print(f"[bold]Status:[/bold] {result.status}")


if __name__ == "__main__":
    app()
