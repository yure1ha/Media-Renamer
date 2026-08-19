from pathlib import Path

from src import models
from src.rename_log import RenameLog
from src.series_scanner import SeriesScanner


class SeriesRenamer:
    SEASONED_EPISODE_NAME_FORMAT   = "{series_name} [S{season_num}E{episode_num}]{suffix}"
    SEASONLESS_EPISODE_NAME_FORMAT = "{series_name} [E{episode_num}]{suffix}"
    SEASON_NAME_FORMAT             = "{series_name} [S{season_num}]"

    def __init__(self, root_dir: Path, series_name: str, dry_run: bool, undo_rename: bool) -> None:
        self.root_dir = root_dir
        self.series_name = series_name
        self.dry_run = dry_run
        self.undo_rename = undo_rename
        self.scanner = SeriesScanner(root_dir=self.root_dir, series_name=self.series_name)
        self.rename_log = RenameLog(root_dir=self.root_dir, dry_run=self.dry_run)

    def run(self) -> None:
        skipped = []
        failed = []

        if self.undo_rename:
            undo_renames = self._plan_undo_renames()

            s, f = self._execute_undo_renames(undo_renames)
            skipped.extend(s)
            failed.extend(f)

            return

        seasonless_episode_renames = self._plan_seasonless_episode_renames()
        seasoned_episode_renames = self._plan_seasoned_episode_renames()
        season_renames  = self._plan_season_renames()

        s, f = self._execute_renames(
            seasonless_episode_renames
            + seasoned_episode_renames
            + season_renames
        )
        skipped.extend(s)
        failed.extend(f)

        self._print_errors(skipped, failed)

    def _plan_seasonless_episode_renames(self) -> list[models.Rename]:
        renames = []

        for episode in self.scanner.seasonless_episodes:
            new_name = self.SEASONLESS_EPISODE_NAME_FORMAT.format(
                series_name=self.series_name,
                episode_num=self._zero_pad(
                    episode.num, self.scanner.max_episode_num
                ),
                suffix=episode.path.suffix
            )

            renames.append(models.Rename(
                old_path=episode.path,
                new_path=episode.path.with_name(new_name)
            ))

        return renames

    def _plan_seasoned_episode_renames(self) -> list[models.Rename]:
        renames = []

        for season in self.scanner.seasons:
            for episode in season.episodes:
                new_name = self.SEASONED_EPISODE_NAME_FORMAT.format(
                    series_name=self.series_name,
                    season_num=season.num,
                    episode_num=self._zero_pad(
                        episode.num, self.scanner.max_episode_num
                    ),
                    suffix=episode.path.suffix
                )

                renames.append(models.Rename(
                    old_path=episode.path,
                    new_path=episode.path.with_name(new_name)
                ))

        return renames

    def _plan_season_renames(self) -> list[models.Rename]:
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

    def _plan_undo_renames(self) -> list[models.Rename]:
        entries = self.rename_log.load()
        undo_renames = []

        for entry in entries:
            if entry.old_path.exists():
                print(f"\n[WARNING] Destination '{entry.old_path} already exists")
                continue

            undo_renames.append(models.Rename(entry.old_path, entry.new_path))

        return undo_renames

    def _execute_renames(self, renames: list[models.Rename]) -> tuple[list[str], list[str]]:
        skipped = []
        failed = []

        for rename in renames:
            if not rename.needs_rename:
                print(f"\n[WARNING] No rename needed at '{rename.old_path}'")
                skipped.append(rename.old_path.as_posix())
                continue

            print(f"\n[RENAME] '{rename.old_path}' -> '{rename.new_path}'")

            if not self.dry_run:
                try:
                    rename.old_path.rename(rename.new_path)
                    self.rename_log.record(models.Rename(
                        rename.old_path,
                        rename.new_path)
                    )

                except Exception as e:
                    print(f"\n[ERROR] Failed to rename '{rename.old_path}': {e}")
                    failed.append(rename.old_path.as_posix())

        if not self.dry_run:
            self.rename_log.save()

        return skipped, failed

    def _execute_undo_renames(self, undo_renames: list[models.Rename]) -> tuple[list[str], list[str]]:
        skipped = []
        failed = []

        for undo in reversed(undo_renames):
            if not undo.needs_rename:
                print(f"\n[WARNING] No rename needed at {undo.old_path}")
                skipped.append(undo.new_path.as_posix())
                continue

            print(f"\n[UNDO] Reverting '{undo.new_path}' -> '{undo.old_path}'")

            if not self.dry_run:
                try:
                    undo.new_path.rename(undo.old_path)

                except Exception as e:
                    print(f"\n[ERROR] Failed to revert '{undo.new_path}': {e}")
                    failed.append(undo.new_path.as_posix())

        return skipped, failed

    @staticmethod
    def _print_errors(skipped: list, failed: list) -> None:
        if skipped:
            count = len(skipped)
            noun = "rename" if count == 1 else "renames"

            print(f"\nCompleted with {count} {noun} skipped")

            for path in skipped:
                print(f"\n  - {path}")

        if failed:
            count = len(failed)
            noun = "rename" if count == 1 else "renames"

            print(f"\nCompleted with {count} {noun} failed")

            for path in failed:
                print(f"\n  - {path}")

    @staticmethod
    def _zero_pad(num: int, max_num: int) -> str:
        return str(num).zfill(len(str(max_num)))
