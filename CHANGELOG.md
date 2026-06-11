# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
