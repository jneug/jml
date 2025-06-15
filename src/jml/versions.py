import re
import shutil
import io
from datetime import datetime
from pathlib import Path
import typing as t
import zipfile
import logging

from rich.console import Console

from .util import match_patterns
from .config import CONFIG_FILE

# Some constants
RE_VERSION = re.compile(r"^\d+$")
RE_VERSION2 = re.compile(r"^([!<>=]{0,2})(\d+)$")
RE_REPLACE = re.compile(r"^(?<!\\)/(.*?)(?<!\\)/(.*)(?<!\\)/$")

ML_INT = -1

logger = logging.getLogger("jml")


def create_solution(config: dict, console: Console = None) -> set[int]:
    return create_version(ML_INT, config, console=console)


def create_version(version: int, config: dict, console: Console = None) -> set[int]:
    """Creates a version of the base project by parsing files for markers
    and copying only lines suitable to the given version number. The solution version is created for version number -1.

    The result is a set of version numbers discovered in the task markers
    of the parsed files. The set will always contain all version numbers
    up to the maximum found number.
    """
    # initialize some local vars
    console = console or Console()

    source_dir = config["source_dir"]
    output_dir = config["output_dir"]
    project_name = config["name"]

    dry_run = config["dry_run"]
    is_ml = version == ML_INT

    versions = set()

    # prepare output name
    if is_ml:
        ver_name = config["name_format"].format(
            project=project_name,
            version=config["solution_suffix"],
            date=datetime.now(),
        )
    elif version == 0:
        ver_name = project_name
    else:
        ver_name = config["name_format"].format(
            project=project_name, version=version, date=datetime.now()
        )
    output_dir = output_dir / ver_name

    if source_dir == output_dir:
        logger.warning(
            f"skipped {ver_name} (version {version})\noutput path would override source folder at {source_dir}"
        )
        return set()

    # prepare output folders
    if output_dir.is_dir():
        if config["clear"]:
            remove_path(output_dir, dry_run=dry_run)
            logger.info(f"removed target directory {output_dir}")
        else:
            logger.debug(f"using existing target directory at {output_dir}")
    if not output_dir.is_dir():
        make_dirs(output_dir, dry_run=dry_run)
        logger.info(f"created target directory {output_dir}")

    # extract some config options to local scope
    include = config["include"]
    exclude = config["exclude"]

    keep_empty_files = config["keep_empty_files"]

    # copy files in the source
    console.print(f"creating version [yellow]{ver_name}[/] in [cyan]{output_dir}[/]")
    for root, dirs, files in source_dir.walk():
        outroot = output_dir / root.relative_to(source_dir)
        make_dirs(outroot, dry_run=dry_run)

        for file in files:
            fullpath = root / file
            fulloutpath = outroot / file

            relpath = fullpath.relative_to(source_dir)
            reloutpath = fulloutpath.relative_to(output_dir.parent)

            if file == CONFIG_FILE:
                logger.debug(f"skipped config file `{CONFIG_FILE}`")
                continue
            elif match_patterns(file, exclude):
                logger.info(f"{relpath!s:>32} X")
                continue
            elif match_patterns(file, include):
                not_empty, _versions = compile_file(
                    version, fullpath, fulloutpath, config
                )
                versions = versions.union(_versions)

                if not not_empty and not keep_empty_files:
                    remove_path(fulloutpath, dry_run=dry_run)
                    logger.info(f"{relpath!s:>32} X  (empty)")
                else:
                    logger.info(f"{relpath!s:>32} !> {reloutpath!s}")
            else:
                copy_path(fullpath, fulloutpath, dry_run=dry_run)
                logger.info(f"{relpath!s:>32} -> {reloutpath!s}")

    # copy additional files
    additional_files = config["additional_files"]
    for file in additional_files:
        if file and file.exists():
            fulloutpath = output_dir / file.name
            copy_path(file, fulloutpath, dry_run=dry_run)
            logger.info(f"{file!s:>32} -> {fulloutpath}")

    if is_ml and config["delete_solution"]:
        remove_path(output_dir, dry_run=dry_run)
        logger.info(f"removed solution directory at `{output_dir}`")
    elif config["create_zip"] or config["create_zip_only"]:
        create_zip(output_dir, config)
        if config["create_zip_only"]:
            remove_path(output_dir, dry_run=dry_run)
            logger.info(f"removed version directory at `{output_dir}`")

    if not versions:
        versions.add(0)
    return versions


def compile_file(
    version: int, source: Path, target: Path, config: dict
) -> tuple[bool, set[int]]:
    """Compiles `source` into `target` by checking each line for opening / closing tags.

    Returns a tuple with a bool to indicate if at least one line was written and a set of version numbers found in `source`.
    """

    # extract some config options to local scope
    dry_run = config["dry_run"]

    tag_open = config["task_open"]
    tag_close = config["task_close"]

    ml_open = config["solution_open"]
    ml_close = config["solution_close"]

    transform_func = create_transform(version, config)

    versions = set()

    is_ml = version == ML_INT

    lines_written = 0
    with open_path(source, "r", encoding=config["encoding"], dry_run=dry_run) as inf:
        with open_path(target, encoding=config["encoding"], dry_run=dry_run) as outf:
            skip = False
            transform = None
            line = inf.readline()

            while line:
                lline = line.lstrip()
                if lline.startswith(ml_close) or lline.startswith(tag_close):
                    skip = False
                    transform = None
                elif lline.startswith(ml_open) and is_ml:
                    skip = False
                    transform = None
                elif lline.startswith(ml_open) and not is_ml:
                    parts = lline.split(maxsplit=3)
                    if len(parts) > 1:
                        v_match = RE_VERSION2.match(parts[1])
                        if v_match is not None:
                            versions.add(int(v_match.group(2)))
                        skip = not test_version(version, parts[1])
                    else:
                        skip = True
                elif lline.startswith(tag_open):
                    parts = lline.split(maxsplit=3)
                    if len(parts) > 1:
                        if is_ml:
                            v_match = RE_VERSION2.match(parts[1])
                            if v_match is not None:
                                versions.add(int(v_match.group(2)))
                            skip = True
                        else:
                            skip = not test_version(version, parts[1])
                    else:
                        skip = is_ml
                    transform = transform_func
                elif skip:
                    pass
                else:
                    if transform:
                        line = transform(line)
                    outf.write(line)
                    if len(line.strip()) > 0:
                        lines_written += 1
                line = inf.readline()
    return (lines_written > 0, versions)


def create_zip(path: str, config: dict) -> None:
    """Creates a zip file from a project version directory."""
    dry_run = config["dry_run"]

    if config["create_zip"] or config["create_zip_only"]:
        zip_dir, zip_name = path.parent, path.name

        # prepare output directory
        if not zip_dir.exists():
            make_dirs(zip_dir, dry_run=dry_run)

        # prepare output filename
        file = zip_dir / f"{zip_name}.zip"
        if file.exists():
            if file.is_file():
                remove_path(file, dry_run=dry_run)
            elif file.is_dir():
                logger.warning(f"directory found at {file}! unable to create zip file.")
                return

        # create zip file
        if not dry_run:
            try:
                with zipfile.ZipFile(file, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in path.walk():
                        for file in files:
                            filepath = root / file
                            relpath = filepath.relative_to(path)
                            zipf.write(filepath, arcname=relpath)
            except OSError as oserr:
                logger.warning(f"  could not create zip at {file} ({oserr.strerror})")
                return
        logger.info(f"created zip file at {file}")


def create_transform(version: int, config: dict) -> t.Callable:
    transform = lambda line: line  # noqa: E731

    prefix = config["task_comment_prefix"]
    if version == ML_INT:
        prefix = config["solution_comment_prefix"]

    if prefix:
        m = RE_REPLACE.match(prefix)
        if m:
            pat, repl = m.group(1).replace("\\/", "/"), m.group(2).replace("\\/", "/")
            pat, repl = re.compile(pat), repl

            def transform(line):
                return re.sub(pat, repl, line)

        else:
            pat = re.compile(f"^(\\s*)({prefix})")

            def transform(line):
                return re.sub(pat, "\\1", line)

    return transform


def test_version(version1: str | int, version2: str | int) -> bool:
    """Compares a version with a version string and checks if the first
    is in the range defined by the second. The second version can be
    prefixed by one of =, <, >, >=, <= or != to compare with a range of
    versions.
    """
    if not (v1_match := RE_VERSION2.match(str(version1))):
        return False
    if not (v2_match := RE_VERSION2.match(str(version2))):
        return True

    ver1 = int(version1)
    ver2 = int(v2_match.group(2))
    op = v2_match.group(1)

    if len(op) == 0 or op == "=":
        return ver1 == ver2
    if op == "=" or op == "==":
        return ver1 == ver2
    if op == "<=":
        return ver1 <= ver2
    if op == "<":
        return ver1 < ver2
    if op == ">=":
        return ver1 >= ver2
    if op == ">":
        return ver1 > ver2
    if op == "!=" or op == "<>":
        return ver1 != ver2
    return False


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
            shutil.copytree(source, target)
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
