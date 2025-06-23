import pytest
from pathlib import Path

from jml.utils import files


def test_is_cached(tmp_path):
    file = Path.cwd() / "is_not_cached.txt"
    assert not files.is_cached(file, tmp_path)

    file = tmp_path / "is_not_cached.txt"
    assert not files.is_cached(file, tmp_path)

    file = tmp_path / "is_cached.txt"
    file.write_text("is cached")
    assert files.is_cached(file, tmp_path)

    file = Path.cwd() / "is_cached.txt"
    assert files.is_cached(file, tmp_path)


def test_check_cache(tmp_path):
    cache = tmp_path / "cache"
    cache.mkdir()

    file = tmp_path / "is_not_cached.txt"
    assert not files.check_cache(file, cache)

    file = tmp_path / "is_cached.txt"
    file.write_text("is cached")
    cached_file = files.check_cache(file, cache)
    assert cached_file.samefile(cache / file.name)
    assert files.check_cache(file, cache).samefile(cached_file)
