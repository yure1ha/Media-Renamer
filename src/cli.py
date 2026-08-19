import shlex
from pathlib import Path


def get_root_dir() -> Path:
    root_dir = input("\nEnter Path: ").strip()

    if not root_dir:
        raise ValueError("[ERROR] No path provided\n")

    try:
        tokens = shlex.split(root_dir)

    except ValueError as e:
        raise ValueError(f"[ERROR] Could not parse path '{root_dir}': {e}\n")

    if len(tokens) != 1:
        raise ValueError("[ERROR] Enter a single path\n")

    root_dir_path = Path(tokens[0])

    if not root_dir_path.is_dir():
        raise NotADirectoryError(
            f"[ERROR] '{root_dir}' is not a valid directory\n"
        )

    return Path(root_dir_path).expanduser().resolve()


def get_series_name() -> str:
    name = input("Enter Series Name: ")
    return name


def ask_yes_no(prompt: str) -> bool:
    while True:
        yes_no = input(f"{prompt} [Y/N]: ").strip().lower()

        if yes_no not in ("y", "n"):
            print("[ERROR] Enter Y or N\n")

        return yes_no == "y"


def is_dry_run() -> bool:
    return ask_yes_no("Dry Run?")


def is_undo_rename() -> bool:
    return ask_yes_no("Undo Rename?")


def is_run_again() -> bool:
    return ask_yes_no("Run Again?")


def is_same_dir() -> bool:
    return ask_yes_no("Use Same Directory?")
