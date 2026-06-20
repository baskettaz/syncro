import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

BACKUP_FOLDER_NAME = "__backup__"
BACKUP_FILE_NAME = "__changes__.txt"
MAXBACKUPS = 5


def create_backup(folder: Path) -> None:
    backup = folder / BACKUP_FOLDER_NAME
    backup.mkdir(exist_ok=True)

    timed_backup = backup / datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timed_backup.mkdir(exist_ok=True)


def remove_exceeded_backups(folder: Path, max_backups: int = MAXBACKUPS) -> None:
    backup = folder / BACKUP_FOLDER_NAME

    if len([element for element in backup.iterdir() if element.is_dir()]) <= MAXBACKUPS:
        return

    backups = sorted(backup.iterdir(), key=lambda x: x.name, reverse=True)

    for old_backup in backups[max_backups:]:
        old_backup.rmdir()
