# Time Capsule — Troubleshooting

Solutions for common problems, plus how to back up and recover your data.

## Quick facts

| What | Where |
| --- | --- |
| Database (memories, categories, settings) | `%APPDATA%\TimeCapsule\timecapsule.db` |
| Photos | `%APPDATA%\TimeCapsule\photos\` |
| Thumbnails | `%APPDATA%\TimeCapsule\photos\thumbs\` |
| Installed app (default) | `%LOCALAPPDATA%\Programs\Time Capsule\` |

Paste any of these paths into the File Explorer address bar to open them.

## The timeline is empty after upgrading

Versions before 3.0.0 stored data in JSON files (`memories.json`,
`important_dates.json`, `settings.json`) next to the executable. Version
3.0.0 uses a new SQLite database in `%APPDATA%\TimeCapsule` and **does not
migrate old data**.

Your old data is not lost — it is still next to the old executable:

1. If you exported a CSV with the old version, use
   **⋮ menu → Import from CSV** to bring memories back in.
2. Otherwise, open the old `memories.json` in a text editor — every memory's
   title, date, notes, and category are readable there — and re-enter them.

## Memories disappeared (no upgrade involved)

1. Confirm the app is reading the folder you expect: the database is always
   at `%APPDATA%\TimeCapsule\timecapsule.db` for the current Windows user.
   If your partner uses a different Windows account, each account has its
   own data.
2. Check the search box — an active search filters the timeline. Clear it.
3. If the database file was deleted or replaced, restore it from a backup
   (see below).

## Backing up

Copy the whole `%APPDATA%\TimeCapsule` folder somewhere safe (cloud drive,
USB stick). That single folder contains the database and all photos.

For an extra plain-text safety net, use **⋮ menu → Export to CSV**
periodically. CSV files do not include photos.

## Restoring a backup

1. Close Time Capsule.
2. Copy your backed-up `TimeCapsule` folder back to `%APPDATA%`, replacing
   the existing one.
3. Start the app.

> If you see files named `timecapsule.db-wal` or `timecapsule.db-shm`, they
> belong to the database. Always back up and restore all `timecapsule.db*`
> files together.

## Photos show as blank tiles

Thumbnails live in `photos\thumbs\`. If a thumbnail is missing, its tile is
skipped in the gallery and the timeline shows an accurate "+N" count. To
regenerate a missing thumbnail, open the memory, remove the photo, and
re-add it from the full-size file in `photos\`.

## Update check problems

- **"Could not reach GitHub to check for updates"** — you are offline or a
  firewall blocks `api.github.com`. The app works fully offline; check again
  later via **⋮ menu → Check for updates**.
- The automatic startup check never blocks the app and stays silent when the
  network is unavailable.
- To disable the startup check, close the app and run the following, then
  restart:

  ```powershell
  $db = "$env:APPDATA\TimeCapsule\timecapsule.db"
  python -c "import sqlite3; c = sqlite3.connect(r'$db'); c.execute(\"INSERT INTO settings (key, value) VALUES ('update_check', 'off') ON CONFLICT(key) DO UPDATE SET value = 'off'\"); c.commit()"
  ```

## The app will not start

1. Reinstall from the
   [latest release](https://github.com/tyler-macinnis/time-capsule/releases/latest) —
   installing over the top is safe and never touches your data.
2. If it still fails, rename `%APPDATA%\TimeCapsule` to `TimeCapsule.bak`
   and launch again. If the app now starts, the database was damaged —
   restore from a backup or send the `.bak` folder to the maintainer.

## Reporting a bug

Open an issue at
[github.com/tyler-macinnis/time-capsule/issues](https://github.com/tyler-macinnis/time-capsule/issues)
with what you did, what you expected, and what happened instead.
