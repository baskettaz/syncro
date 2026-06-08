import logging
from collections.abc import Generator
from dataclasses import dataclass, field
from pathlib import Path

from syncro.containers.ordered_set import OrderedSet

logger = logging.getLogger(__name__)


BUFSIZE = 1024 * 1024  # 1MB


def verify_files(left: Path, right: Path) -> bool:
    if not (left.is_file() and right.is_file()):
        return False
    return True


def cmp_files_stats(left: Path, right: Path) -> bool:
    "Compare two files and return whether they are identical"

    verify_files(left, right)
    return left.stat() == right.stat()


def cmp_files_as_binaries(left: Path, right: Path, bufsize: int = BUFSIZE) -> bool:
    "Compare two files as binaries and return whether they are identical"

    verify_files(left, right)

    with open(left.absolute(), "rb") as fp1, open(right.absolute(), "rb") as fp2:
        while True:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)

            if b1 != b2:
                return False

            if not b1 and not b2:
                return True


@dataclass
class DirCompare:
    # fmt: off
    left_dir    : Path
    right_dir   : Path
    skip        : list[str] = field(default_factory = list)
    # fmt: on

    def filter(self, root: Path) -> Generator[Path]:
        for item in root.glob("**"):
            if not item.is_file():
                # Note: dirs aren't interesting
                continue

            element = f"{item.relative_to(root)}"
            if self.skip:
                if not any(to_skip in element for to_skip in self.skip):
                    yield item
            else:
                yield item

    @property
    def left(self) -> OrderedSet:
        return OrderedSet(self.filter(self.left_dir))

    @property
    def right(self) -> OrderedSet:
        return OrderedSet(self.filter(self.right_dir))

    @property
    def left_only(self) -> OrderedSet:
        return self.left - self.right

    @property
    def right_only(self) -> OrderedSet:
        return self.right - self.left

    @property
    def common(self) -> OrderedSet:
        return self.left & self.right

    def report(self) -> None:
        if self.left_only:
            logger.info("Only in the left dir:\n%s", "\n".join(self.left_only))
        if self.right_only:
            logger.info("Only in the right dir:\n%s", "\n".join(self.right_only))
        if self.common:
            logger.info("Common files:\n%s", "\n".join(self.right_only))


@dataclass
class DirCompareFull:
    # fmt: off
    from_dir : Path
    to_dir   : Path
    compared : DirCompare = field(init = False, repr = True)
    skip     : list[str]  = field(default_factory = list)
    shallow  : bool       = True

    no_diffs : OrderedSet = field(init = True, repr = True, default_factory=OrderedSet)
    diffs    : OrderedSet = field(init = True, repr = True, default_factory=OrderedSet)
    # fmt: on

    def __post_init__(self) -> None:
        self.compared = DirCompare(self.from_dir, self.to_dir, self.skip)
        self.determine_diffs()

    def make_shallow_compare(self, file: Path, left: Path, right: Path) -> None:
        if cmp_files_stats(left, right):
            self.no_diffs.add(file)
        else:
            self.diffs.add(file)

    def make_full_compare(self, file: Path, left: Path, right: Path) -> None:
        if cmp_files_stats(left, right) and cmp_files_as_binaries(left, right):
            self.no_diffs.add(file)
        else:
            self.diffs.add(file)

    def determine_diffs(self) -> None:
        for file in self.compared.common:
            left = self.from_dir / file
            right = self.to_dir / file

            if self.shallow:
                self.make_shallow_compare(file, left, right)
            else:
                self.make_full_compare(file, left, right)
