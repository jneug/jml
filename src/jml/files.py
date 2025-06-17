from pathlib import Path
import urllib.parse
import urllib.request
import shutil
import tempfile
import logging
import hashlib
from collections.abc import Iterable

from .util import resolve_path, is_url
from jml import __cmdname__, __version__


logger = logging.getLogger("jml")


def process_files(output_dir: Path, config: dict) -> Iterable[Path]:
    if "files" in config:
        if "files_cache" in config:
            file_cache = Path(config["files_cache"])
        else:
            # temporary cache folder to prevent duplicate downloads
            file_cache = Path(tempfile.gettempdir()) / __cmdname__ / __version__
        file_cache.mkdir(parents=True, exist_ok=True)

        for file in config["files"]:
            file["source_path"] = resolve_path(file["source"])
            file["target_path"] = resolve_path(file["name"], root=output_dir)

            logger.debug(f"processing {file['source']}")
            if processed_file := process_file(file, config, cache=file_cache):
                yield processed_file


def process_file(file: dict, config: dict, cache: Path) -> Path:
    if is_url(file["source"]):
        if config["dry_run"]:
            logger.debug(
                f"downloading file from {file['source']} to {file['target_path']}"
            )
        else:
            if (
                download_file(file["source"], file["target_path"], cache=cache)
                and "checksum" in file
            ):
                if not verify_download(
                    file["target_path"],
                    file["checksum"],
                    method=file.get("checksum_method") or "sha256",
                ):
                    logger.warning(
                        f"failed to verify checksum for {file['target_path']} "
                    )
                    file["target_path"].unlink()
                    return None
                else:
                    logger.debug(f"verified checksum for {file['target_path']} ")
        return file["target_path"]
    elif file["source_path"].exists():
        if config["dry_run"]:
            logger.debug(
                f"copying file from {file['source_path']} to {file['target_path']}"
            )
        else:
            copy_file(file["source_path"], file["target_path"], cache=cache)
        return file["target_path"]
    else:
        return None


def copy_file(source: Path, target: Path, cache: Path) -> bool:
    if cached := is_cached(source, cache):
        source = cached
    else:
        if source.is_dir():
            shutil.copytree(source, cache / source.name)
        elif source.is_file():
            shutil.copy(source, cache)

    # TODO: error handling
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, target)
    elif source.is_file():
        shutil.copy(source, target)
    logger.debug(f"copied from {source} to {target}")
    return True


def download_file(url: str, target: Path, cache: Path) -> bool:
    url_parsed = urllib.parse.urlparse(url)
    file_name = Path(url_parsed.path).name

    if cached := is_cached(file_name, cache):
        copy_file(cached, target, cache)
        return True

    # load file into cache
    try:
        source, _ = urllib.request.urlretrieve(url, cache / file_name)
        copy_file(source, target, cache)
        logger.debug(f"downloaded file {url} to {target}")
        return True
    except urllib.error.HTTPError as http_e:
        logger.warning(f"error downloading from {url}:")
        logger.warning(f"  {http_e!s}")
        return False


def verify_download(file: Path, checksum: str, method: str = "sha256") -> bool:
    hash_method = hashlib.new(method)
    with file.open("rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            hash_method.update(block)
    return hash_method.hexdigest() == checksum


def is_cached(path: str | Path, cache: Path) -> Path | None:
    name = Path(path).name
    for file in cache.glob(name):
        if file.is_file():
            return file
    return None


# Utilities for file operations
## just wrappers that respect DRY_RUN settings
def open_path(
    path: Path, mode: str = "w", encoding: str = "utf-8", dry_run: bool = False
) -> t.IO[t.Any]:
    """Opens a file for reading/writing."""
    if mode[0] == "w" and dry_run:
        logger.debug(f"created file {path!s}")
        return io.StringIO()
    else:
        return path.open(mode, encoding=encoding)


def copy_path(source: Path, target: Path, dry_run: bool = False) -> None:
    if not dry_run:
        if source.is_dir():
            shutil.copytree(source, target / source.name)
        else:
            shutil.copy(source, target)
    else:
        logger.debug(f"copied {source!s} to {target!s}")


def remove_path(path: Path, dry_run: bool = False) -> None:
    if not dry_run:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    else:
        logger.debug(f"deleted {path!s}")


def make_dirs(path: Path, dry_run: bool = False, exist_ok: bool = True) -> None:
    if not dry_run:
        path.mkdir(exist_ok=exist_ok, parents=True)
    else:
        logger.debug(f"created directory {path!s}")
