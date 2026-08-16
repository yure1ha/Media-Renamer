from pathlib import Path

import models
import series_scanner


class SeriesRenamer:
    def __init__(self, root_dir: Path, series_name: str, dry_run: bool) -> None:
        self.root_dir = root_dir
        self.series_name = series_name
        self.dry_run = dry_run
        self.scanner = series_scanner.SeriesScanner(root_dir=self.root_dir)

    EPISODE_NAME_FORMAT = "{series_name} [S{season_num}E{episode_num}]{suffix}"
    SEASON_NAME_FORMAT  = "{series_name} [S{season_num}]"

    def run(self) -> None:
        self._execute([*self._plan_episode_renames(), *self._plan_season_renames()])

    def _plan_episode_renames(self) -> list[models.Rename]:
        renames = []

        for season in self.scanner.seasons:
            for episode in season.episodes:
                new_name = self.EPISODE_NAME_FORMAT.format(
                    series_name=self.series_name,
                    season_num=season.num,
                    episode_num=self.zero_pad(episode.num, self.scanner.max_episode_num),
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

    def _execute(self, renames: list[models.Rename]) -> None:
        for rename in renames:
            if not rename.needs_rename:
                continue

            print(f"Renaming '{rename.old_path}' -> '{rename.new_path}'")

            if self.dry_run:
                continue

            rename.old_path.rename(rename.new_path)

    @staticmethod
    def zero_pad(num: int, max_num: int) -> str:
        return str(num).zfill(len(str(max_num)))
