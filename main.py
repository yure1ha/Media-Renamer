import argparse
from pathlib import Path
from typing import Optional

import cli

def main() -> None:
    parser = argparse.ArgumentParser(description="Rename series files and directories.")
    parser.add_argument(
        "directory_path",
        nargs="?",
        type=str,
        help="Root directory path containing the series"
    )
    args = parser.parse_args()

    directory_path: Optional[Path] = None
    if args.directory_path:
        possible_path = Path(args.directory_path)
        if possible_path.is_dir():
            directory_path = possible_path
        else:
            print(f"Invalid Path: '{possible_path}'")

    cli.interactive_mode(directory_path)


if __name__ == "__main__":
    main()
