from functools import cached_property
from pathlib import Path

from src import models
from src import parsing


class SeriesScanner:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir

    @cached_property
    def max_episode_num(self) -> int:
        return max((episode.num for season in self.seasons for episode in season.episodes), default=0)

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

    @staticmethod
    def _get_episodes(season_dir: Path) -> list[models.Episode]:
        episodes = []

        for episode in season_dir.iterdir():
            if not episode.is_file():
                continue

            episode_num = parsing.extract_episode_num(episode)
            if episode_num is None:
                continue

            episodes.append(models.Episode(
                path=episode,
                num=episode_num)
            )

        return episodes
