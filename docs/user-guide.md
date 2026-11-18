# Time Capsule — User Guide

Time Capsule is a memory journal for the moments that matter: a photo-rich
timeline of any and all events — birthdays, anniversaries, trips, firsts —
with an "On This Day" greeting at every launch and a stats dashboard.

## Installation

1. Download `TimeCapsule-Setup-<version>.exe` from the
   [latest release](https://github.com/tyler-macinnis/time-capsule/releases/latest).
2. Run the installer. It installs just for your user account — no administrator
   prompt — and adds a Start menu shortcut (desktop shortcut optional).
3. Launch **Time Capsule** from the Start menu.

A portable `Time.Capsule.<version>.portable.exe` is also attached to each
release if you prefer to run without installing.

### Updating

Time Capsule checks GitHub for a newer release at startup and offers to open
the download page when one is available. You can also check manually via
**⋮ menu → Check for updates**. Installing a new version over the old one
keeps all of your data.

### Uninstalling

Uninstall from Windows **Settings → Apps**. Your memories and photos are
never deleted by the uninstaller (see [Where your data lives](#where-your-data-lives)).

## The three views

Switch views with the navigation rail on the left.

- **Timeline** — every memory grouped by year, newest first. Each card shows
  the title, date, "time since", notes, photo thumbnails, and category,
  plus edit and delete buttons. Click a card to edit it.
- **Gallery** — every photo across all memories in one grid. Click a photo
  for a full-size viewer with a shortcut to its memory.
- **Stats** — days of history, memories by category, and the next five
  upcoming anniversaries.

## Working with memories

### Adding a memory

1. Click the **+** button in the bottom-right corner.
2. Give it a title (required) and pick a date — anything from 1800 to 2100
   works, so birthdays and long-ago events fit right in.
3. Optionally add notes, a category, and photos.
4. Click **Save**.

Photos are copied into the app's data folder, so the originals can be moved
or deleted afterwards without affecting Time Capsule.

### Editing and deleting

Use the pencil or trash buttons on any timeline card, or click the card
itself (or the **Open memory** button in the photo viewer) to open it.
Change anything and **Save**, or click **Delete** to remove the memory along
with its photos. Deleting always asks for confirmation.

### Searching

Type in the search box in the title bar. The timeline filters live across
titles, notes, and categories.

## Categories

Open **⋮ menu → Manage categories** to add or remove categories, each with
its own color. The color tints the memory card accent, the category chip,
and the stats chart. Deleting a category keeps its memories — they just
become uncategorized.

## On This Day

When a memory's anniversary lands on today's date, Time Capsule greets you
with it at launch and pins an "On this day" banner to the top of the
timeline.

## Stats

The Stats view shows:

- a **Days of history** counter (from your earliest memory to today),
- total memories and photos,
- memories by category,
- the next five upcoming anniversaries with how long ago each event occurred.

## Backup and restore

- **⋮ menu → Back up everything** saves one `.zip` file containing all your
  memories, categories, settings, and photos. Keep it somewhere safe (cloud
  drive, USB stick).
- **⋮ menu → Restore from backup** loads such a file. It **replaces
  everything** currently in the app, so you are asked to confirm first. Use
  it to move to a new computer or recover after a problem.

The zip is deliberately simple, so your memories stay readable without the
app: a `photos` folder with the original images, and `backup.json`, a plain
text file listing every memory (title, date, notes, category, photo file
names) along with your categories and settings.

CSV export and import were removed in favor of this format.

## Appearance

**⋮ menu → Appearance** offers eight theme presets and a custom hex accent
color, plus a light/dark mode switch. The sun/moon button in the title bar
toggles the mode quickly. All choices are remembered.

## Where your data lives

Everything is stored per-user under:

```text
%APPDATA%\TimeCapsule\
├── timecapsule.db   ← memories, categories, settings (SQLite)
└── photos\          ← full-size photos
    └── thumbs\      ← generated thumbnails
```

To back up, copy the whole `TimeCapsule` folder. To restore, copy it back
before launching the app. See the
[troubleshooting guide](troubleshooting.md) for recovery details.

> **Note for upgraders**: versions before 3.0.0 stored data in JSON files next
> to the executable. 3.0.0 starts fresh and does not read those files —
> re-enter your memories by hand.
