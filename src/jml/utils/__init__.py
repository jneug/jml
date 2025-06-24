# -*- coding: utf-8 -*-

import fnmatch
import logging
import re
import urllib.parse
from pathlib import Path

import click
import rich
from rich.logging import RichHandler


RE_VERSION = re.compile(r"^\d+$")
RE_VERSION2 = re.compile(r"^([!<>=]{0,2})(\d+)$")


def configure_logger(
    log_level: int, debug: bool, dry_run: bool, console: rich.console.Console = None
) -> int:
    """Configures the logger for this run and returns the log level."""
    if dry_run:
        if log_level > logging.INFO:
            log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[
            RichHandler(
                console=console,
                show_time=False,
                tracebacks_suppress=[click],
                markup=True,
            ),
        ],
    )
    return log_level


def resolve_path(path: str | Path, root: str | Path = None) -> Path:
    """If path is a relative path, it is resolved to an absolute
    path by prefixing it with base. Otherwise it is returned as
    realpath. If base is omitted, os.getcwd() is used. Then this
    essentially replicates os.path.abspath()
    """
    path = Path(path)
    if not path.is_absolute():
        if not root:
            root = Path.cwd()
        path = Path(root) / path
    return path.resolve()


def match_patterns(file: str | Path, patterns: list[str]) -> bool:
    """Matches a file against a list of UNIX-like filename patterns.
    True is returned if filename is matched by at least one pattern.
    """
    file = str(file)
    for p in patterns:
        if fnmatch.fnmatch(file, p):
            return True
    return False


def is_url(url: str) -> bool:
    url = urllib.parse.urlparse(url)
    return url.scheme not in ("file", "")


def parse_url(url: str) -> tuple:
    return urllib.parse.urlparse(url)


def get_versions(line: str) -> set[int]:
    return set()


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
