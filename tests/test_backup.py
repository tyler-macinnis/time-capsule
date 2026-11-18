"""Full backup (JSON + photos) and restore."""

from __future__ import annotations

import json
import os
import zipfile

import pytest

from timecapsule import storage
from timecapsule.storage import BackupError, Database


def test_backup_round_trip_replaces_everything(db, make_memory, sample_png, tmp_path):
    kept = storage.import_photo(sample_png)
    db.upsert_memory(make_memory(title="Kept", category="Us", photos=[kept]))
    db.delete_category("Adventures")
    db.set_setting("accent", "#0288D1")
    backup = str(tmp_path / "backup.zip")
    storage.create_backup(backup)
    with zipfile.ZipFile(backup) as zf:  # readable without the app
        assert json.loads(zf.read("backup.json"))["memories"][0]["title"] == "Kept"

    # Diverge from the backup: new memory, new photo, old photo deleted.
    later = storage.import_photo(sample_png)
    db.upsert_memory(make_memory(title="Later", photos=[later]))
    storage.delete_photo(kept)
    db.close()

    storage.restore_backup(backup)

    restored = Database()
    try:
        (memory,) = restored.list_memories()
        assert (memory.title, memory.category, memory.photos) == ("Kept", "Us", [kept])
        assert "Adventures" not in restored.categories()  # defaults not reseeded
        assert "Us" in restored.categories()
        assert restored.get_settings() == {"accent": "#0288D1"}
    finally:
        restored.close()
    assert os.path.exists(storage.photo_path(kept))
    assert os.path.exists(storage.thumb_path(kept))
    assert not os.path.exists(storage.photo_path(later))
    assert not os.path.exists(os.path.join(storage.APP_DIR, "restore.tmp"))


@pytest.mark.parametrize("kind", ["not_a_zip", "no_json", "junk_json", "bad_date", "future_format"])
def test_restore_rejects_bad_files_and_keeps_data(db, make_memory, tmp_path, kind):
    db.upsert_memory(make_memory(title="Precious"))
    bad = tmp_path / "bad.zip"
    if kind == "not_a_zip":
        bad.write_text("hello")
    else:
        with zipfile.ZipFile(bad, "w") as zf:
            zf.writestr("readme.txt", "nope")
            good = {"format": 1, "memories": [], "categories": {}, "settings": {}}
            bad_memory = {"id": "x", "title": "T", "day": "someday"}
            if kind == "junk_json":
                zf.writestr(storage.BACKUP_JSON, "{not json")
            elif kind == "bad_date":
                zf.writestr(
                    storage.BACKUP_JSON, json.dumps({**good, "memories": [bad_memory]})
                )
            elif kind == "future_format":
                zf.writestr(storage.BACKUP_JSON, json.dumps({**good, "format": 99}))
    db.close()

    with pytest.raises(BackupError):
        storage.restore_backup(str(bad))

    reopened = Database()
    try:
        assert [m.title for m in reopened.list_memories()] == ["Precious"]
    finally:
        reopened.close()


def test_restore_ignores_files_outside_the_backup_layout(db, tmp_path):
    backup = str(tmp_path / "backup.zip")
    storage.create_backup(backup)
    with zipfile.ZipFile(backup, "a") as zf:
        zf.writestr("../escaped.txt", "x")
        zf.writestr("extra/thing.txt", "x")
    db.close()

    storage.restore_backup(backup)

    assert not os.path.exists(os.path.join(os.path.dirname(storage.APP_DIR), "escaped.txt"))
    assert os.listdir(storage.APP_DIR) == [storage.DB_NAME]
