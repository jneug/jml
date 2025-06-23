import hashlib
import io
import logging
import shutil
import tempfile
import typing as t
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

logger = logging.getLogger("jml")

# module global flag for dry run mode
_DRY_RUN = False


def enable_dry_run() -> None:
    """
    Enables dry run mode for file operations.
    """
    globals()["_DRY_RUN"] = True


def is_cached(path: Path, cache: Path) -> Path | None:
    """Checks if the given file exists within the cache dir and
    returns either the cached Path or None.

    Args:
        path (Path): Path to the file to check.
        cache (Path): Path to the cache directory.

    Returns:
        Path or None: Either the path of the cached file or `None`.
    """
    for file in cache.glob(path.name):
        if file.is_file():
            return file
    return None


def check_cache(path: Path, cache: Path | None) -> Path | None:
    """
    Returns the path to the cached version of path. If path is not cached,
    it is copied to the cache first.

    If `cache` is `None`, the function will always return `None`.

    Args:
        path (Path): Path to the file to cache.
        cache (Path or None): Path to the cache directory or `None`.

    Returns:
        Path or None: The cached version of the file.
    """
    if not cache:
        return None

    if cached := is_cached(path, cache):
        return cached
    else:
        # copy path to cache
        make_dirs(cache)
        if path.is_dir():
            shutil.copytree(path, cache / path.name)
        elif path.is_file():
            shutil.copy(path, cache)
        else:
            return None
        return cache / path.name


def clear_cache(path: Path, cache: Path) -> None:
    """
    Removes `path` from the `cache` directory.

    Args:
        path (Path): Path to the to the file to remove from the cache.
        cache (Path): Path to the cache directory.
    """
    if cached := is_cached(path, cache):
        if path.is_dir():
            shutil.rmtree(cached)
        else:
            cached.unlink()


def make_dirs(path: Path, exist_ok: bool = True) -> None:
    """
    Creates the directory `path` and all parents.

    By default, `exist_ok` is set to `True` but may be disabled.

    Args:
        path (Path): Path to create.
        exists_ok (bool): Passed to `Path.mkdir()`.
    """
    if _DRY_RUN:
        return
    path.mkdir(exist_ok=exist_ok, parents=True)


def copy_path(source: Path, dest: Path, cache: Path | None = None) -> None:
    """
    Copies the file or directory at `source` to `dest`. Directories are copied
    recursive. If `dest` does not exist, the parent folder is created.

    If `source` is a file and `dest` a directory, `source` is copied to `dest`.
    If `dest` is a file, `source` is copied to that file. If `dest` is an
    existing file, the operation fails.

    If `source` is a directory and `dest`, too, `source` is copied into `dest`. If `dest` is an existing file, the operation fails.

    If `cache` is a directory path, it is checked first for a cached version of
    `source` and if present, the cached version is copied.

    Args:
        source (Path): Path to the source file or directory.
        dest (Path):Path to the destination.
        cache (Path or None): Optional Path to a cache directory.
    """
    if _DRY_RUN:
        return

    if cache:
        source = check_cache(source, cache)

    # TODO: error handling
    make_dirs(dest.parent)
    if source.is_dir():
        shutil.copytree(source, dest)
    elif source.is_file():
        shutil.copy(source, dest)


def remove_path(path: Path) -> None:
    """
    Deletes `path` fully. Take care!

    Args:
        path (Path): Path to the file or directory to delete.
    """
    if _DRY_RUN:
        return

    if path.is_dir():
        shutil.rmtree(path)
    elif path.is_file():
        path.unlink()


def open_path(path: Path, mode: str = "w", encoding: str = "utf-8") -> t.IO[t.Any]:
    """
    Opens `path` for reading/writing. Arguments are passed to `Path.open()`.
    """
    if mode[0] == "w" and _DRY_RUN:
        return io.StringIO()
    else:
        return path.open(mode, encoding=encoding)


def download_file(
    url: str,
    dest: Path,
    cache: Path | None = None,
    checksum: str | None = None,
    checksum_method: str = "sha1",
) -> bool:
    """
    Downloads a file from `url` to `dest`.

    If `cache` is given it will be checked for a cached version of the file first. If there is non, the file will be downloaded to `cache` first.

    If `checksum` and `checksum_method` are given, the file hash is verified
    once after download. An already cached version is not verified again.

    Args:
        url (str): URL to a valid file download.
        dest (Path): Path to the download destination.
        cache (Path or None): Optional path to a cache directory.
        checksum (str): Optional checksum hash of the file.
        checksum_method (str): Hashing method used for checksum verification (defaults to `sha1`).

    Returns:
        bool: If the download succeeded (or the file was copied from the cache).
    """
    if _DRY_RUN:
        return True

    url_parsed = urllib.parse.urlparse(url)
    url_path = Path(url_parsed.path)

    if cache:
        if cached := is_cached(url_path, cache):
            copy_path(cached, dest)
            return True

    with tempfile.TemporaryDirectory() as load_dest:
        load_dest = Path(load_dest)
        loaded_file, _ = urllib.request.urlretrieve(url, load_dest / url_path.name)

        if checksum:
            if not verify_checksum(loaded_file, checksum, method=checksum_method):
                raise IOError(f"Failed to verify checksum for download {url}.")

        if cache:
            # copied the download to the cache
            check_cache(loaded_file, cache)
        copy_path(loaded_file, dest)
    return True


def verify_checksum(file: Path, checksum: str, method: str = "sha1") -> bool:
    with file.open("rb") as f:
        digest = hashlib.file_digest(f, method)
    return digest.hexdigest() == checksum


def create_zip(path: Path, dest: Path | None = None) -> Path | None:
    """
    Creates a zip file from `path`.

    If `dest` is not given, the zip file is created in the same directory
    as `path` with the name of path and the suffix `.zip`. If `dest` is
    a Path to a `.zip` file, it is used as the zip target, otherwise it is
    used as the target directory.

    Returns the Path of the created file or `None` if the creation failed.

    Args:
        path (Path): Path to the file or directory to zip.
        dest (Path): Optional destination for the zip file.

    Returns:
        None or Path: The path of the created zip file.
    """
    if _DRY_RUN:
        return

    zip_file = path.with_suffix(".zip")
    if dest:
        if dest.suffix == ".zip":
            zip_file = dest
        else:
            zip_file = dest / zip_file.name

    make_dirs(zip_file.parent)
    if zip_file.is_file():
        if zip_file.is_file():
            remove_path(zip_file)

    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        if path.is_dir():
            for root, dirs, files in path.walk():
                for file in files:
                    filepath = root / file
                    relpath = filepath.relative_to(path)
                    zipf.write(filepath, arcname=relpath)
        elif path.is_file():
            zipf.write(path, arcname=path.name)
    return zip_file
