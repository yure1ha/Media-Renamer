from src import cli
from src.series_renamer import SeriesRenamer


def main() -> None:
    root_dir = None
    name = None

    while True:
        if not root_dir:
            root_dir = cli.get_root_dir()

        if not name:
            name = cli.get_series_name()

        dry_run = cli.is_dry_run()
        undo_rename = cli.is_undo_rename()

        renamer = SeriesRenamer(
            root_dir=root_dir,
            series_name=name,
            dry_run=dry_run,
            undo_rename=undo_rename
        )

        renamer.run()

        run_again = cli.is_run_again()
        if not run_again:
            print("\nExiting...")
            print("\nProcess Complete\n")
            break

        use_same_dir = cli.is_same_dir()
        if not use_same_dir:
            root_dir = None
            name = None


if __name__ == "__main__":
    main()
