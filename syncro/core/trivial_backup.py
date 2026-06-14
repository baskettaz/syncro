from pathlib import Path
from datetime import datetime

datetime.now()

BACKUP_NAME = "__backup__"
MAXBACKUPS = 5




def create_backup(folder: Path) -> None:
    backup = folder / BACKUP_NAME
    backup.mkdir(exist_ok=True)

    timed_backup = backup / datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timed_backup.mkdir(exist_ok=True)


def remove_exceeded_backups(folder: Path, max_backups: int = MAXBACKUPS) -> None:
    backup = folder / BACKUP_NAME

    if len([element for element in backup.iterdir() if element.is_dir()]) <= MAXBACKUPS:
        return

    backups = sorted(backup.iterdir(), key=lambda x: x.name, reverse=True)

    for old_backup in backups[MAXBACKUPS:]:
        if old_backup.is_dir():
            for item in old_backup.iterdir():
                if item.is_file():
                    item.unlink()
                else:
                    remove_exceeded_backups(item)
            old_backup.rmdir()

