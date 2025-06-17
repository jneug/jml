# -*- coding: utf-8 -*-

import logging
import click
import fnmatch
import rich
from pathlib import Path
import urllib.parse

from rich.logging import RichHandler


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


def match_patterns(filename: str, patterns: list[str]) -> bool:
    """Matches a filename against a list of UNIX-like filename patterns.
    True is returned if filename is matched by at least one pattern.
    """
    for p in patterns:
        if fnmatch.fnmatch(filename, p):
            return True
    return False


def is_url(url: str) -> bool:
    url = urllib.parse.urlparse(url)
    return url.scheme not in ("file", "")
