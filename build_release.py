"""Build the Windows executable (flet pack) and, if available, the installer."""

import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def app_version() -> str:
    init_py = os.path.join(ROOT, "src", "timecapsule", "__init__.py")
    with open(init_py, "r", encoding="utf-8") as fh:
        match = re.search(r'VERSION = "(.+)"', fh.read())
    if not match:
        raise SystemExit("Could not find VERSION in src/timecapsule/__init__.py")
    return match.group(1)


def build_exe() -> None:
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
        cwd=ROOT,
    )


def find_iscc() -> str | None:
    """Locate the Inno Setup compiler."""
    found = shutil.which("ISCC")
    if found:
        return found
    for env in ("ProgramFiles(x86)", "ProgramFiles"):
        base = os.environ.get(env)
        if base:
            candidate = os.path.join(base, "Inno Setup 6", "ISCC.exe")
            if os.path.exists(candidate):
                return candidate
    return None


def build_installer(version: str) -> None:
    iscc = find_iscc()
    if not iscc:
        print("Inno Setup (ISCC.exe) not found — skipping installer build.")
        print("Install it from https://jrsoftware.org/isinfo.php to build the setup.")
        return
    subprocess.run(
        [iscc, f"/DAppVersion={version}", os.path.join("installer", "timecapsule.iss")],
        check=True,
        cwd=ROOT,
    )
    print(f"Installer written to dist/TimeCapsule-Setup-{version}.exe")


if __name__ == "__main__":
    version = app_version()
    build_exe()
    build_installer(version)
