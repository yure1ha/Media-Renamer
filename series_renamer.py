from pathlib import Path

import parsing


class SeriesRenamer:
    def __init__(self, root_dir: Path, series_name: str, dry_run: bool) -> None:
        self.root_dir = root_dir
        self.series_name = series_name
        self.dry_run = dry_run

    def season_dirs(self) -> dict[Path, int]:
        season_dirs = {}

        for item in self.root_dir.iterdir():
            if not item.is_dir():
                continue

            season_num = parsing.extract_season_num(item)

            if season_num is not None:
                season_dirs[item] = season_num

        return season_dirs

    def rename_season_dirs(self) -> None:
        for season_path, season_num in self.season_dirs.items():
            new_season_path = season_path.with_name(f"Season {season_num}")

            if new_season_path != season_path:
                print(f"Renaming: '{season_path}' -> '{new_season_path}'")

                if not self.dry_run:
                    season_path.rename(new_season_path)

    def find_max_episode_num(self) -> int:
        episode_nums = []

        for season_path in self.season_dirs.keys():
            for episode in season_path.iterdir():
                if not episode.is_file():
                    continue

                episode_num = parsing.extract_episode_num(episode)

                if episode_num is not None:
                    episode_nums.append(episode_num)

        return max(episode_nums) if episode_nums else 0


    def rename_episodes(self) -> None:
        max_episode_num = self.find_max_episode_num()

        for season_path, season_num in self.season_dirs.items():
            for episode_path in season_path.iterdir():
                if not episode_path.is_file():
                    continue

                episode_num = parsing.extract_episode_num(episode_path)

                if episode_num is None:
                    continue

                padded_episode_num = self.zero_pad(episode_num, max_episode_num)

                new_episode_name = f"{self.series_name} [S{season_num}E{padded_episode_num}]{episode_path.suffix}"
                new_episode_path = episode_path.with_name(new_episode_name)

                if new_episode_path != episode_path:
                    print(f"Renaming: '{episode_path}' -> '{new_episode_path}'")

                    if not self.dry_run:
                        episode_path.rename(new_episode_path)

    @staticmethod
    def zero_pad(num: int, max_num: int) -> str:
        padding_length = len(str(max_num))
        return str(num).zfill(padding_length)
