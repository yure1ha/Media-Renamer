from functools import cached_property
from itertools import chain
from pathlib import Path

from src import models
from src import parsing


class SeriesScanner:
    SKIPPED_FILENAMES: set[str] = {".DS_Store", "rename_log.json"}

    def __init__(self, root_dir: Path, series_name: str) -> None:
        self.root_dir = root_dir
        self.series_name = series_name
        self.skipped_files: set[Path] = {self.root_dir / name for name in self.SKIPPED_FILENAMES}

    @cached_property
    def max_episode_num(self) -> int:
        episodes = chain(
            (episode.num for episode in self.seasonless_episodes),
            (episode.num for season in self.seasons for episode in season.episodes),
        )

        return max(episodes, default=0)

    @cached_property
    def seasonless_episodes(self) -> list[models.Episode]:
        return self._get_episodes(self.root_dir)

    @cached_property
    def seasons(self) -> list[models.Season]:
        seasons = []

        for item in self.root_dir.iterdir():
            if not item.is_dir():
                continue

            season_num = parsing.extract_season_num(item)
            if season_num is None:
                continue

            seasons.append(models.Season(
                path=item,
                num=season_num,
                episodes=self._get_episodes(item)
            ))

        return seasons

    def _get_episodes(self, season_dir: Path) -> list[models.Episode]:
        episodes = []

        for episode in season_dir.iterdir():
            if episode in self.skipped_files:
                continue

            if not episode.is_file():
                continue

            episode_num = parsing.extract_episode_num(episode)
            if episode_num is None:
                try:
                    episode_num = parsing.extract_unmarked_episode_num(episode, self.series_name)

                except Exception as e:
                    print(
                        f"\n[ERROR] Failed to extract episode number from '{episode}'"
                        f": {e}")
                    continue

            if episode_num is None:
                print(f"\n[WARNING] No episode number found in '{episode}'")
                continue

            episodes.append(models.Episode(
                path=episode,
                num=episode_num)
            )

        return episodes
