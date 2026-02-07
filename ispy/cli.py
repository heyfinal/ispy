"""
iSpy CLI - Command Line Interface
"""

import os
import sys
import json
import argparse
import getpass
import urllib.request
import urllib.error
import plistlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

os.environ.setdefault("HOMEBREW_NO_ENV_HINTS", "1")

from .core import iSpyTool
from .config import Config
from .device import detect_devices
from .backup import BackupManager, BackupCatalog
from .case import CaseBuilder, load_case, build_timeline, search_case, export_case_report


# Optional imports
try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

BANNER = r"""
o8o                                  
 `"'                                  
oooo   .oooo.o oo.ooooo.  oooo    ooo 
`888  d88(  "8  888' `88b  `88.  .8'  
 888  `"Y88b.   888   888   `88..8'   
 888  o.  )88b  888   888    `888'    
o888o 8""888P'  888bod8P'     .8'     
                888       .o..P'      
               o888o      `Y8P'       
""".strip("\n")

UPDATE_CACHE = Path.home() / ".ispy" / "update_check.json"
UPDATE_URL = "https://api.github.com/repos/heyfinal/ispy/releases/latest"
REPO_URL = "https://github.com/heyfinal/ispy"


def _version_tuple(value: str):
    value = value.lstrip("v")
    parts = []
    for chunk in value.split("."):
        try:
            parts.append(int(chunk))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _read_update_cache():
    if not UPDATE_CACHE.exists():
        return None
    try:
        data = json.loads(UPDATE_CACHE.read_text())
        checked_at = datetime.fromisoformat(data.get("checked_at", ""))
        if datetime.now() - checked_at > timedelta(days=1):
            return None
        return data
    except Exception:
        return None


def _write_update_cache(latest: str, update_available: bool):
    try:
        UPDATE_CACHE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "checked_at": datetime.now().isoformat(),
            "latest": latest,
            "update_available": update_available,
        }
        UPDATE_CACHE.write_text(json.dumps(data))
    except Exception:
        pass


def _get_update_notice(current_version: str) -> str:
    cached = _read_update_cache()
    if cached:
        if cached.get("update_available"):
            return f"Update available: {cached.get('latest')}"
        return ""

    try:
        req = urllib.request.Request(
            UPDATE_URL,
            headers={"User-Agent": "ispy-update-check"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        latest = payload.get("tag_name", "").strip()
        if not latest:
            _write_update_cache("", False)
            return ""
        update_available = _version_tuple(latest) > _version_tuple(current_version)
        _write_update_cache(latest, update_available)
        if update_available:
            return f"Update available: {latest}"
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, json.JSONDecodeError):
        return ""
    return ""


def print_output(message: str, style: str = None):
    """Print with or without rich formatting"""
    if RICH_AVAILABLE and console:
        console.print(message, style=style)
    else:
        print(message)


def print_error(message: str):
    """Print error message"""
    if RICH_AVAILABLE and console:
        console.print(f"[red]Error:[/red] {message}")
    else:
        print(f"Error: {message}", file=sys.stderr)


def print_success(message: str):
    """Print success message"""
    if RICH_AVAILABLE and console:
        console.print(f"[green]✓[/green] {message}")
    else:
        print(f"✓ {message}")


def display_banner():
    """Show ASCII banner if provided."""
    if not BANNER.strip():
        return
    try:
        from . import __version__
        version = __version__
    except Exception:
        version = "unknown"

    meta_lines = [
        "Created by Final. AI powered.",
        "Created October 2025.",
        f"Version {version}",
        f"Repo: {REPO_URL}",
    ]
    update_notice = _get_update_notice(version)
    if update_notice:
        meta_lines.append(update_notice)
    meta = "\n".join(meta_lines)
    if RICH_AVAILABLE and console:
        console.print(f"[bright_cyan]{BANNER}[/bright_cyan]")
        console.print(f"[cyan]{meta}[/cyan]")
    else:
        print(BANNER)
        print(meta)


def _run_with_progress(tool: iSpyTool, device, modules_list, include_ai: bool):
    if not RICH_AVAILABLE or not console:
        return tool.run_diagnostic(device, modules=modules_list, include_ai=include_ai)

    total = len(modules_list)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Starting...", total=total)

        def on_module(module_name: str, index: int, total_count: int):
            progress.update(task, description=f"Running {module_name}...", advance=1)

        report = tool.run_diagnostic(
            device,
            modules=modules_list,
            include_ai=include_ai,
            progress_callback=on_module
        )
        progress.update(task, description="Complete")
        return report


def _display_report(report: dict, verbose: bool):
    """Display diagnostic report"""
    summary = report.get('summary', {})

    if RICH_AVAILABLE and console:
        grade = summary.get('overall_grade', 'N/A')
        score = summary.get('overall_score', 0)
        grade_color = _get_grade_color(grade)

        console.print(Panel(
            f"[{grade_color}]{grade}[/{grade_color}] ({score}%)",
            title="Device Health",
            border_style=grade_color
        ))

        if verbose:
            table = Table(title="Module Results")
            table.add_column("Module", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Key Info", style="white")

            for module_name, results in report.get('modules', {}).items():
                if 'error' in results:
                    status = "[red]Error[/red]"
                    info = results['error'][:50]
                else:
                    status = "[green]OK[/green]"
                    info = _get_key_info(module_name, results)
                table.add_row(module_name, status, info)

            console.print(table)

        recs = summary.get('top_recommendations', [])
        if recs:
            console.print("\n[yellow]Recommendations:[/yellow]")
            for rec in recs:
                console.print(f"  • {rec}")

        if 'ai_analysis' in report:
            console.print(Panel(
                report['ai_analysis'],
                title="AI Analysis",
                border_style="blue"
            ))
            _maybe_prompt_api_key_update(report['ai_analysis'])
    else:
        grade = summary.get('overall_grade', 'N/A')
        score = summary.get('overall_score', 0)
        print(f"\nDevice Health: {grade} ({score}%)")

        if verbose:
            print("\nModule Results:")
            print("-" * 40)
            for module_name, results in report.get('modules', {}).items():
                status = "Error" if 'error' in results else "OK"
                print(f"  {module_name}: {status}")

        recs = summary.get('top_recommendations', [])
        if recs:
            print("\nRecommendations:")
            for rec in recs:
                print(f"  • {rec}")
        if 'ai_analysis' in report:
            _maybe_prompt_api_key_update(report['ai_analysis'])


def _get_grade_color(grade: str) -> str:
    """Get color for grade"""
    colors = {
        'A+': 'green', 'A': 'green', 'A-': 'green',
        'B+': 'blue', 'B': 'blue', 'B-': 'blue',
        'C+': 'yellow', 'C': 'yellow', 'C-': 'yellow',
        'D+': 'orange1', 'D': 'orange1', 'D-': 'orange1',
        'F': 'red'
    }
    return colors.get(grade, 'white')


def _get_key_info(module: str, results: dict) -> str:
    """Extract key info from module results"""
    if module == 'battery':
        level = results.get('battery_level', '?')
        return f"Level: {level}%"
    elif module == 'storage':
        usage = results.get('usage_percent', '?')
        return f"Usage: {usage}%"
    elif module == 'network':
        status = results.get('connectivity_status', '?')
        return f"Status: {status}"
    elif module == 'security':
        score = results.get('security_score', '?')
        return f"Score: {score}"
    elif module == 'thermal':
        status = results.get('status', '?')
        return f"Status: {status}"
    return "OK"


def _maybe_prompt_api_key_update(ai_text: str):
    if not sys.stdin.isatty():
        return
    if "insufficient_quota" not in ai_text and "Error code: 429" not in ai_text:
        return
    try:
        choice = input("\nOpenAI quota error. Update API key now? [y/N]: ").strip().lower()
    except EOFError:
        return
    if choice != "y":
        return

    new_key = getpass.getpass("Enter new OPENAI_API_KEY: ").strip()
    if not new_key:
        print_error("No key entered. Keeping existing key.")
        return

    os.environ["OPENAI_API_KEY"] = new_key
    config = Config()
    config.openai_api_key = new_key
    try:
        config.save()
        print_success("API key updated in config.")
    except Exception as exc:
        print_error(f"Failed to save API key: {exc}")


def _resolve_backup_dir(config: Config, udid: Optional[str], backup_path: Optional[str]) -> Path:
    if backup_path:
        return Path(backup_path).expanduser()
    if udid:
        return config.backup_root / udid
    return config.backup_root


def _load_plist_bytes(data: bytes):
    try:
        return plistlib.loads(data)
    except Exception:
        return None


def _post_run_menu(tool: iSpyTool, device, report: dict):
    if not sys.stdin.isatty():
        return
    while True:
        print("\nWhat do you want to do next?")
        print("1) Run full diagnostic again")
        print("2) Run quick check")
        print("3) Run specific modules")
        print("4) Export report (json)")
        print("5) Export report (txt)")
        print("6) Exit")
        choice = input("Select option [1-6]: ").strip()

        if choice == "1":
            modules_list = tool.module_manager.get_available_modules()
            report = _run_with_progress(tool, device, modules_list, include_ai=True)
            _display_report(report, verbose=True)
        elif choice == "2":
            modules_list = ['battery', 'storage', 'network', 'security']
            report = _run_with_progress(tool, device, modules_list, include_ai=False)
            _display_report(report, verbose=False)
        elif choice == "3":
            available = tool.module_manager.get_available_modules()
            print("\nAvailable modules:")
            module_info = tool.module_manager.get_module_info()
            for idx, name in enumerate(available, start=1):
                desc = module_info.get(name, "")
                suffix = f" - {desc}" if desc else ""
                print(f"{idx}) {name}{suffix}")
            raw = input("Select modules by number or name (comma-separated): ").strip()
            tokens = [t.strip() for t in raw.split(",") if t.strip()]
            modules_list = []
            for token in tokens:
                if token.isdigit():
                    index = int(token) - 1
                    if 0 <= index < len(available):
                        modules_list.append(available[index])
                else:
                    modules_list.append(token)
            if not modules_list:
                print_error("No modules selected.")
                continue
            report = _run_with_progress(tool, device, modules_list, include_ai=False)
            _display_report(report, verbose=True)
        elif choice == "4":
            output_path = tool.export_report(report, format="json")
            print_success(f"Report saved to: {output_path}")
        elif choice == "5":
            output_path = tool.export_report(report, format="txt")
            print_success(f"Report saved to: {output_path}")
        elif choice == "6":
            break
        else:
            print_error("Invalid selection.")


def _main_argparse():
    """Fallback CLI using argparse when click is not available"""
    parser = argparse.ArgumentParser(
        description='iSpy - iOS Device Diagnostic Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ispy devices          List connected devices
  ispy diagnose         Run diagnostics
  ispy quick            Quick diagnostic check
  ispy modules          List available modules
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # devices command
    subparsers.add_parser('devices', help='List connected iOS devices')

    # diagnose command
    diag_parser = subparsers.add_parser('diagnose', help='Run diagnostics')
    diag_parser.add_argument('-u', '--udid', help='Device UDID')
    diag_parser.add_argument('-m', '--modules', action='append', help='Specific modules')
    diag_parser.add_argument('-o', '--output', help='Output file path')

    # quick command
    quick_parser = subparsers.add_parser('quick', help='Quick diagnostic check')
    quick_parser.add_argument('-u', '--udid', help='Device UDID')

    # modules command
    subparsers.add_parser('modules', help='List available modules')

    # version command
    subparsers.add_parser('version', help='Show version')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    display_banner()
    tool = iSpyTool()

    if args.command == 'version':
        from . import __version__
        print(f"iSpy version {__version__}")

    elif args.command == 'devices':
        devices_list = tool.get_connected_devices()
        if not devices_list:
            print("No iOS devices found.")
            sys.exit(1)
        print("\nConnected iOS Devices:")
        print("-" * 60)
        for device in devices_list:
            print(f"  Name: {device.name}")
            print(f"  Model: {device.model}")
            print(f"  iOS: {device.ios_version}")
            print(f"  UDID: {device.udid}")
            print("-" * 60)

    elif args.command == 'modules':
        available = tool.get_available_modules()
        print("\nAvailable Modules:")
        print("-" * 40)
        for name, desc in available.items():
            print(f"  {name}: {desc}")

    elif args.command == 'diagnose':
        device = tool.get_device(args.udid if hasattr(args, 'udid') else None)
        if not device:
            print("No device found.")
            sys.exit(1)
        print(f"\nRunning diagnostics on: {device.name}")
        modules_list = args.modules if hasattr(args, 'modules') and args.modules else None
        modules_list = modules_list or tool.module_manager.get_available_modules()
        report = _run_with_progress(tool, device, modules_list, include_ai=False)
        _display_report(report, verbose=True)
        _post_run_menu(tool, device, report)

        if hasattr(args, 'output') and args.output:
            output_path = tool.export_report(report, Path(args.output))
            print(f"Report saved to: {output_path}")

    elif args.command == 'quick':
        device = tool.get_device(args.udid if hasattr(args, 'udid') else None)
        if not device:
            print("No device found.")
            sys.exit(1)
        print(f"\nQuick check on: {device.name}")
        modules_list = ['battery', 'storage', 'network', 'security']
        report = _run_with_progress(tool, device, modules_list, include_ai=False)
        _display_report(report, verbose=False)
        _post_run_menu(tool, device, report)


# Click-based CLI (only defined if click is available)
if CLICK_AVAILABLE:
    @click.group()
    @click.option('--config', '-c', type=click.Path(exists=True), help='Config file path')
    @click.option('--verbose', '-v', is_flag=True, help='Verbose output')
    @click.pass_context
    def cli(ctx, config, verbose):
        """iSpy - iOS Device Diagnostic Tool

        Comprehensive diagnostics for iOS devices with AI-powered analysis.
        """
        ctx.ensure_object(dict)
        ctx.obj['verbose'] = verbose

        if config:
            ctx.obj['config'] = Config(Path(config))
        else:
            ctx.obj['config'] = Config()

        ctx.obj['tool'] = iSpyTool(ctx.obj['config'])
        display_banner()

    @cli.command()
    @click.pass_context
    def devices(ctx):
        """List connected iOS devices"""
        tool: iSpyTool = ctx.obj['tool']
        device_list = tool.get_connected_devices()

        if not device_list:
            print_error("No iOS devices found. Ensure device is connected and trusted.")
            sys.exit(1)

        if RICH_AVAILABLE and console:
            table = Table(title="Connected iOS Devices")
            table.add_column("Name", style="cyan")
            table.add_column("Model", style="green")
            table.add_column("iOS", style="yellow")
            table.add_column("UDID", style="dim")

            for device in device_list:
                table.add_row(
                    device.name or "Unknown",
                    device.model or "Unknown",
                    device.ios_version or "Unknown",
                    device.udid[:16] + "..." if len(device.udid) > 16 else device.udid
                )
            console.print(table)
        else:
            print("\nConnected iOS Devices:")
            print("-" * 60)
            for device in device_list:
                print(f"  Name: {device.name}")
                print(f"  Model: {device.model}")
                print(f"  iOS: {device.ios_version}")
                print(f"  UDID: {device.udid}")
                print("-" * 60)

    @cli.command()
    @click.option('--udid', '-u', help='Device UDID (uses first device if not specified)')
    @click.option('--modules', '-m', multiple=True, help='Specific modules to run')
    @click.option('--ai/--no-ai', default=False, help='Include AI analysis')
    @click.option('--output', '-o', type=click.Path(), help='Output file path')
    @click.option('--format', '-f', type=click.Choice(['json', 'txt']), default='json', help='Output format')
    @click.pass_context
    def diagnose(ctx, udid, modules, ai, output, format):
        """Run diagnostics on a device"""
        tool: iSpyTool = ctx.obj['tool']
        verbose = ctx.obj['verbose']

        device = tool.get_device(udid)
        if not device:
            print_error("No device found. Connect an iOS device and try again.")
            sys.exit(1)

        print_output(f"\nRunning diagnostics on: {device.name} ({device.model})")

        modules_list = list(modules) if modules else tool.module_manager.get_available_modules()
        report = _run_with_progress(tool, device, modules_list, include_ai=ai)

        _display_report(report, verbose)
        _post_run_menu(tool, device, report)

        if output:
            output_path = tool.export_report(report, Path(output), format)
            print_success(f"Report saved to: {output_path}")

    @cli.command()
    @click.option('--udid', '-u', help='Device UDID')
    @click.pass_context
    def quick(ctx, udid):
        """Run quick diagnostic check (essential modules only)"""
        tool: iSpyTool = ctx.obj['tool']

        device = tool.get_device(udid)
        if not device:
            print_error("No device found.")
            sys.exit(1)

        print_output(f"\nQuick check on: {device.name}")
        modules_list = ['battery', 'storage', 'network', 'security']
        report = _run_with_progress(tool, device, modules_list, include_ai=False)
        _display_report(report, verbose=False)
        _post_run_menu(tool, device, report)

    @cli.command()
    @click.option('--udid', '-u', help='Device UDID')
    @click.option('--output', '-o', type=click.Path(), help='Output file path')
    @click.pass_context
    def full(ctx, udid, output):
        """Run full diagnostic with AI analysis"""
        tool: iSpyTool = ctx.obj['tool']

        device = tool.get_device(udid)
        if not device:
            print_error("No device found.")
            sys.exit(1)

        print_output(f"\nFull diagnostic on: {device.name}")
        modules_list = tool.module_manager.get_available_modules()
        report = _run_with_progress(tool, device, modules_list, include_ai=True)
        _display_report(report, verbose=True)
        _post_run_menu(tool, device, report)

        if output:
            output_path = tool.export_report(report, Path(output))
            print_success(f"Report saved to: {output_path}")

    @cli.command('modules')
    @click.pass_context
    def modules_cmd(ctx):
        """List available diagnostic modules"""
        tool: iSpyTool = ctx.obj['tool']
        available = tool.get_available_modules()

        if RICH_AVAILABLE and console:
            table = Table(title="Available Diagnostic Modules")
            table.add_column("Module", style="cyan")
            table.add_column("Description", style="white")

            for name, desc in available.items():
                table.add_row(name, desc)
            console.print(table)
        else:
            print("\nAvailable Modules:")
            print("-" * 40)
            for name, desc in available.items():
                print(f"  {name}: {desc}")

    @cli.group()
    @click.pass_context
    def backup(ctx):
        """Backup acquisition and extraction utilities"""
        pass

    @backup.command("create")
    @click.option('--udid', '-u', help='Device UDID')
    @click.option('--output', '-o', type=click.Path(), help='Backup output directory')
    @click.option('--full/--no-full', default=False, help='Force full backup')
    @click.option('--network/--no-network', default=False, help='Use network device')
    @click.option('--interactive/--no-interactive', default=False, help='Prompt for passwords if needed')
    @click.pass_context
    def backup_create(ctx, udid, output, full, network, interactive):
        """Create a local backup using idevicebackup2"""
        config: Config = ctx.obj['config']
        tool: iSpyTool = ctx.obj['tool']

        device = None
        selected_udid = udid
        if not selected_udid:
            device_list = tool.get_connected_devices()
            if not device_list:
                print_error("No iOS devices found. Ensure device is connected and trusted.")
                sys.exit(1)
            if not sys.stdin.isatty():
                print_error("No UDID provided and no TTY available to select a device.")
                sys.exit(1)
            print_output("Select a device for backup:")
            for idx, dev in enumerate(device_list, start=1):
                print_output(f"{idx}) {dev.name or 'Unknown'} | {dev.model or 'Unknown'} | iOS {dev.ios_version or 'Unknown'} | {dev.udid}")
            choice = click.prompt("Enter device number", type=int)
            if choice < 1 or choice > len(device_list):
                print_error("Invalid selection.")
                sys.exit(1)
            device = device_list[choice - 1]
            selected_udid = device.udid
        else:
            device = tool.get_device(selected_udid) if config.auto_select_device else None
        if not device and not selected_udid:
            print_error("No device selected. Use --udid or run `ispy backup devices`.")
            sys.exit(1)
        backup_dir = Path(output).expanduser() if output else _resolve_backup_dir(
            config, device.udid if device else selected_udid, None
        )

        manager = BackupManager(udid=device.udid if device else selected_udid, network=network, interactive=interactive)
        print_output(f"Creating backup at: {backup_dir}")
        try:
            manager.backup(backup_dir, full=full)
            print_success("Backup completed.")
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @backup.command("devices")
    @click.pass_context
    def backup_devices(ctx):
        """List connected devices for backups"""
        tool: iSpyTool = ctx.obj['tool']
        device_list = tool.get_connected_devices()
        if not device_list:
            print_error("No iOS devices found. Ensure device is connected and trusted.")
            sys.exit(1)
        if RICH_AVAILABLE and console:
            table = Table(title="Connected iOS Devices")
            table.add_column("Name", style="cyan")
            table.add_column("Model", style="green")
            table.add_column("iOS", style="yellow")
            table.add_column("UDID", style="dim")
            for device in device_list:
                table.add_row(
                    device.name or "Unknown",
                    device.model or "Unknown",
                    device.ios_version or "Unknown",
                    device.udid
                )
            console.print(table)
        else:
            print("\nConnected iOS Devices:")
            print("-" * 60)
            for device in device_list:
                print(f"  Name: {device.name}")
                print(f"  Model: {device.model}")
                print(f"  iOS: {device.ios_version}")
                print(f"  UDID: {device.udid}")
                print("-" * 60)

    @backup.command("info")
    @click.option('--udid', '-u', help='Device UDID')
    @click.option('--backup', '-b', 'backup_path', type=click.Path(), help='Backup directory')
    @click.pass_context
    def backup_info(ctx, udid, backup_path):
        """Show backup metadata using idevicebackup2"""
        config: Config = ctx.obj['config']
        backup_dir = _resolve_backup_dir(config, udid, backup_path)
        manager = BackupManager(udid=udid)
        try:
            proc = manager.info(backup_dir)
            print(proc.stdout.strip())
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @backup.command("list")
    @click.option('--udid', '-u', help='Device UDID')
    @click.option('--backup', '-b', 'backup_path', type=click.Path(), help='Backup directory')
    @click.pass_context
    def backup_list(ctx, udid, backup_path):
        """List files using idevicebackup2 (CSV output)"""
        config: Config = ctx.obj['config']
        backup_dir = _resolve_backup_dir(config, udid, backup_path)
        manager = BackupManager(udid=udid)
        try:
            proc = manager.list_files(backup_dir)
            print(proc.stdout.strip())
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @backup.command("encryption")
    @click.option('--udid', '-u', help='Device UDID')
    @click.option('--backup', '-b', 'backup_path', type=click.Path(), help='Backup directory')
    @click.option('--enable/--disable', default=True, help='Enable or disable encryption')
    @click.option('--password', help='Encryption password')
    @click.pass_context
    def backup_encryption(ctx, udid, backup_path, enable, password):
        """Enable or disable backup encryption"""
        config: Config = ctx.obj['config']
        backup_dir = _resolve_backup_dir(config, udid, backup_path)
        manager = BackupManager(udid=udid, interactive=not password)
        try:
            manager.set_encryption(backup_dir, enabled=enable, password=password)
            print_success("Backup encryption updated.")
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @backup.command("catalog")
    @click.option('--backup', '-b', 'backup_path', type=click.Path(), required=True, help='Backup directory')
    @click.option('--domain', help='Filter by domain')
    @click.option('--contains', help='Filter by path substring')
    @click.option('--limit', type=int, default=200, help='Limit number of rows')
    @click.pass_context
    def backup_catalog(ctx, backup_path, domain, contains, limit):
        """List files from Manifest.db"""
        try:
            catalog = BackupCatalog(Path(backup_path).expanduser())
            records = catalog.list_records(domain=domain, contains=contains, limit=limit)
            for record in records:
                print(f"{record.domain}/{record.relative_path} :: {record.file_id}")
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @backup.command("extract")
    @click.option('--backup', '-b', 'backup_path', type=click.Path(), required=True, help='Backup directory')
    @click.option('--domain', required=True, help='Domain name (e.g., HomeDomain)')
    @click.option('--path', 'relative_path', help='Relative path inside domain')
    @click.option('--output', '-o', type=click.Path(), help='Output file or directory')
    @click.pass_context
    def backup_extract(ctx, backup_path, domain, relative_path, output):
        """Extract a file or domain from a backup"""
        try:
            catalog = BackupCatalog(Path(backup_path).expanduser())
            if relative_path:
                record = catalog.find_record(domain, relative_path)
                if not record:
                    print_error("File not found in backup.")
                    sys.exit(1)
                if not output:
                    print_error("Output path required for file extraction.")
                    sys.exit(1)
                path = catalog.extract_file(record, Path(output).expanduser())
                print_success(f"Extracted to: {path}")
            else:
                if not output:
                    print_error("Output directory required for domain extraction.")
                    sys.exit(1)
                count = catalog.extract_domain(domain, Path(output).expanduser())
                print_success(f"Extracted {count} files.")
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @cli.group()
    @click.pass_context
    def parse(ctx):
        """Parse raw files from a backup"""
        pass

    @parse.command("plist")
    @click.option('--backup', '-b', 'backup_path', type=click.Path(), required=True, help='Backup directory')
    @click.option('--domain', required=True, help='Domain name')
    @click.option('--path', 'relative_path', required=True, help='Relative path inside domain')
    @click.option('--output', '-o', type=click.Path(), help='Output JSON file')
    @click.pass_context
    def parse_plist(ctx, backup_path, domain, relative_path, output):
        """Parse a plist from the backup and print JSON"""
        try:
            catalog = BackupCatalog(Path(backup_path).expanduser())
            record = catalog.find_record(domain, relative_path)
            if not record:
                print_error("File not found in backup.")
                sys.exit(1)
            data = _load_plist_bytes(catalog.read_file_bytes(record))
            payload = json.dumps(data, indent=2, default=str)
            if output:
                Path(output).expanduser().write_text(payload)
                print_success(f"Saved to: {output}")
            else:
                print(payload)
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @parse.command("sqlite")
    @click.option('--backup', '-b', 'backup_path', type=click.Path(), required=True, help='Backup directory')
    @click.option('--domain', required=True, help='Domain name')
    @click.option('--path', 'relative_path', required=True, help='Relative path inside domain')
    @click.option('--query', help='SQL query to run')
    @click.option('--limit', type=int, default=200, help='Limit rows')
    @click.pass_context
    def parse_sqlite(ctx, backup_path, domain, relative_path, query, limit):
        """Run a SQL query against a SQLite DB from backup"""
        try:
            catalog = BackupCatalog(Path(backup_path).expanduser())
            record = catalog.find_record(domain, relative_path)
            if not record:
                print_error("File not found in backup.")
                sys.exit(1)
            db_path = catalog.get_file_path(record)
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                if query:
                    cursor = conn.execute(query + f" LIMIT {int(limit)}")
                    rows = [dict(row) for row in cursor.fetchall()]
                    print(json.dumps(rows, indent=2, default=str))
                else:
                    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    print(json.dumps(tables, indent=2))
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @cli.group()
    @click.pass_context
    def case(ctx):
        """Build and inspect a parsed case file"""
        pass

    @case.command("build")
    @click.option('--backup', '-b', 'backup_path', type=click.Path(), required=True, help='Backup directory')
    @click.option('--output', '-o', type=click.Path(), help='Output case JSON file')
    @click.pass_context
    def case_build(ctx, backup_path, output):
        """Build a case JSON from backup artifacts"""
        config: Config = ctx.obj['config']
        backup_dir = Path(backup_path).expanduser()
        if output:
            output_path = Path(output).expanduser()
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = config.case_output_dir / f"ispy_case_{timestamp}.json"

        try:
            builder = CaseBuilder(backup_dir)
            saved = builder.save(output_path)
            print_success(f"Case saved to: {saved}")
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @case.command("timeline")
    @click.option('--case', 'case_path', type=click.Path(), help='Case JSON file')
    @click.option('--backup', 'backup_path', type=click.Path(), help='Backup directory')
    @click.option('--limit', type=int, default=200, help='Limit events')
    @click.pass_context
    def case_timeline(ctx, case_path, backup_path, limit):
        """Build a simple timeline view"""
        if not case_path and not backup_path:
            print_error("Provide --case or --backup.")
            sys.exit(1)
        try:
            if case_path:
                case_data = load_case(Path(case_path).expanduser())
            else:
                case_data = CaseBuilder(Path(backup_path).expanduser()).build()
            events = build_timeline(case_data, limit=limit)
            print(json.dumps(events, indent=2, default=str))
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @case.command("search")
    @click.option('--case', 'case_path', type=click.Path(), help='Case JSON file')
    @click.option('--backup', 'backup_path', type=click.Path(), help='Backup directory')
    @click.option('--query', '-q', required=True, help='Search query')
    @click.option('--limit', type=int, default=50, help='Limit matches')
    @click.pass_context
    def case_search(ctx, case_path, backup_path, query, limit):
        """Search parsed artifacts"""
        if not case_path and not backup_path:
            print_error("Provide --case or --backup.")
            sys.exit(1)
        try:
            if case_path:
                case_data = load_case(Path(case_path).expanduser())
            else:
                case_data = CaseBuilder(Path(backup_path).expanduser()).build()
            results = search_case(case_data, query, limit=limit)
            print(json.dumps(results, indent=2, default=str))
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @case.command("report")
    @click.option('--case', 'case_path', type=click.Path(), help='Case JSON file')
    @click.option('--backup', 'backup_path', type=click.Path(), help='Backup directory')
    @click.option('--format', 'report_format', type=click.Choice(['json', 'csv', 'html']), default='json')
    @click.option('--output', '-o', type=click.Path(), required=True, help='Output report file')
    @click.pass_context
    def case_report(ctx, case_path, backup_path, report_format, output):
        """Export a report summary"""
        if not case_path and not backup_path:
            print_error("Provide --case or --backup.")
            sys.exit(1)
        try:
            if case_path:
                case_data = load_case(Path(case_path).expanduser())
            else:
                case_data = CaseBuilder(Path(backup_path).expanduser()).build()
            path = export_case_report(case_data, Path(output).expanduser(), report_format)
            print_success(f"Report saved to: {path}")
        except Exception as exc:
            print_error(str(exc))
            sys.exit(1)

    @cli.command()
    @click.argument('question')
    @click.option('--udid', '-u', help='Device UDID for context')
    @click.option('--case', 'case_path', type=click.Path(), help='Case JSON file for AI context')
    @click.option('--backup', 'backup_path', type=click.Path(), help='Backup directory to build context')
    @click.pass_context
    def ask(ctx, question, udid, case_path, backup_path):
        """Ask AI a question about iOS diagnostics"""
        tool: iSpyTool = ctx.obj['tool']

        if not tool.ai_engine:
            print_error("AI not configured. Set OPENAI_API_KEY in config or environment.")
            sys.exit(1)

        context = None
        if case_path:
            try:
                context = load_case(Path(case_path).expanduser())
            except Exception as exc:
                print_error(f"Failed to load case: {exc}")
                sys.exit(1)
        elif backup_path:
            try:
                builder = CaseBuilder(Path(backup_path).expanduser())
                context = builder.build()
            except Exception as exc:
                print_error(f"Failed to build case: {exc}")
                sys.exit(1)
        elif udid:
            device = tool.get_device(udid)
            if device:
                context = {"device": device.to_dict()}

        print_output("\nAsking AI...")
        response = tool.analyze_with_ai(question, context)

        if response:
            if RICH_AVAILABLE and console:
                console.print(Panel(response, title="AI Response", border_style="green"))
            else:
                print("\nAI Response:")
                print("-" * 40)
                print(response)
        else:
            print_error("No response from AI.")

    @cli.command()
    @click.pass_context
    def version(ctx):
        """Show iSpy version"""
        from . import __version__
        print_output(f"iSpy version {__version__}")


def main():
    """Main entry point"""
    if CLICK_AVAILABLE:
        cli(obj={})
    else:
        _main_argparse()


if __name__ == '__main__':
    main()
