from src.cli import parse
from src.series_renamer import SeriesRenamer


def main() -> None:
    args = parse()
    renamer = SeriesRenamer(
        root_dir=args.root_dir,
        series_name=args.series_name,
        undo_rename=args.undo_rename,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    renamer.run()


if __name__ == "__main__":
    main()
