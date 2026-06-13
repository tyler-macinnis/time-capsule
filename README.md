# Time Capsule

A memory journal for the moments that matter: a photo-rich timeline of any
and all events, an "On This Day" greeting at every launch, and a stats
dashboard.

## Documentation

- [User guide](docs/user-guide.md) — installing, updating, and using every feature
- [Troubleshooting](docs/troubleshooting.md) — data locations, backup/restore, common fixes

## Features

- **Timeline** — memories grouped by year with notes, categories, photos, "time since",
  and edit/delete buttons on every card
- **Gallery** — every photo in one grid, with a full-size viewer
- **Stats** — days of history, memories by category, upcoming anniversaries
- **On This Day** — a surprise greeting when a memory's anniversary is today
- **Photos** — attach any number of pictures to a memory; thumbnails are generated automatically
- **CSV** — export and import memories with proper file dialogs
- **SQLite storage** — all data in a per-user database under `%APPDATA%\TimeCapsule`
- **Installer & updates** — per-user Inno Setup installer (no admin) and a built-in
  update check against GitHub releases

## Installing (users)

Download and run `TimeCapsule-Setup-<version>.exe` from the
[latest release](https://github.com/tyler-macinnis/time-capsule/releases/latest).
See the [user guide](docs/user-guide.md) for details.

## Setup Instructions

1. **Install Python**  
   Ensure Python is installed on your system. You can download it from [python.org](https://www.python.org/).

2. **Set Up a Virtual Environment**  
   Create a virtual environment with the command:

   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment**  
   On Windows, activate the virtual environment with:

   ```bash
   .venv\Scripts\activate
   ```

   On Unix or MacOS, use:

   ```bash
   source .venv/bin/activate
   ```

4. **Update Pip**  
   Upgrade pip to the latest version:

   ```bash
   python -m pip install --upgrade pip
   ```

5. **Install Requirements**  
   Install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. **Run the Application**

   Start the application with:

   ```bash
   python src/main.py
   ```

## Update Dependencies

Dependencies are pinned in [requirements.txt](requirements.txt). Update versions there as needed.

## Build a Windows Executable

To build a Windows executable (and the installer, if Inno Setup is present), run the
following command from within the virtual environment:

```bash
python build_release.py
```

The portable executable is written to `dist/Time Capsule.exe`. If
[Inno Setup 6](https://jrsoftware.org/isinfo.php) is installed, the installer is
also compiled to `dist/TimeCapsule-Setup-<version>.exe` from
[installer/timecapsule.iss](installer/timecapsule.iss); otherwise that step is
skipped with a notice.

App data (the SQLite database and the `photos/` folder) lives in
`%APPDATA%\TimeCapsule`, regardless of where the executable runs from.

## Publish a Release

Releases are fully automated by [.github/workflows/release.yml](.github/workflows/release.yml):

1. Bump `VERSION` in [src/timecapsule/\_\_init\_\_.py](src/timecapsule/__init__.py).
2. Add a matching `## [x.y.z] - YYYY-MM-DD` entry to [CHANGELOG.md](CHANGELOG.md).
3. Either push a tag or trigger the workflow manually:

   ```bash
   git tag v3.0.0
   git push origin v3.0.0
   ```

   Or run the **Release** workflow from the GitHub Actions tab and enter the version.

The workflow verifies the version matches the app, runs the smoke tests, builds the
executable and installer, extracts the release notes from the changelog, and publishes
a GitHub Release with the installer and portable `.exe` attached. Every push to `main`
is also smoke-tested and built by [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Attribution

[Dose icons created by Pixel perfect - Flaticon](https://www.flaticon.com/free-icons/dose "dose icons")
