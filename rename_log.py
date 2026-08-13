import json
from pathlib import Path
from typing import List, Tuple

import platform_utils

RENAME_LOG_FILE = "rename_log.json"


def save_rename_log(rename_log: List[Tuple[str, str]], root_directory_path: Path, dry_run: bool) -> None:
    log_path = root_directory_path / RENAME_LOG_FILE
    if dry_run:
        print("[Dry Run] Skipping saving rename log.")
        return

    try:
        with log_path.open("w") as f:
            json.dump(rename_log, f, indent=2)
    except Exception as error:
        print(f"Error saving rename log: {error}")


def undo_rename(root_directory_path: Path, dry_run: bool) -> None:
    log_path = root_directory_path / RENAME_LOG_FILE

    if not log_path.is_file():
        print("No rename log found. Cannot undo rename.")
        return

    if dry_run:
        print("[Dry Run] Undo not performed.")
        return

    try:
        with log_path.open("r") as log_file:
            rename_log_entries = json.load(log_file)
        rename_log: List[Tuple[str, str]] = [
            (str(original_path), str(new_path)) for original_path, new_path in rename_log_entries
        ]
    except Exception as error:
        print(f"Error reading rename log: {error}")
        return

    restored_files = []

    for original_path_string, new_path_string in reversed(rename_log):
        original_path = Path(original_path_string)
        new_path = Path(new_path_string)
        if new_path.exists():
            print(f"Restoring '{new_path}' to '{original_path}'")
            try:
                new_path.rename(original_path)
                platform_utils.macos_hide_extension(original_path)
                restored_files.append(original_path)
            except Exception as error:
                print(f"Error restoring file: {error}")

    try:
        log_path.unlink()
    except Exception as error:
        print(f"Error deleting rename log file: {error}")

    if restored_files:
        print("\n\nRestored Files:\n")
        for restored_file_path in restored_files:
            print(restored_file_path.name)
            print(restored_file_path)
            print()
