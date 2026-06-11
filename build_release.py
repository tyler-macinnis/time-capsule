"""Build a single-file Windows executable with `flet pack` (PyInstaller)."""

import subprocess
import sys

subprocess.run(
    [
        sys.executable,
        "-m",
        "flet.cli",
        "pack",
        "src/main.py",
        "--name",
        "Time Capsule",
        "--icon",
        "res/time.ico",
        "--add-data",
        "res;res",
        "--product-name",
        "Time Capsule",
    ],
    check=True,
)
