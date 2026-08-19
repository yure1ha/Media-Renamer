import shutil
import subprocess
import sys
from pathlib import Path


def macos_hide_extension(file: Path) -> None:
    if sys.platform != "darwin":
        return

    if shutil.which("SetFile") is None:
        print("Warning: 'SetFile' command not found.")
        return

    try:
        subprocess.run(["SetFile", "-a", "E", str(file)], check=True)

    except Exception as e:
        print(f"Warning: Could not hide extension for '{file}': {e}")
