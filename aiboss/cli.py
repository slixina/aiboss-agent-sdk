import typer
import platform
import socket
from typing import Optional
from .client import AibossClient
from .config import get_agent_id, get_api_url, save_config
from .runner import AgentRunner
from rich.console import Console
from rich.table import Table
from typing import Optional, List

app = typer.Typer()
console = Console()

@app.command()
def enroll(
    code: str = typer.Argument(..., help="Enrollment code from the web dashboard"),
    url: str = typer.Option("http://localhost:3000", help="API URL of the AI Boss server"),
    name: Optional[str] = typer.Option(None, help="Name for this agent (defaults to hostname)"),
    capabilities: Optional[List[str]] = typer.Option(None, help="List of capabilities (default: *)")
):
    """Enroll a new agent. By default, it registers with '*' capability to receive all tasks."""
    if not name:
        name = socket.gethostname()
        
    console.print(f"Enrolling agent '{name}' to {url}...")
    
    # Save base config first so client can use it
    save_config(url, "", "")
    
    client = AibossClient(base_url=url)
    try:
        # If no capabilities provided, default to wildcard *
        if not capabilities:
            capabilities = ["*"]
        
        result = client.enroll(code, name, capabilities)
        
        agent_id = result.get("agent_id")
        if agent_id:
            console.print(f"[green]Successfully enrolled! Agent ID: {agent_id}[/green]")
            console.print(f"API Key: {result.get('api_key')[:8]}...")
        else:
            console.print("[red]Enrollment failed: No Agent ID returned.[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def start():
    """Start the agent to process tasks."""
    agent_id = get_agent_id()
    if not agent_id:
        console.print("[red]Agent not configured. Run 'aiboss enroll' first.[/red]")
        raise typer.Exit(code=1)

    console.print(f"Starting agent {agent_id}...")
    runner = AgentRunner()
    runner.run()

@app.command()
def status():
    """Check agent status and earnings."""
    agent_id = get_agent_id()
    api_url = get_api_url()
    
    if not agent_id:
        console.print("[yellow]Agent not configured.[/yellow]")
        return

    table = Table(title="Agent Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Agent ID", agent_id)
    table.add_row("API URL", api_url)
    
    client = AibossClient()
    
    # Check connectivity via Sync
    try:
        sync_res = client.sync(status="idle")
        if sync_res:
             table.add_row("Connection", "[green]Online[/green]")
        else:
             table.add_row("Connection", "[red]Offline[/red]")
    except Exception as e:
        table.add_row("Connection", f"[red]Error: {e}[/red]")

    # Check earnings
    paycheck = client.get_paycheck()
    if paycheck:
        table.add_row("Name", paycheck.get("agent_name", "N/A"))
        table.add_row("Total Earnings", str(paycheck.get("total_earnings", 0)))
        table.add_row("Rank", str(paycheck.get("rank", "N/A")))
    
    console.print(table)

@app.command()
def check():
    """Diagnose network connection to AI Boss API."""
    import time
    from urllib.parse import urlparse
    import requests
    
    api_url = get_api_url()
    console.print(f"[bold]Diagnosing connection to:[/bold] {api_url}")
    
    # 1. Parse URL
    parsed = urlparse(api_url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    
    if not host:
        console.print("[red]Invalid URL format.[/red]")
        return

    # 2. DNS Resolution
    console.print(f"\n[bold]DNS Resolution for {host}:{port}[/bold]")
    try:
        # Try to resolve both IPv4 and IPv6
        addr_info = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        seen_ips = set()
        for family, type, proto, canonname, sockaddr in addr_info:
            ip = sockaddr[0]
            if ip in seen_ips: continue
            seen_ips.add(ip)
            family_str = "IPv6" if family == socket.AF_INET6 else "IPv4"
            console.print(f"  - {family_str}: {ip}")
    except Exception as e:
        console.print(f"[red]DNS Resolution Failed: {e}[/red]")
        # Don't return, try HTTP anyway as it might use a proxy or different path

    # 3. HTTP Request
    console.print("\n[bold]HTTP Request Check[/bold]")
    try:
        # Use a session to simulate actual client
        s = requests.Session()
        console.print(f"  GET {api_url} ... ", end="")
        start_time = time.time()
        resp = s.get(api_url, timeout=10)
        elapsed = (time.time() - start_time) * 1000
        
        status_style = "green" if resp.status_code < 400 else "yellow"
        console.print(f"[{status_style}]{resp.status_code} {resp.reason}[/{status_style}] ({elapsed:.1f}ms)")
        console.print(f"  Server: {resp.headers.get('Server', 'Unknown')}")
        
    except Exception as e:
        console.print(f"[red]FAILED: {e}[/red]")
        
    console.print("\n[bold]Diagnosis Complete.[/bold]")

if __name__ == "__main__":
    app()
