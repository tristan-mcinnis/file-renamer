#!/usr/bin/env python3
"""
File Renamer - Intelligent file renaming using local language models.

Main CLI entry point.
"""

import sys
from pathlib import Path
from typing import List, Optional

import click
from tabulate import tabulate
from tqdm import tqdm

from src.extractors.document import DocumentExtractor
from src.models.client import LMStudioClient
from src.namers.formatter import FilenameFormatter
from src.utils.backup import RenameTracker
from src.utils.config import Config


@click.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True),
    default=".",
    help="Directory to process (default: current directory)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default=None,
    help="Path to config file (default: config.yaml)",
)
@click.option(
    "--execute",
    "-e",
    is_flag=True,
    help="Actually rename files (default: dry-run)",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt (use with --execute)",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Process subdirectories recursively",
)
@click.option(
    "--types",
    "-t",
    type=str,
    default=None,
    help="Comma-separated file extensions to process (e.g., pdf,docx)",
)
@click.option(
    "--batch-size",
    "-b",
    type=int,
    default=20,
    help="Number of files to process per batch (default: 20)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output",
)
def main(
    path: str,
    config: Optional[str],
    execute: bool,
    yes: bool,
    recursive: bool,
    types: Optional[str],
    batch_size: int,
    verbose: bool,
):
    """
    Intelligent file renaming using local language models.

    This tool analyzes file contents and generates descriptive,
    standardized filenames in kebab-case format.
    """
    try:
        # Load configuration
        cfg = Config(config)

        click.echo("=" * 60)
        click.echo("File Renamer - Intelligent file renaming")
        click.echo("=" * 60)
        click.echo()

        # Override dry-run if execute flag is set
        if execute:
            click.echo("⚠️  EXECUTE MODE: Files will be renamed!")
            if not yes:
                if not click.confirm("Are you sure you want to continue?"):
                    click.echo("Cancelled.")
                    return
        else:
            click.echo("🔍 DRY-RUN MODE: No files will be renamed")

        click.echo()

        # Initialize components
        client = LMStudioClient(
            base_url=cfg.lm_studio_url,
            text_model=cfg.text_model,
            vision_model=cfg.vision_model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
        )

        extractor = DocumentExtractor(
            max_length=cfg.get("extraction.max_text_length", 2000),
            max_pages=cfg.get("extraction.max_pdf_pages", 5),
        )

        formatter = FilenameFormatter(
            case_style=cfg.case_style,
            date_format=cfg.date_format,
            date_position=cfg.date_position,
            max_length=cfg.max_filename_length,
        )

        # Test LM Studio connection
        click.echo("Testing LM Studio connection...")
        if not client.test_connection():
            click.echo("❌ Could not connect to LM Studio. Please ensure it's running.")
            return

        click.echo("✅ Connected to LM Studio")
        click.echo()

        # Get files to process
        files = get_files_to_process(
            Path(path), cfg, recursive, types.split(",") if types else None
        )

        if not files:
            click.echo("No files found to process.")
            return

        click.echo(f"Found {len(files)} file(s) to process")
        click.echo()

        # Process files in batches to prevent system overload
        if len(files) > batch_size:
            click.echo(f"Processing in batches of {batch_size} files to prevent crashes")
            click.echo()

        results = []
        total_batches = (len(files) + batch_size - 1) // batch_size  # Ceiling division

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(files))
            batch_files = files[start_idx:end_idx]

            if total_batches > 1:
                click.echo(f"Batch {batch_num + 1}/{total_batches} ({len(batch_files)} files)")

            for file_path in tqdm(batch_files, desc=f"Processing batch {batch_num + 1}", disable=not verbose):
                result = process_file(file_path, extractor, client, formatter, cfg, verbose)
                if result:
                    results.append(result)

            # Small pause between batches to let system breathe
            if batch_num < total_batches - 1 and total_batches > 1:
                click.echo("Waiting 2 seconds before next batch...")
                import time
                time.sleep(2)
                click.echo()

        # Display results
        if results:
            click.echo()
            click.echo("Proposed renames:")
            click.echo()

            table_data = [
                [
                    r["original_name"],
                    "→",
                    r["new_name"],
                    "✅" if r["success"] else "❌",
                ]
                for r in results
            ]

            click.echo(
                tabulate(
                    table_data,
                    headers=["Original", "", "New Name", "Status"],
                    tablefmt="simple",
                )
            )

            # Execute renames if requested
            if execute:
                click.echo()
                click.echo("Renaming files...")

                # Initialize rename tracker
                tracker = RenameTracker()

                for result in results:
                    if result["success"]:
                        try:
                            old_path = result["old_path"]
                            new_path = result["new_path"]
                            old_path.rename(new_path)
                            click.echo(f"✅ Renamed: {new_path.name}")

                            # Track successful rename
                            tracker.add_rename(old_path, new_path, success=True)
                        except Exception as e:
                            click.echo(f"❌ Error renaming {old_path.name}: {e}")

                            # Track failed rename
                            tracker.add_rename(
                                old_path,
                                result.get("new_path", old_path),
                                success=False,
                                error=str(e)
                            )

                # Save tracking log
                tracker.save()

                click.echo()
                click.echo(f"✅ Renamed {len([r for r in results if r['success']])} files")
                click.echo()
                click.echo(tracker.get_summary())
        else:
            click.echo("No files were processed.")

    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def get_files_to_process(
    directory: Path,
    config: Config,
    recursive: bool,
    filter_types: Optional[List[str]],
) -> List[Path]:
    """Get list of files to process."""
    files = []
    supported_exts = config.all_supported_extensions()

    # Filter to specific types if requested
    if filter_types:
        supported_exts = [
            ext for ext in supported_exts if ext.lstrip(".") in filter_types
        ]

    pattern = "**/*" if recursive else "*"

    for file_path in directory.glob(pattern):
        if not file_path.is_file():
            continue

        # Skip hidden files if configured
        if config.get("processing.skip_hidden", True) and file_path.name.startswith(
            "."
        ):
            continue

        # Check extension
        if file_path.suffix.lower() in supported_exts:
            files.append(file_path)

    return files


def process_file(
    file_path: Path,
    extractor: DocumentExtractor,
    client: LMStudioClient,
    formatter: FilenameFormatter,
    config: Config,
    verbose: bool,
) -> Optional[dict]:
    """Process a single file and return rename information."""
    try:
        # Skip if already formatted
        if config.skip_already_formatted and formatter.is_already_formatted(
            file_path.name
        ):
            if verbose:
                click.echo(f"⏭️  Skipping (already formatted): {file_path.name}")
            return None

        # Check if file is an image
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".tiff"}
        is_image = file_path.suffix.lower() in image_extensions

        if is_image:
            # Process image with vision model
            if verbose:
                click.echo(f"👁️  Analyzing image: {file_path.name}")

            analysis = client.analyze_image(str(file_path), config.vision_prompt)
            if not analysis:
                if verbose:
                    click.echo(f"⚠️  Could not analyze image: {file_path.name}")
                return None
        else:
            # Process document with text extraction
            if verbose:
                click.echo(f"📄 Extracting content from: {file_path.name}")

            content = extractor.extract(file_path)
            if not content:
                if verbose:
                    click.echo(f"⚠️  Could not extract content from: {file_path.name}")
                return None

            # Analyze with LLM
            if verbose:
                click.echo(f"🤖 Analyzing content...")

            analysis = client.analyze_text(content[:1000], config.text_prompt)
            if not analysis:
                if verbose:
                    click.echo(f"⚠️  Could not analyze: {file_path.name}")
                return None

        # Extract or generate date
        date = formatter.extract_date_from_filename(file_path.name)
        if not date:
            date = formatter.get_current_date()

        # Format new filename
        new_name = formatter.format_components(analysis, date)
        new_filename = f"{new_name}{file_path.suffix}"
        new_path = file_path.parent / new_filename

        return {
            "old_path": file_path,
            "new_path": new_path,
            "original_name": file_path.name,
            "new_name": new_filename,
            "success": True,
        }

    except Exception as e:
        if verbose:
            click.echo(f"❌ Error processing {file_path.name}: {e}")
        return {
            "old_path": file_path,
            "new_path": None,
            "original_name": file_path.name,
            "new_name": f"Error: {str(e)}",
            "success": False,
        }


if __name__ == "__main__":
    main()
