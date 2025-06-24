import logging
import re
import tempfile
import typing as t
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from rich.console import Console

from jml import __cmdname__, __version__

from .config import CONFIG_FILE, ConfigDict
from .utils import files, is_url, match_patterns, resolve_path, test_version, parse_url

# Some constants
RE_VERSION = re.compile(r"^\d+$")
RE_VERSION2 = re.compile(r"^([!<>=]{0,2})(\d+)$")

ML_INT = -1

logger = logging.getLogger("jml")


def create_solution(config: dict, console: Console = None) -> set[int]:
    return create_version(ML_INT, config, console=console)


def create_version(
    version: int, config: ConfigDict, console: Console = None
) -> set[int]:
    """Creates a version of the base project by parsing files for markers
    and copying only lines suitable to the given version number. The solution version is created for version number -1.

    The result is a set of version numbers discovered in the task markers
    of the parsed files. The set will always contain all version numbers
    up to the maximum found number.
    """
    # initialize some local vars
    console = console or Console()

    # build version specific configuration
    vconfig = ConfigDict(config)
    vconfig.project_name = vconfig.name
    vconfig.no = version
    vconfig.is_ml = version == ML_INT
    vconfig.output_root = vconfig.output_dir

    def relp(p: Path) -> Path:
        if p.is_relative_to(vconfig.project_root):
            return p.relative_to(vconfig.project_root)
        elif p.is_relative_to(vconfig.output_root):
            return p.relative_to(vconfig.output_root)
        else:
            return p

    # prepare output name
    if vconfig.is_ml:
        vconfig.name = vconfig.name_format.format(
            project=vconfig.project_name,
            version=vconfig.solutions.suffix,
            date=datetime.now(),
        )
    elif version == 0:
        vconfig.name = vconfig.project_name
    else:
        vconfig.name = vconfig.name_format.format(
            project=vconfig.project_name, version=version, date=datetime.now()
        )
    vconfig.output_dir = vconfig.output_dir / vconfig.name

    # merge in version specific config
    vconfig.merge(
        next(
            (cfg for cfg in config.versions if "no" in cfg and cfg["no"] == version),
            dict(),
        )
    )

    if vconfig.source_dir == vconfig.output_dir:
        logger.warning(
            f"skipped [jml.ver]{vconfig.name}[/] (version [jml.ver]{vconfig.no}[/])\noutput path would override source folder at [jml.path]{relp(vconfig.source_dir)}[/]"
        )
        return set()

    # prepare output folders
    if vconfig.output_dir.is_dir():
        if vconfig.clear:
            files.remove_path(vconfig.output_dir)
            logger.info(
                f"removed target directory [jml.path]{relp(vconfig.output_dir)}[/]"
            )
        else:
            logger.debug(
                f"using existing target directory at [jml.path]{relp(vconfig.output_dir)}[/]"
            )
    if not vconfig.output_dir.is_dir():
        files.make_dirs(vconfig.output_dir)
        logger.info(f"created target directory [jml.path]{relp(vconfig.output_dir)}[/]")

    # extract some config options to local scope
    include = config.sources.include
    exclude = config.sources.exclude

    keep_empty_files = config.sources.keep_empty_files
    keep_empty_dirs = config.sources.keep_empty_dirs

    versions = set()

    # copy files in the source
    console.print(
        f"creating version [jml.ver]{vconfig.name}[/] in [jml.path]{relp(vconfig.output_dir)}[/]"
    )
    for root, dirs, source_files in vconfig.source_dir.walk():
        outroot = vconfig.output_dir / root.relative_to(vconfig.source_dir)
        files.make_dirs(outroot)

        for file in source_files:
            fullpath = root / file
            fulloutpath = outroot / file

            relpath = fullpath.relative_to(vconfig.source_dir)
            reloutpath = fulloutpath.relative_to(vconfig.output_dir.parent)

            if file == CONFIG_FILE:
                logger.debug(f"[jml.file]{relpath!s:>32}[/] [red bold]X[/]  (skipped)")
                continue
            elif match_patterns(relpath, exclude):
                logger.info(f"[jml.file]{relpath!s:>32}[/] [red bold]X[/]")
                continue
            elif match_patterns(relpath, include):
                not_empty, _versions = compile_file(
                    version, fullpath, fulloutpath, vconfig
                )
                versions = versions.union(_versions)

                if not not_empty and not keep_empty_files:
                    files.remove_path(fulloutpath)
                    logger.info(f"[jml.file]{relpath!s:>32}[/] [red bold]X[/]  (empty)")
                else:
                    logger.info(
                        f"[jml.file]{relpath!s:>32}[/] [yellow bold]!>[/] [jml.path]{reloutpath!s}[/]"
                    )
            else:
                files.copy_path(fullpath, fulloutpath)
                logger.info(
                    f"[jml.file]{relpath!s:>32}[/] [green bold]->[/] [jml.path]{reloutpath!s}[/]"
                )

    # process additional files
    if not vconfig.is_ml or not vconfig.solutions.delete:
        for f in process_files(vconfig.output_dir, vconfig):
            logger.info(f"{'':>32} [green bold]->[/] {relp(f)!s}")

    if vconfig.is_ml and vconfig.solutions.delete:
        files.remove_path(vconfig.output_dir)
        logger.info(
            f"removed solution directory at [jml.path]{relp(vconfig.output_dir)}[/]"
        )
    elif vconfig.zip.create or vconfig.zip.only_zip:
        try:
            zip_file = files.create_zip(vconfig.output_dir, dest=vconfig.zip.dir)
            logger.info(f"created zip file at [jml.path]{relp(zip_file)}[/]")
        except OSError as oserr:
            logger.warning(f"failed to create zip: [jml.err]{oserr.strerror}[/]")
        finally:
            if vconfig.zip.only_zip:
                files.remove_path(vconfig.output_dir)
                logger.info(
                    f"removed version directory at [jml.path]{relp(vconfig.output_dir)}[/]"
                )

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
    tag_open = config.tasks.open
    tag_close = config.tasks.close

    ml_open = config.solutions.open
    ml_close = config.solutions.close

    transform_func = create_transform(version, config)

    versions = set()

    is_ml = version == ML_INT

    lines_written = 0
    with files.open_path(source, "r", encoding=config.sources.encoding) as inf:
        with files.open_path(target, encoding=config.sources.encoding) as outf:
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


def create_transform(version: int, config: ConfigDict) -> t.Callable:
    transform = lambda line: line  # noqa: E731

    prefix = config.tasks.line.prefix
    replace = config.tasks.line.replace
    if version == ML_INT:
        prefix = config.solutions.line.prefix
        replace = config.solutions.line.replace

    if prefix:
        if replace:
            prefix = re.compile(prefix)

            def transform(line):
                return re.sub(prefix, replace, line)
        else:
            pat = re.compile(f"^(\\s*)({prefix})")

            def transform(line):
                return re.sub(pat, "\\1", line)

    return transform


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

            logger.debug(f"processing [jml.path]{file['name']}[/]")
            if processed_file := process_file(file, config, cache=file_cache):
                yield processed_file


def process_file(file: dict, config: dict, cache: Path) -> Path:
    if is_url(file["source"]):
        try:
            # Create host-specific cache folder to prevent name collisions
            parsed_url = parse_url(file["source"])
            cache = cache / parsed_url.hostname
            cache.mkdir(exist_ok=True)

            files.download_file(
                file["source"],
                file["target_path"],
                cache=cache,
                checksum=file.get("checksum"),
                checksum_method=file.get("checksum_method", "sha1"),
            )
        except OSError as oserr:
            logger.warning(
                f"failed to download file from [jml.path]{file['source']}[/]: [jml.err]{oserr}[/]"
            )
            return None
        return file["target_path"]
    elif file["source_path"].exists():
        files.copy_path(file["source_path"], file["target_path"], cache=cache)
        return file["target_path"]
    else:
        return None
