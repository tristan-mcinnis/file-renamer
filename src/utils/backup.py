"""Backup and tracking utilities for file renames."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class RenameTracker:
    """Track all file renames for undo functionality."""

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize rename tracker.

        Args:
            log_dir: Directory to store rename logs (default: ~/.file-renamer/)
        """
        if log_dir is None:
            log_dir = Path.home() / ".file-renamer"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"renames_{timestamp}.json"

        self.renames: List[Dict] = []

    def add_rename(
        self,
        old_path: Path,
        new_path: Path,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """
        Record a rename operation.

        Args:
            old_path: Original file path
            new_path: New file path
            success: Whether rename succeeded
            error: Error message if failed
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "old_path": str(old_path.absolute()),
            "new_path": str(new_path.absolute()),
            "old_name": old_path.name,
            "new_name": new_path.name,
            "directory": str(old_path.parent.absolute()),
            "success": success,
            "error": error,
        }

        self.renames.append(record)

    def save(self):
        """Save rename log to disk."""
        with open(self.log_file, "w") as f:
            json.dump(
                {
                    "session_start": datetime.now().isoformat(),
                    "total_renames": len(self.renames),
                    "successful": len([r for r in self.renames if r["success"]]),
                    "failed": len([r for r in self.renames if not r["success"]]),
                    "renames": self.renames,
                },
                f,
                indent=2,
            )

        print(f"\n✅ Rename log saved: {self.log_file}")

    def get_summary(self) -> str:
        """Get summary of rename operations."""
        successful = len([r for r in self.renames if r["success"]])
        failed = len([r for r in self.renames if not r["success"]])

        return (
            f"Rename Summary:\n"
            f"  Total: {len(self.renames)}\n"
            f"  Successful: {successful}\n"
            f"  Failed: {failed}\n"
            f"  Log file: {self.log_file}"
        )


def load_rename_log(log_file: Path) -> Dict:
    """
    Load a rename log file.

    Args:
        log_file: Path to log file

    Returns:
        Dictionary with rename data
    """
    with open(log_file, "r") as f:
        return json.load(f)


def list_rename_logs(log_dir: Optional[Path] = None) -> List[Path]:
    """
    List all rename log files.

    Args:
        log_dir: Directory containing logs (default: ~/.file-renamer/)

    Returns:
        List of log file paths, sorted by timestamp (newest first)
    """
    if log_dir is None:
        log_dir = Path.home() / ".file-renamer"

    if not log_dir.exists():
        return []

    logs = sorted(log_dir.glob("renames_*.json"), reverse=True)
    return logs


def undo_renames(log_file: Path, dry_run: bool = True) -> int:
    """
    Undo renames from a log file.

    Args:
        log_file: Path to rename log file
        dry_run: If True, only show what would be undone

    Returns:
        Number of files successfully reverted
    """
    log_data = load_rename_log(log_file)
    renames = log_data["renames"]

    # Filter only successful renames
    successful_renames = [r for r in renames if r["success"]]

    if not successful_renames:
        print("No successful renames to undo.")
        return 0

    print(f"\nFound {len(successful_renames)} renames to undo")
    print("-" * 60)

    reverted = 0

    for rename in successful_renames:
        old_path = Path(rename["old_path"])
        new_path = Path(rename["new_path"])

        # Check if new file exists
        if not new_path.exists():
            print(f"⚠️  File not found (already renamed?): {new_path.name}")
            continue

        # Check if we'd overwrite something
        if old_path.exists():
            print(f"⚠️  Cannot revert (original name exists): {old_path.name}")
            continue

        if dry_run:
            print(f"Would revert: {new_path.name} → {old_path.name}")
        else:
            try:
                new_path.rename(old_path)
                print(f"✅ Reverted: {new_path.name} → {old_path.name}")
                reverted += 1
            except Exception as e:
                print(f"❌ Error reverting {new_path.name}: {e}")

    if dry_run:
        print()
        print("This was a DRY RUN. Use --execute to actually revert.")
    else:
        print()
        print(f"✅ Successfully reverted {reverted} files")

    return reverted
