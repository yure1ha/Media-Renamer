from pathlib import Path
from typing import List, Optional, Tuple

import rename_log
import renamer


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} [Y/N]: ").strip().upper()
        if answer in ("Y", "N"):
            return answer == "Y"
        print("Enter 'Y' or 'N'.")


def interactive_mode(directory_path: Optional[Path]) -> None:
    while True:
        while directory_path is None:
            user_input = input("Directory Path: ").strip()
            user_input = user_input.replace("\\ ", " ")
            directory_path = Path(user_input)

            if not directory_path.is_dir():
                print(f"Invalid Path: '{directory_path}'")
                directory_path = None

        root_directory_series_name = directory_path.name
        user_series_name = input("[Optional][Press Enter to Skip] Series Name: ").strip()

        if user_series_name:
            use_root_directory_series_name = ask_yes_no(
                f"Use root directory series name '{root_directory_series_name}' for renaming instead of '{user_series_name}'?"
            )
            series_name = user_series_name
            rename_series_name = root_directory_series_name if use_root_directory_series_name else user_series_name
        else:
            series_name = root_directory_series_name
            rename_series_name = root_directory_series_name

        dry_run = ask_yes_no("Dry Run")

        if ask_yes_no("Undo Previous Rename"):
            rename_log.undo_rename(directory_path, dry_run)

        season_directories = renamer.find_season_directory(directory_path)
        renamed: List[Tuple[str, str]] = []

        if season_directories:
            print(f"Found season directories: {[p.name for p, _ in season_directories]}")
            for season_directory_path, season_number in season_directories:
                updated_path = renamer.rename_season_directory(season_directory_path, season_number, renamed, dry_run)
                if not renamer.rename_season_directory_files(
                        rename_series_name, (updated_path, season_number), series_name, renamed, dry_run
                ):
                    print("No episodes were renamed in season directory.")
        else:
            print("No season directories found, attempting to rename files in root directory.")
            if not renamer.rename_root_directory_files(
                    directory_path, rename_series_name, series_name, renamed, dry_run
            ):
                print("No episodes were renamed in root directory.")

        rename_log.save_rename_log(renamed, directory_path, dry_run)
        print(f"Rename Log: '{directory_path / rename_log.RENAME_LOG_FILE}'")
        print("Process Complete")

        if renamed:
            print("\n\nRenamed Files:\n")
            for _, new_path_str in renamed:
                new_path = Path(new_path_str)
                print(new_path.name)
                print(new_path)
                print()

        run_again = ask_yes_no("Run Again")
        if not run_again:
            print("Exiting...\n")
            return

        use_same_directory = ask_yes_no("Use Same Directory")
        print()
        if not use_same_directory:
            directory_path = None
