#!/usr/bin/env python3
"""
Undo file renames from a previous session.

This script reads the rename log and reverts files back to their original names.
"""

import sys
from pathlib import Path

import click
from tabulate import tabulate

from src.utils.backup import list_rename_logs, load_rename_log, undo_renames


@click.command()
@click.option(
    "--log",
    "-l",
    type=click.Path(exists=True),
    default=None,
    help="Path to specific log file to undo (default: most recent)",
)
@click.option(
    "--list",
    "-ls",
    is_flag=True,
    help="List all available rename logs",
)
@click.option(
    "--execute",
    "-e",
    is_flag=True,
    help="Actually revert files (default: dry-run)",
)
@click.option(
    "--show",
    "-s",
    is_flag=True,
    help="Show details of a log file",
)
def main(log: str, list: bool, execute: bool, show: bool):
    """
    Undo file renames from a previous session.

    By default, this shows what would be undone (dry-run mode).
    Use --execute to actually revert the files.
    """
    # List logs if requested
    if list:
        logs = list_rename_logs()

        if not logs:
            click.echo("No rename logs found in ~/.file-renamer/")
            return

        click.echo("Available rename logs:")
        click.echo("=" * 60)

        table_data = []
        for i, log_file in enumerate(logs, 1):
            try:
                log_data = load_rename_log(log_file)
                timestamp = log_file.stem.replace("renames_", "")
                # Format timestamp nicely
                timestamp_pretty = f"{timestamp[:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"

                table_data.append(
                    [
                        i,
                        timestamp_pretty,
                        log_data["total_renames"],
                        log_data["successful"],
                        log_file.name,
                    ]
                )
            except Exception as e:
                click.echo(f"⚠️  Error reading {log_file.name}: {e}")

        click.echo(
            tabulate(
                table_data,
                headers=["#", "Date/Time", "Total", "Success", "Log File"],
                tablefmt="simple",
            )
        )
        click.echo()
        click.echo(
            "To undo a session, use: python undo.py --log ~/.file-renamer/renames_TIMESTAMP.json"
        )
        return

    # Determine which log to use
    log_file = None

    if log:
        log_file = Path(log)
    else:
        # Use most recent log
        logs = list_rename_logs()
        if not logs:
            click.echo("❌ No rename logs found in ~/.file-renamer/")
            click.echo(
                "   Make sure you've run rename.py with --execute at least once."
            )
            return

        log_file = logs[0]
        click.echo(f"Using most recent log: {log_file.name}")

    if not log_file.exists():
        click.echo(f"❌ Log file not found: {log_file}")
        return

    # Show log details if requested
    if show:
        log_data = load_rename_log(log_file)

        click.echo()
        click.echo("=" * 60)
        click.echo("Rename Log Details")
        click.echo("=" * 60)
        click.echo(f"Session: {log_data['session_start']}")
        click.echo(f"Total renames: {log_data['total_renames']}")
        click.echo(f"Successful: {log_data['successful']}")
        click.echo(f"Failed: {log_data['failed']}")
        click.echo()

        click.echo("Files renamed:")
        click.echo("-" * 60)

        table_data = []
        for rename in log_data["renames"]:
            if rename["success"]:
                status = "✅"
            else:
                status = "❌"

            table_data.append(
                [status, rename["old_name"], "→", rename["new_name"]]
            )

        click.echo(
            tabulate(
                table_data, headers=["Status", "Original", "", "New"], tablefmt="simple"
            )
        )
        click.echo()
        return

    # Perform undo
    click.echo()
    click.echo("=" * 60)
    click.echo("Undo File Renames")
    click.echo("=" * 60)
    click.echo(f"Log file: {log_file}")
    click.echo()

    if not execute:
        click.echo("🔍 DRY-RUN MODE: No files will be reverted")
        click.echo()

    try:
        log_data = load_rename_log(log_file)
        click.echo(f"Session date: {log_data['session_start']}")
        click.echo(f"Total renames in log: {log_data['total_renames']}")
        click.echo()

        # Confirm if executing
        if execute:
            click.echo("⚠️  WARNING: This will revert your files!")
            if not click.confirm("Are you sure you want to continue?"):
                click.echo("Cancelled.")
                return

        reverted = undo_renames(log_file, dry_run=not execute)

        if not execute and reverted > 0:
            click.echo()
            click.echo(
                f"To actually revert these {reverted} files, run with --execute flag"
            )

    except Exception as e:
        click.echo(f"❌ Error: {e}")
        if "--verbose" in sys.argv:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
