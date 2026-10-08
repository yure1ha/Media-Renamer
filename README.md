# Series Renamer

A CLI tool to batch rename local TV series into the format `[Series Name][S#]` for seasons and `[Series Name][S#][E#]`
for episodes

## Usage

```bash
cd /path/to/project
python3 main.py <root_dir> <series_name> [-d] [-u] [-v]
```

- Dry Run: `[--dry-run] [-d]` Simulate renaming without making changes
- Undo Rename: `[--undo] [-u]` Undo previous rename
- Verbose: `[--verbose] [-v]` Enable verbose output

### Supported Formats

| Style | Examples | Extracts |
|---|---|---|
| Season + Episode | `S01E05`, `s1e5`, `S01.E05`, `S01 - E05` | Season 1, Episode 5 |
| Episode Keyword | `Episode 5`, `Ep05`, `E5` | Episode 5 |
| Season Keyword | `Season 1`, `S01` | Season 1 |
| Unmarked | `Series Name - 05` | Episode 5 |

## Architecture

To start, the scanner (`src/series_scanner.py`) reads the provided directory and uses the parsing module's
(`src/parsing.py`) regex patterns to extract the season and episode numbers. From these it builds and caches `Episode`
and `Season` models (`src/models.py`). Then, the renamer (`src/series_renamer.py`) builds a list of
`Rename` objects from the scanner output before executing the rename operation, logging each successful one so that it
can be undone later. Skipped items are printed at the end of the operation.
