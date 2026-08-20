import argparse
from pathlib import Path

from src.models import CLIArgs


def parse() -> CLIArgs:
    parser = argparse.ArgumentParser(
        description="Batch rename TV series"
    )

    parser.add_argument(
        "root_dir",
        type=Path,
        help="Target directory to rename",
    )

    parser.add_argument(
        "series_name",
        type=str,
        help="Target series name",
    )

    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Simulate renaming without making changes",
    )

    parser.add_argument(
        "-u",
        "--undo",
        action="store_true",
        help="Undo the previous rename operation",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )

    args = parser.parse_args()

    root_dir: Path = args.root_dir
    cleaned_path: Path = root_dir.expanduser().resolve()

    if not cleaned_path.is_dir():
        parser.error(f"[ERROR] {cleaned_path} is not a valid directory")

    return CLIArgs(
        root_dir=cleaned_path,
        series_name=args.series_name,
        undo_rename=args.undo,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
