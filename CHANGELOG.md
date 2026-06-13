# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.2.0] - 2026-06-12

### Added in 3.2.0

- The app version is shown in the window titlebar and next to the app name in
  the app bar.

### Fixed in 3.2.0

- Timeline memory cards render again. A layout bug (stretched rows inside the
  scrolling list) made every card invisible, leaving only the year headers.

### Changed in 3.2.0

- The timeline is redesigned as a vertical timeline: a continuous rail with a
  category-colored dot per memory, accent-tinted year pills, and month
  markers between entries.
- Searching now shows how many memories matched, and a dedicated
  "no matches" state when nothing does.
- The smoke test script is replaced by a full pytest unit test suite
  (`tests/`) covering storage, models, state, date utilities, update checks,
  theming, and headless construction of every view.

## [3.1.0] - 2026-06-12

### Added in 3.1.0

- Edit and delete buttons directly on each timeline card (delete asks for
  confirmation). Editing is still also available by clicking a card.
- "Days of history" stat: days from your earliest memory to today.

### Fixed in 3.1.0

- Memories can be dated anywhere from 1800 to 2100 — birthdays and other
  long-ago events fit on the timeline, in the gallery, in stats, and in
  On This Day.
- Upcoming anniversaries in Stats now show how long ago each event occurred in
  years, months, and days instead of years only.

### Changed in 3.1.0

- Time Capsule now tracks any and all events: the relationship-specific
  "our start date" concept is gone, along with the "Our story" section,
  "Days together" card, and milestone badges in Stats.
- Upgraded the UI framework from Flet 0.28 to Flet 0.85 (the Flet 1.0 line):
  dialogs, file pickers, and the update check now use the new async APIs.
- Slimmed direct dependencies to three: `flet[all]`, `pillow`, and
  `pyinstaller` — all at their latest versions.

### Removed in 3.1.0

- "Set our start date" menu item and the start-date picker; any stored
  start date setting is ignored.
- `python-dateutil` dependency; the "time since" calculation is now pure
  standard library.

## [3.0.0] - 2026-06-12

> **Breaking change**: data is now stored in a SQLite database under
> `%APPDATA%\TimeCapsule`. Data from earlier versions (`memories.json`,
> `important_dates.json`, `settings.json`) is **not** migrated — 3.0.0 starts
> fresh. Re-enter memories manually or bring them over with CSV import.

### Added in 3.0.0

- SQLite storage (`%APPDATA%\TimeCapsule\timecapsule.db`) with WAL journaling,
  foreign-key enforcement, and a versioned schema for future migrations.
- Windows installer built with Inno Setup: per-user install (no admin prompt),
  Start menu and optional desktop shortcuts, clean uninstall that preserves data.
- Update check on startup and a "Check for updates" menu item: compares the
  running version against the latest GitHub release and offers to open the
  download page. Silent on network failure; disable with the `update_check`
  setting.
- `docs/` folder with a user guide and troubleshooting guide.

### Changed in 3.0.0

- App data (database and photos) now lives in `%APPDATA%\TimeCapsule` instead
  of next to the executable.
- Settings moved from `settings.json` into the database.
- Release builds now produce both the installer and a portable `.exe`.
- Timeline photo strip now shows an accurate "+N" count when some thumbnails
  are missing from disk.

### Removed in 3.0.0

- JSON storage (`memories.json`, `settings.json`) and the automatic v1
  migration of `important_dates.json`/`categories.json`.

## [2.0.1] - 2026-06-12

### Fixed in 2.0.1

- Fixed startup error on Windows (`module 'flet' has no attribute 'animation'`) by
  using `ft.Animation` directly, as required by flet 0.28.x.

## [2.0.0] - 2026-06-11

### Added in 2.0.0

- Photo attachments on memories, with automatic thumbnails and a gallery view.
- "On This Day" startup greeting and timeline banner for anniversaries of past memories.
- Love-stats dashboard: days together, milestones, memories by category, upcoming anniversaries.
- Customizable appearance: eight theme presets, custom accent color, and a persisted
  light/dark mode preference.
- Window icon (and multi-size `res/time.ico` used for the executable).
- VS Code `tasks.json` with run, test, build, install, and icon-regeneration tasks.
- Automatic one-way migration of v1 `important_dates.json` / `categories.json`
  (originals backed up as `.bak`).

### Changed in 2.0.0

- Complete UI rewrite from CustomTkinter to [Flet](https://flet.dev) with timeline,
  gallery, and stats views.
- Data now stored in `memories.json` (ISO dates, schema v2) plus `settings.json`.
- CSV export/import now uses file dialogs instead of hard-coded paths; legacy v1
  CSV columns and date formats are still accepted on import.
- Build script now packages with `flet pack`.

### Removed in 2.0.0

- CustomTkinter, tkcalendar, pipdeptree, and pur dependencies.

## [1.1.2] - 2024-08-04

### Fixed in 1.1.2

- Fixed `SCRIPT_DIR` for PyInstaller.

## [1.1.1] - 2024-08-01

### Fixed in 1.1.1

- Added necessary hidden import for tkcalender. See the
  [tkcalendar PyInstaller HOWTO](https://tkcalendar.readthedocs.io/en/stable/howtos.html#pyinstaller)
  for more info.

## [1.1.0] - 2024-07-30

### Added in 1.1.0

- Added support for categories.

### Changed in 1.1.0

- Moved buttons to the left side of the GUI.

## [1.0.2] - 2024-07-28

### Added in 1.0.2

- Improved the way that "time since" is calculated.

## [1.0.1] - 2024-07-28

### Fixed in 1.0.1

- Fixed minimum size for windows.

## [1.0.0] - 2024-07-22

### Added in 1.0.0

- Added initial release.
