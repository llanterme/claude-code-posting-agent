"""CLI entrypoint for Multi-Agent LLM System."""

import os
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from dotenv import load_dotenv

# Add project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flow.graph import execute_workflow, get_workflow_status
from utils.logging import setup_logfire

# Load environment variables
load_dotenv()

# Initialize CLI app and console
app = typer.Typer(
    name="social-agents",
    help="Multi-Agent LLM System for automated content generation",
    add_completion=False
)
console = Console()


def check_openai_api_key() -> bool:
    """Check if OpenAI API key is configured.
    
    Returns:
        True if API key is available, False otherwise
    """
    return bool(os.getenv("OPENAI_API_KEY"))


def display_results(results: dict) -> None:
    """Display workflow results in a formatted way.
    
    Args:
        results: Dictionary with workflow execution results
    """
    if results["success"]:
        # Success case - display generated content
        console.print(Panel(
            Text(results["generated_content"], style="green"),
            title=f"Generated Content ({results['platform']} - {results['tone']})",
            border_style="green"
        ))
        
        # Display research bullet points
        research_table = Table(title="Research Findings")
        research_table.add_column("Bullet Points", style="cyan")
        
        for bullet in results["research_bullet_points"]:
            research_table.add_row(bullet)
        
        console.print(research_table)
        
        # Display metadata
        console.print(f"\n[bold]Execution Summary:[/bold]")
        console.print(f"• Word Count: {results['word_count']}")
        console.print(f"• Execution Time: {results['execution_time_seconds']:.2f}s")
        console.print(f"• Topic: {results['topic']}")
        
    else:
        # Error case - display error information
        console.print(Panel(
            Text(results["error"], style="red"),
            title="Execution Failed",
            border_style="red"
        ))
        console.print(f"\n[bold]Failed after:[/bold] {results['execution_time_seconds']:.2f}s")


@app.command()
def generate(
    topic: str = typer.Argument(..., help="Topic to research and generate content for"),
    platform: str = typer.Option(
        "general", 
        "--platform", 
        "-p",
        help="Target platform (twitter, linkedin, blog, general)"
    ),
    tone: str = typer.Option(
        "informative", 
        "--tone", 
        "-t",
        help="Content tone (professional, casual, informative, engaging)"
    ),
    verbose: bool = typer.Option(
        False, 
        "--verbose", 
        "-v",
        help="Enable verbose logging output"
    )
) -> None:
    """Generate content using the multi-agent workflow.
    
    This command orchestrates the ResearchAgent and ContentAgent to:
    1. Research the specified topic and generate 5-7 factual bullet points
    2. Transform the research into platform-optimized content with the specified tone
    
    Examples:
        social-agents generate "artificial intelligence" --platform twitter --tone casual
        social-agents generate "climate change" --platform linkedin --tone professional
        social-agents generate "python programming" --platform blog --tone informative
    """
    # Check for required API key
    if not check_openai_api_key():
        console.print(Panel(
            "[red]Error: OPENAI_API_KEY environment variable is required.[/red]\n"
            "Please set your OpenAI API key:\n"
            "export OPENAI_API_KEY='your-api-key-here'",
            title="Configuration Error",
            border_style="red"
        ))
        raise typer.Exit(1)
    
    # Initialize logging
    try:
        setup_logfire()
    except Exception as e:
        if verbose:
            console.print(f"[yellow]Warning: Logfire setup failed: {e}[/yellow]")
    
    # Validate inputs
    supported_platforms = ["twitter", "linkedin", "blog", "general"]
    supported_tones = ["professional", "casual", "informative", "engaging"]
    
    if platform.lower() not in supported_platforms:
        console.print(f"[red]Error: Platform '{platform}' not supported.[/red]")
        console.print(f"Supported platforms: {', '.join(supported_platforms)}")
        raise typer.Exit(1)
    
    if tone.lower() not in supported_tones:
        console.print(f"[red]Error: Tone '{tone}' not supported.[/red]")
        console.print(f"Supported tones: {', '.join(supported_tones)}")
        raise typer.Exit(1)
    
    # Display execution start
    console.print(f"\n[bold]Starting multi-agent workflow...[/bold]")
    console.print(f"• Topic: {topic}")
    console.print(f"• Platform: {platform}")
    console.print(f"• Tone: {tone}")
    console.print("\n[dim]Executing ResearchAgent → ContentAgent pipeline...[/dim]\n")
    
    # Execute workflow
    try:
        with console.status("[bold green]Executing workflow..."):
            results = execute_workflow(topic, platform.lower(), tone.lower())
        
        # Display results
        display_results(results)
        
        # Exit with appropriate code
        if not results["success"]:
            raise typer.Exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Workflow interrupted by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Display system status and configuration information."""
    status_info = get_workflow_status()
    
    # Create status table
    status_table = Table(title="System Status")
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status", style="green")
    
    # Check API key
    api_key_status = "✓ Configured" if check_openai_api_key() else "✗ Missing"
    api_key_style = "green" if check_openai_api_key() else "red"
    
    status_table.add_row("OpenAI API Key", Text(api_key_status, style=api_key_style))
    status_table.add_row("Workflow Version", status_info["workflow_version"])
    status_table.add_row("Agents", ", ".join(status_info["agents"]))
    
    console.print(status_table)
    
    # Display supported options
    console.print(f"\n[bold]Supported Platforms:[/bold] {', '.join(status_info['supported_platforms'])}")
    console.print(f"[bold]Supported Tones:[/bold] {', '.join(status_info['supported_tones'])}")
    console.print(f"[bold]Execution Flow:[/bold] {' → '.join(status_info['execution_flow'])}")


@app.command()
def version() -> None:
    """Display version information."""
    console.print("[bold]Multi-Agent LLM System[/bold]")
    console.print("Version: 1.0.0")
    console.print("Author: Claude Code")
    console.print("\nCore Technologies:")
    
    dependencies = get_workflow_status()["dependencies"]
    for lib, version in dependencies.items():
        console.print(f"• {lib}: {version}")


if __name__ == "__main__":
    app()