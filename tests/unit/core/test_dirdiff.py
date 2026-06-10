from collections.abc import Generator
from pathlib import Path
from shutil import copytree

import pytest

from syncro.containers.ordered_set import OrderedSet
from syncro.core.dirdiff import (
    DirCompare,
    DirCompareFull,
    cmp_files_as_binaries,
    cmp_files_stats,
    verify_files,
)


@pytest.fixture(scope="function")
def first_file(tmp_path) -> Generator[Path]:
    path = tmp_path / "first.txt"
    path.write_text("Hello, World!")
    yield path


@pytest.fixture(scope="function")
def second_file(tmp_path) -> Generator[Path]:
    path = tmp_path / "second.txt"
    path.write_text("Hello, World!")
    yield path


@pytest.fixture(scope="function")
def first_dir(tmp_path) -> Generator[Path]:
    a = tmp_path / "a"
    a.mkdir(exist_ok=True)
    one = a / "one.py"
    one.write_text("import sys")
    two = a / "hello.csv"
    two.write_text("1,2,3,4")
    three = a / "text.txt"
    three.write_text("Hello text")
    yield tmp_path


@pytest.fixture(scope="function")
def second_dir(first_dir) -> Generator[Path]:
    path = first_dir.parent / "b"

    copytree(first_dir, path, dirs_exist_ok=True)

    a = path / "to_be_skipped"
    a.mkdir(exist_ok=True)
    one = a / "two.py"
    one.write_text("import sys")
    two = a / "hello2.csv"
    two.write_text("1,2,3,4")
    three = a / "text2.txt"
    three.write_text("Hello text2")
    yield path


def test_verify_files_all_files(first_file, second_file):
    assert verify_files(first_file, second_file)


def test_verify_files_left_dir(first_file, second_file):
    assert not verify_files(first_file.parent, second_file)


def test_verify_files_right_dir(first_file, second_file):
    assert not verify_files(first_file, second_file.parent)


def test_cmp_files_stats_identical(first_file):
    assert cmp_files_stats(first_file, first_file)


def test_cmp_files_stats_not_identical(first_file, second_file):
    assert not cmp_files_stats(first_file, second_file)


def test_cmp_files_as_binaries_identical(first_file, second_file):
    assert cmp_files_as_binaries(first_file, second_file)


def test_cmp_files_as_binaries_not_identical(first_file, second_file):
    second_file.write_text("Goodbye, World!")
    assert not cmp_files_as_binaries(first_file, second_file)


def test_dir_compare_with_diff_dirs_all(first_dir, second_dir):
    dc = DirCompare(first_dir, second_dir)
    assert len(dc.left) == 3
    assert dc.left == OrderedSet([r"a\hello.csv", r"a\one.py", r"a\text.txt"])
    assert len(dc.right) == 6
    assert dc.right == OrderedSet(
        [
            r"to_be_skipped\hello2.csv",
            r"to_be_skipped\text2.txt",
            r"to_be_skipped\two.py",
            r"a\hello.csv",
            r"a\one.py",
            r"a\text.txt",
        ]
    )
    assert len(dc.common) == 3
    assert dc.common == OrderedSet([r"a\hello.csv", r"a\one.py", r"a\text.txt"])

    assert len(dc.left_only) == 0
    assert len(dc.right_only) == 3


def test_dir_compare_with_diff_dirs_skip_elements(first_dir, second_dir):
    dc = DirCompare(first_dir, second_dir, skip=["to_be_skipped"])
    assert len(dc.left) == 3
    assert dc.left == OrderedSet([r"a\hello.csv", r"a\one.py", r"a\text.txt"])
    assert len(dc.right) == 3
    assert dc.right == OrderedSet([r"a\hello.csv", r"a\one.py", r"a\text.txt"])
    assert len(dc.common) == 3
    assert dc.common == OrderedSet([r"a\hello.csv", r"a\one.py", r"a\text.txt"])

    assert len(dc.left_only) == 0
    assert len(dc.right_only) == 0


def test_dir_compare_full_all_shallow(first_dir, second_dir):
    dcf = DirCompareFull(first_dir, second_dir, shallow=True)
    assert len(dcf.left_only) == 0
    assert len(dcf.right_only) == 3
    assert len(dcf.diffs) == 3
    assert len(dcf.no_diffs) == 0
