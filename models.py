from dataclasses import dataclass
from pathlib import Path

@dataclass
class Episode:
    path: Path
    num: int

@dataclass
class Season:
    path: Path
    num: int
    episodes: list[Episode]

@dataclass
class Rename:
    old_path: Path
    new_path: Path

    @property
    def needs_rename(self) -> bool:
        return self.new_path != self.old_path
