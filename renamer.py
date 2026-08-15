from pathlib import Path
from typing import List, Tuple

import parsing
import platform_utils


def zero_pad_number(number: int, maximum_number: int) -> str:
    padding_length = len(str(maximum_number))
    return str(number).zfill(padding_length)


def find_season_directory(root_directory_path: Path) -> List[Tuple[Path, int]]:
    season_directories = []
    for entry in root_directory_path.iterdir():
        if not entry.is_dir():
            continue

        match = parsing.SEASON_NUM_PATTERNS.search(entry.name)
        if match:
            season_number = int(match.group(1))
            season_directories.append((entry, season_number))

    return season_directories


def rename_season_directory(
        season_directory_path: Path,
        season_number: int,
        rename_log: List[Tuple[str, str]],
        dry_run: bool,
) -> Path:
    parent_directory = season_directory_path.parent
    new_directory_name = f"Season {season_number}"
    new_path = parent_directory / new_directory_name

    if season_directory_path != new_path:
        print(f"Renaming season directory '{season_directory_path}' -> '{new_path}'")
        if not dry_run:
            try:
                season_directory_path.rename(new_path)
            except Exception as error:
                print(f"Error renaming directory: {error}")
        else:
            print("[Dry Run] Skipping actual rename.")

        rename_log.append((str(season_directory_path), str(new_path)))

    return new_path


def try_extract_episode_numbers(filenames: List[str], series_name: str) -> List[int]:
    episode_numbers = []
    for filename in filenames:
        ep_num = parsing.extract_episode_num(filename, series_name)
        if ep_num is not None:
            episode_numbers.append(ep_num)
    return episode_numbers


def rename_season_directory_files(
        root_directory_name: str,
        season_directory_tuple: Tuple[Path, int],
        series_name: str,
        rename_log: List[Tuple[str, str]],
        dry_run: bool,
) -> bool:
    season_directory_path, season_number = season_directory_tuple
    filenames = [f.name for f in season_directory_path.iterdir() if f.is_file()]

    episode_numbers = try_extract_episode_numbers(filenames, series_name)
    if not episode_numbers:
        return False

    max_episode = max(episode_numbers)

    for filename in filenames:
        episode_number = parsing.extract_episode_num(filename, series_name)
        if episode_number is None:
            print(f"Skipping file without episode number: '{filename}'")
            continue

        padded = parsing.zero_pad_number(episode_number, max_episode)
        ext = Path(filename).suffix
        new_filename = f"{root_directory_name} [S{season_number}E{padded}]{ext}"

        old_path = season_directory_path / filename
        new_path = season_directory_path / new_filename

        if old_path != new_path:
            print(f"Renaming '{old_path}' to '{new_path}'")
            if not dry_run:
                try:
                    old_path.rename(new_path)
                    platform_utils.macos_hide_extension(new_path)
                except Exception as error:
                    print(f"Error renaming file: {error}")
            else:
                print("[Dry Run] Skipping actual rename.")

            rename_log.append((str(old_path), str(new_path)))

    return True


def rename_root_directory_files(
        root_directory_path: Path,
        root_directory_name: str,
        series_name: str,
        rename_log: List[Tuple[str, str]],
        dry_run: bool,
) -> bool:
    filenames = [f.name for f in root_directory_path.iterdir() if f.is_file()]

    episode_numbers = try_extract_episode_numbers(filenames, series_name)
    if not episode_numbers:
        return False

    maximum_episode_number = max(episode_numbers)

    for filename in filenames:
        episode_number = parsing.extract_episode_num(filename, series_name)
        if episode_number is None:
            print(f"Skipping file without episode number: '{filename}'")
            continue

        padded = parsing.zero_pad_number(episode_number, maximum_episode_number)
        filename_extension = Path(filename).suffix
        new_filename = f"{root_directory_name} [E{padded}]{filename_extension}"

        old_path = root_directory_path / filename
        new_path = root_directory_path / new_filename

        if old_path != new_path:
            print(f"Renaming '{old_path}' -> '{new_path}'")
            if not dry_run:
                try:
                    old_path.rename(new_path)
                    platform_utils.macos_hide_extension(new_path)
                except Exception as error:
                    print(f"Error renaming file: {error}")
            else:
                print("[Dry Run] Skipping actual rename.")

            rename_log.append((str(old_path), str(new_path)))

    return True
