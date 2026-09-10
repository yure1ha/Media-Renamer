from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Episode:
    path: Path
    num: int


@dataclass(frozen=True)
class Season:
    path: Path
    num: int
    episodes: list[Episode]


@dataclass(frozen=True)
class Rename:
    old_path: Path
    new_path: Path

    @property
    def needs_rename(self) -> bool:
        return self.new_path != self.old_path


@dataclass(frozen=True)
class CLIArgs:
    root_dir: Path
    series_name: str
    undo_rename: bool
    dry_run: bool
    verbose: bool
