"""Typer CLI for Open Synthesis."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="open-synthesis",
    help="RAG pipeline for synthesizing peer-reviewed scientific literature.",
)
console = Console()


@app.command()
def ingest(
    query: Annotated[str, typer.Argument(help="Search query for data sources")],
    domain: Annotated[str, typer.Option(help="Domain/collection name for vector store")] = "default",
    sources: Annotated[Optional[str], typer.Option(help="Comma-separated source names (default: all)")] = None,
    config: Annotated[Optional[Path], typer.Option(help="Path to TOML config file")] = None,
) -> None:
    """Ingest documents from data sources into the vector store."""
    import asyncio

    from open_synthesis.config import load_settings
    from open_synthesis.corpus.manager import CorpusManager

    settings = load_settings(config)
    manager = CorpusManager(settings)
    source_list = sources.split(",") if sources else None

    console.print(f"[bold]Ingesting:[/bold] {query!r} into domain [cyan]{domain}[/cyan]")
    result = asyncio.run(manager.ingest(query, domain, source_names=source_list))
    console.print(f"[green]Done.[/green] Ingested {result['documents']} documents, {result['chunks']} chunks.")


@app.command()
def synthesize(
    question: Annotated[str, typer.Argument(help="Research question to synthesize")],
    domain: Annotated[str, typer.Option(help="Domain/collection to search")] = "default",
    validate: Annotated[bool, typer.Option(help="Run validation passes")] = True,
    output: Annotated[Optional[Path], typer.Option(help="Save result to JSON file")] = None,
    config: Annotated[Optional[Path], typer.Option(help="Path to TOML config file")] = None,
) -> None:
    """Run the full synthesis pipeline on a research question."""
    import asyncio
    import json

    from open_synthesis.config import load_settings
    from open_synthesis.synthesis.pipeline import SynthesisPipeline

    settings = load_settings(config)
    pipeline = SynthesisPipeline(settings)

    console.print(f"[bold]Synthesizing:[/bold] {question!r} from domain [cyan]{domain}[/cyan]")
    result = asyncio.run(pipeline.run(question, domain, validate=validate))

    console.print(f"\n[bold green]Synthesis complete.[/bold green]")
    if result.confidence:
        console.print(f"Confidence: [yellow]{result.confidence.value}[/yellow]")
    if result.hallucination_flags:
        console.print(f"[red]Hallucination flags:[/red] {result.hallucination_flags}")
    console.print(f"\n{result.synthesis}")

    if output:
        output.write_text(json.dumps(result.model_dump(mode="json"), indent=2))
        console.print(f"\nSaved to {output}")


@app.command()
def validate(
    input_file: Annotated[Path, typer.Argument(help="Path to synthesis result JSON")],
    config: Annotated[Optional[Path], typer.Option(help="Path to TOML config file")] = None,
) -> None:
    """Run validation on a saved synthesis result."""
    import asyncio
    import json

    from open_synthesis.config import load_settings
    from open_synthesis.synthesis.pipeline import SynthesisPipeline
    from open_synthesis.types import SynthesisResult

    settings = load_settings(config)
    pipeline = SynthesisPipeline(settings)
    data = json.loads(input_file.read_text())
    result = SynthesisResult(**data)

    console.print(f"[bold]Validating synthesis:[/bold] {result.question!r}")
    validated = asyncio.run(pipeline.validate_result(result))

    console.print(f"Confidence: [yellow]{validated.confidence.value if validated.confidence else 'unknown'}[/yellow]")
    if validated.hallucination_flags:
        console.print(f"[red]Hallucination flags:[/red] {validated.hallucination_flags}")
    else:
        console.print("[green]No hallucination flags.[/green]")

    output = input_file.with_suffix(".validated.json")
    output.write_text(json.dumps(validated.model_dump(mode="json"), indent=2))
    console.print(f"Saved to {output}")


@app.command()
def paper(
    topic: Annotated[str, typer.Argument(help="Research topic for multi-section paper")],
    domain: Annotated[str, typer.Option(help="Domain/collection name for vector store")] = "default",
    sources_list: Annotated[Optional[str], typer.Option("--sources", help="Comma-separated source names (default: all)")] = None,
    output: Annotated[Optional[Path], typer.Option(help="Save paper as markdown file")] = None,
    config: Annotated[Optional[Path], typer.Option(help="Path to TOML config file")] = None,
) -> None:
    """Generate a multi-section research paper with per-section retrieval and synthesis."""
    import asyncio

    from open_synthesis.config import load_settings
    from open_synthesis.synthesis.paper import PaperPipeline

    settings = load_settings(config)
    pipeline = PaperPipeline(settings)
    source_names = sources_list.split(",") if sources_list else None

    result = asyncio.run(pipeline.run(topic, domain, source_names=source_names))

    markdown = result.to_markdown()

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown)
        console.print(f"\nSaved to [cyan]{output}[/cyan]")
    else:
        console.print(f"\n{markdown}")


@app.command()
def sources() -> None:
    """List available data sources and their auth requirements."""
    from open_synthesis.corpus.sources import SOURCE_REGISTRY

    table = Table(title="Available Data Sources")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Auth Required")
    table.add_column("Description")

    for name, cls in sorted(SOURCE_REGISTRY.items()):
        info = cls.info()
        auth = "[red]Yes[/red]" if info.get("auth_required") else "[green]No[/green]"
        table.add_row(name, info.get("data_type", ""), auth, info.get("description", ""))

    console.print(table)


if __name__ == "__main__":
    app()
