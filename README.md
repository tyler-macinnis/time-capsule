# Time Capsule

A memory journal for the moments that matter: a photo-rich timeline of any
and all events, an "On This Day" greeting at every launch, and a stats
dashboard.

## Documentation

- [User guide](docs/user-guide.md) — installing, updating, and using every feature
- [Troubleshooting](docs/troubleshooting.md) — data locations, backup/restore, common fixes

## Features

- **Timeline** — memories grouped by year with notes, categories, photos, "time since",
  and edit/delete buttons on every card; memories can be dated anywhere — past or future
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

Releases are fully automated by [.github/workflows/release.yml](.github/workflows/release.yml).
The workflow refuses to run unless the tag, the app version, and the changelog all
agree, so follow these steps in order (replace `x.y.z` with the new version):

1. Bump `VERSION` in [src/timecapsule/\_\_init\_\_.py](src/timecapsule/__init__.py)
   (e.g. `VERSION = "x.y.z"`).
2. Move the notes for the release from `## [Unreleased]` into a matching
   `## [x.y.z] - YYYY-MM-DD` entry in [CHANGELOG.md](CHANGELOG.md). The workflow
   extracts this entry verbatim as the GitHub release notes.
3. Commit and push those changes to `main`, then confirm CI is green.
4. Tag and push:

   ```bash
   git tag vx.y.z
   git push origin vx.y.z
   ```

   Alternatively, run the **Release** workflow manually from the GitHub Actions
   tab and enter the version (e.g. `x.y.z`); the workflow creates and pushes the
   tag for you.

The workflow then:

- verifies the version is `x.y.z` and matches `VERSION` in the app,
- fails if there is no matching `CHANGELOG.md` entry,
- runs the unit test suite (`python -m pytest`),
- builds the portable executable and the Inno Setup installer, and
- publishes a GitHub Release with `TimeCapsule-Setup-<version>.exe` and
  `Time.Capsule.<version>.portable.exe` attached.

If any check fails, fix the version or changelog, push, and re-run the workflow
(or delete and re-push the tag). Every push to `main` is also tested and
built by [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Attribution

[Dose icons created by Pixel perfect - Flaticon](https://www.flaticon.com/free-icons/dose "dose icons")
