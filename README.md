# Time Capsule

A memory journal for the moments that matter: a photo-rich timeline of your story,
an "On This Day" greeting at every launch, and a love-stats dashboard.

## Features

- **Timeline** — memories grouped by year with notes, categories, photos, and "time since"
- **Gallery** — every photo in one grid, with a full-size viewer
- **Stats** — days together, milestones, memories by category, upcoming anniversaries
- **On This Day** — a surprise greeting when a memory's anniversary is today
- **Photos** — attach any number of pictures to a memory; thumbnails are generated automatically
- **CSV** — export and import memories with proper file dialogs
- **Migration** — v1 `important_dates.json` and `categories.json` are converted automatically
  on first launch (originals kept as `.bak`)

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

To build a Windows executable, run the following command from within the virtual environment:

```bash
python build_release.py
```

The executable is written to `dist/Time Capsule.exe`. Data files (`memories.json`,
`settings.json`, and the `photos/` folder) are created next to the executable.

## Publish a Release

Releases are fully automated by [.github/workflows/release.yml](.github/workflows/release.yml):

1. Bump `VERSION` in [src/timecapsule/\_\_init\_\_.py](src/timecapsule/__init__.py).
2. Add a matching `## [x.y.z] - YYYY-MM-DD` entry to [CHANGELOG.md](CHANGELOG.md).
3. Either push a tag or trigger the workflow manually:

   ```bash
   git tag v2.0.1
   git push origin v2.0.1
   ```

   Or run the **Release** workflow from the GitHub Actions tab and enter the version.

The workflow verifies the version matches the app, runs the smoke tests, builds the
executable, extracts the release notes from the changelog, and publishes a GitHub
Release with the `.exe` attached. Every push to `main` is also smoke-tested and built
by [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Attribution

[Dose icons created by Pixel perfect - Flaticon](https://www.flaticon.com/free-icons/dose "dose icons")
