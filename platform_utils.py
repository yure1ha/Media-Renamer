import shutil
import subprocess
import sys
from pathlib import Path


def macos_hide_extension(filepath: Path) -> None:
    if sys.platform != "darwin":
        return

    if shutil.which("SetFile") is None:
        print("Warning: 'SetFile' command not found. Cannot hide extension on macOS.")
        return

    try:
        subprocess.run(["SetFile", "-a", "E", str(filepath)], check=True)

    except Exception as error:
        print(f"Warning: Could not hide extension for '{filepath}': {error}")
