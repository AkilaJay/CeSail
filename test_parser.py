import asyncio
from dom_parser.src.page_analyzer import PageAnalyzer
from dom_parser.src.types import PageAnalysis
import json
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

def print_metadata(meta: Dict[str, Any]):
    console.print("\n[bold blue]Page Metadata[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Property")
    table.add_column("Value")
    
    table.add_row("URL", meta.get('url', 'N/A'))
    table.add_row("Title", meta.get('title', 'N/A'))
    table.add_row("Canonical URL", meta.get('canonical', 'N/A'))
    table.add_row("Status", meta.get('status', 'N/A'))
    
    if 'meta' in meta:
        meta_info = meta['meta']
        table.add_row("Description", meta_info.get('description', 'N/A'))
        table.add_row("Keywords", meta_info.get('keywords', 'N/A'))
        table.add_row("Viewport", meta_info.get('viewport', 'N/A'))
        
        if 'og' in meta_info:
            og = meta_info['og']
            table.add_row("OG Title", og.get('title', 'N/A'))
            table.add_row("OG Description", og.get('description', 'N/A'))
            table.add_row("OG Image", og.get('image', 'N/A'))
    
    console.print(table)

def print_document_outline(outline: list):
    if not outline:
        return
        
    console.print("\n[bold blue]Document Outline[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Level")
    table.add_column("Text")
    table.add_column("ID")
    
    for item in outline:
        table.add_row(
            str(item.get('level', '')),
            item.get('text', ''),
            item.get('id', 'N/A')
        )
    
    console.print(table)

def print_forms(forms: list):
    if not forms:
        return
        
    console.print("\n[bold blue]Forms[/bold blue]")
    for form in forms:
        console.print(Panel(f"[bold]Form ID:[/bold] {form.get('id', 'N/A')}"))
        console.print(f"Action: {form.get('action', 'N/A')}")
        console.print(f"Method: {form.get('method', 'N/A')}")
        
        if form.get('fields'):
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Type")
            table.add_column("Name")
            table.add_column("ID")
            table.add_column("Required")
            table.add_column("Value")
            
            for field in form['fields']:
                table.add_row(
                    field.get('type', ''),
                    field.get('name', 'N/A'),
                    field.get('id', 'N/A'),
                    str(field.get('required', False)),
                    field.get('value', 'N/A')
                )
            
            console.print(table)

def print_media(media: list):
    if not media:
        return
        
    console.print("\n[bold blue]Media Elements[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Type")
    table.add_column("Source")
    table.add_column("Alt Text")
    table.add_column("Dimensions")
    
    for item in media:
        dimensions = f"{item.get('width', 'N/A')}x{item.get('height', 'N/A')}"
        table.add_row(
            item.get('type', ''),
            item.get('src', 'N/A'),
            item.get('alt', 'N/A'),
            dimensions
        )
    
    console.print(table)

def print_links(links: list):
    if not links:
        return
        
    console.print("\n[bold blue]Links[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Text")
    table.add_column("URL")
    table.add_column("Target")
    
    for link in links:
        table.add_row(
            link.get('text', ''),
            link.get('href', 'N/A'),
            link.get('target', 'N/A')
        )
    
    console.print(table)

def print_dynamic_state(dynamic: Dict[str, Any]):
    if not dynamic:
        return
        
    console.print("\n[bold blue]Dynamic State[/bold blue]")
    
    if dynamic.get('modals'):
        console.print("\n[bold]Modals:[/bold]")
        for modal in dynamic['modals']:
            console.print(f"- {modal.get('text', 'N/A')} (ID: {modal.get('id', 'N/A')})")
    
    if dynamic.get('notifications'):
        console.print("\n[bold]Notifications:[/bold]")
        for notif in dynamic['notifications']:
            console.print(f"- {notif.get('text', 'N/A')} (ID: {notif.get('id', 'N/A')})")
    
    if dynamic.get('loading'):
        console.print("\n[bold]Loading Indicators:[/bold]")
        for loader in dynamic['loading']:
            console.print(f"- {loader.get('type', 'N/A')} (ID: {loader.get('id', 'N/A')})")

def print_actions(actions: list):
    if not actions:
        return
        
    console.print("\n[bold blue]Available Actions[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Type")
    table.add_column("Description")
    table.add_column("Confidence")
    
    for action in actions:
        table.add_row(
            str(getattr(action, 'type', '')),
            getattr(action, 'description', ''),
            str(getattr(action, 'confidence', 0))
        )
    
    console.print(table)

def print_layout(layout: list):
    if not layout:
        return
        
    console.print("\n[bold blue]Layout Structure[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Type")
    table.add_column("ID")
    table.add_column("Position")
    table.add_column("Size")
    table.add_column("Z-Index")
    
    for item in layout:
        rect = item.get('rect', {})
        position = f"({rect.get('x', 0)}, {rect.get('y', 0)})"
        size = f"{rect.get('width', 0)}x{rect.get('height', 0)}"
        
        table.add_row(
            item.get('type', ''),
            item.get('id', 'N/A'),
            position,
            size,
            item.get('zIndex', 'N/A')
        )
    
    console.print(table)

def print_pagination(pagination: Dict[str, Any]):
    if not pagination:
        return
        
    console.print("\n[bold blue]Pagination[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Type")
    table.add_column("URL")
    
    if pagination.get('next'):
        table.add_row("Next", pagination['next'])
    if pagination.get('prev'):
        table.add_row("Previous", pagination['prev'])
    
    if pagination.get('pages'):
        for page in pagination['pages']:
            table.add_row(f"Page {page.get('number', 'N/A')}", page.get('href', 'N/A'))
    
    console.print(table)

def print_structured_data(data: list):
    if not data:
        return
        
    console.print("\n[bold blue]Structured Data[/bold blue]")
    for item in data:
        console.print(Syntax(json.dumps(item, indent=2), "json"))

async def main():
    url = "https://developer.mozilla.org/en-US/docs/Web/HTML/Element"
    
    async with PageAnalyzer() as analyzer:
        console.print(f"\n[bold green]Analyzing page:[/bold green] {url}")
        page_data = await analyzer.analyze_page(url)
        
        # Print all sections
        print_metadata(page_data.get('meta', {}))
        print_document_outline(page_data.get('outline', []))
        print_forms(page_data.get('forms', []))
        print_media(page_data.get('media', []))
        print_links(page_data.get('links', []))
        print_dynamic_state(page_data.get('dynamic', {}))
        print_actions(page_data.get('actions', []))
        print_layout(page_data.get('layout', []))
        print_pagination(page_data.get('pagination', {}))
        print_structured_data(page_data.get('structuredData', []))
        
        # Print summary
        console.print("\n[bold green]Summary[/bold green]")
        summary = Table(show_header=True, header_style="bold magenta")
        summary.add_column("Category")
        summary.add_column("Count")
        
        summary.add_row("Headings", str(len(page_data.get('outline', []))))
        summary.add_row("Forms", str(len(page_data.get('forms', []))))
        summary.add_row("Media Elements", str(len(page_data.get('media', []))))
        summary.add_row("Links", str(len(page_data.get('links', []))))
        summary.add_row("Actions", str(len(page_data.get('actions', []))))
        summary.add_row("Layout Sections", str(len(page_data.get('layout', []))))
        
        console.print(summary)

if __name__ == "__main__":
    asyncio.run(main()) 