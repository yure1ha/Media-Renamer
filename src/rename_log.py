import json
from pathlib import Path

from src import models


class RenameLog:
    RENAME_LOG = "rename_log.json"

    def __init__(self, root_dir: Path, dry_run: bool) -> None:
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.rename_log: Path = self.root_dir / self.RENAME_LOG
        self.entries: list[models.Rename] = []

    def record(self, rename: models.Rename) -> None:
        self.entries.append(rename)

    def save(self) -> None:
        if self.dry_run:
            print("[DRY RUN] Skipping rename log\n")
            return

        try:
            with self.rename_log.open("w", encoding="utf-8") as f:
                data = [
                    (rename.old_path.as_posix(), rename.new_path.as_posix())
                    for rename in self.entries
                ]

                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(
                f"[ERROR] Failed to save rename log to '{self.rename_log}': "
                f"{e}\n")
            return

    def load(self) -> list[models.Rename]:
        if not self.rename_log.is_file():
            print("[ERROR] No rename log found\n")
            return []

        try:
            with self.rename_log.open("r", encoding="utf-8") as f:
                return [models.Rename(
                    old_path=Path(old_path),
                    new_path=Path(new_path))
                    for old_path, new_path in json.load(f)]

        except Exception as e:
            print(
                f"[ERROR] Failed to read rename log at '{self.rename_log}': "
                f"{e}\n")
            return []
