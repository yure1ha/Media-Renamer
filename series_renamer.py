from pathlib import Path

import models
import rename_log
import series_scanner


class SeriesRenamer:
    EPISODE_NAME_FORMAT = "{series_name} [S{season_num}E{episode_num}]{suffix}"
    SEASON_NAME_FORMAT  = "{series_name} [S{season_num}]"

    def __init__(self, series_name: str, root_dir: Path, dry_run: bool) -> None:
        self.series_name = series_name
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.scanner = series_scanner.SeriesScanner(root_dir=self.root_dir)
        self.rename_log = rename_log.RenameLog(root_dir=self.root_dir, dry_run=self.dry_run)

    def plan_episode_renames(self) -> list[models.Rename]:
        renames = []

        for season in self.scanner.seasons:
            for episode in season.episodes:
                new_name = self.EPISODE_NAME_FORMAT.format(
                    series_name=self.series_name,
                    season_num=season.num,
                    episode_num=self._zero_pad(episode.num, self.scanner.max_episode_num),
                    suffix=episode.path.suffix
                )

                renames.append(models.Rename(
                    old_path=episode.path,
                    new_path=episode.path.with_name(new_name)
                ))

        return renames

    def plan_season_renames(self) -> list[models.Rename]:
        renames = []

        for season in self.scanner.seasons:
            new_name = self.SEASON_NAME_FORMAT.format(
                series_name=self.series_name,
                season_num=season.num
            )

            renames.append(models.Rename(
                old_path=season.path,
                new_path=season.path.with_name(new_name)
            ))

        return renames

    def execute_renames(self, renames: list[models.Rename]) -> list[str]:
        errors = []

        for rename in renames:
            if not rename.needs_rename:
                print(f"[SKIP] No rename needed at {rename.old_path}")
                errors.append(rename.old_path.as_posix())
                continue

            print(f"[RENAME] '{rename.old_path}' -> '{rename.new_path}'")

            if not self.dry_run:
                try:
                    rename.old_path.rename(rename.new_path)
                    self.rename_log.record(models.Rename(
                        rename.old_path,
                        rename.new_path)
                    )

                except Exception as e:
                    print(f"[ERROR] Failed to rename '{rename.old_path}': {e}")
                    errors.append(rename.old_path.as_posix())

        if not self.dry_run:
            self.rename_log.save()

        return errors

    def plan_undo_renames(self) -> list[models.Rename]:
        entries = self.rename_log.load()
        undo_renames = []

        for entry in entries:
            if not entry.old_path.exists():
                print(f"[SKIP] Destination '{entry.old_path} already exists")
                continue

            undo_renames.append(models.Rename(entry.old_path, entry.new_path))

        return undo_renames

    def execute_undo_renames(self, undo_renames: list[models.Rename]) -> list[str]:
        errors = []

        for undo in reversed(undo_renames):
            if not undo.needs_rename:
                print(f"[SKIP] No rename needed at {undo.old_path}")
                errors.append(undo.new_path.as_posix())
                continue

            print(f"[UNDO] Reverting '{undo.old_path}' -> '{undo.new_path}'")

            if not self.dry_run:
                try:
                    undo.new_path.rename(undo.old_path)

                except Exception as e:
                    print(f"[ERROR] Failed to revert '{undo.new_path}': {e}")
                    errors.append(undo.new_path.as_posix())

        return errors

    @staticmethod
    def _zero_pad(num: int, max_num: int) -> str:
        return str(num).zfill(len(str(max_num)))
