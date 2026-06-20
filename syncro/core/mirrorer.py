import logging
import os
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

RunningOnWindows = sys.platform.startswith("win")


def copyinfo(pathFrom: Path, pathTo: Path) -> None:
    try:
        shutil.copystat(pathFrom.absolute(), pathTo.absolute(), follow_symlinks=False)
    except OSError as why:
        logger.critical(why)
        raise


def copylink(pathFrom: Path, pathTo: Path, copystat: bool = True) -> None:
    if pathFrom.is_dir() and RunningOnWindows:
        dirargs = dict(target_is_directory=True)
    else:
        dirargs = dict()

    if os.path.lexists(pathTo.absolute()):
        os.remove(pathTo.absolute())

    linkPath = pathFrom.readlink()
    os.symlink(linkPath.absolute(), pathTo.absolute(), **dirargs)
    if copystat:
        copyinfo(pathFrom, pathTo)


def copyfile():
    pass


def copytree():
    pass
