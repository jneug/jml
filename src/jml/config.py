# -*- coding: utf-8 -*-

import toml
import logging
from pathlib import Path
import importlib

from .util import resolve_path


CONFIG_FILE = "jml.toml"


# init logger
logger = logging.getLogger("jml")


def load_default_config() -> dict:
    config_file = importlib.resources.files() / CONFIG_FILE
    return load_config(config_file, config_file=None)


def load_config(
    path: Path,
    config_file: str = CONFIG_FILE,
    resolve: bool | Path = False,
    base: dict = None,
) -> dict | None:
    if config_file:
        path = path / config_file

    config = {}
    if path.exists():
        config = toml.load(path)
        logger.debug(f"loaded config from {path}")

        if resolve:
            config = resolve_config(
                path, config, root=resolve if type(resolve) is not bool else None
            )

    if base:
        config = {**base, **config}

    return config if config else None


def resolve_config(config_file: Path, config: dict, root: Path | None = None) -> dict:
    """Resolves the provided config by making relative path absolute in
    relation to the given config_file path.
    """
    if not root:
        root = config_file.parent

    for opt in ("output_dir", "create_zip_dir", "project_root"):
        if opt in config:
            config[opt] = resolve_path(config[opt], root=root)

    for opt in ("exclude", "include", "additional_files"):
        if opt in config:
            # get current list
            value = set(config[opt])
            # update list
            if f"+{opt}" in config:
                files = config["+{opt}"]
                del config["+{opt}"]
                value.update(files)
            if f"-{opt}" in config:
                files = config["-{opt}"]
                del config["-{opt}"]
                value.difference_update(files)
            # write new list back to config
            if opt == "additional_files":
                # resolve paths for additional files
                new_value = set()
                for path in value:
                    if path:
                        new_value.add(resolve_path(path, root=root))
                config[opt] = new_value
            else:
                config[opt] = value

    return config


def load_options_config(options: dict) -> dict:
    """
    Creates a compatible config dictionary from the click options
    passed to the main click command.
    """
    options = {k: v for k, v in options.items() if v}

    if "delete_empty" in options:
        options["keep_empty_files"] = not options["delete_empty"]
        del options["delete_empty"]

    if "no_clear" in options:
        options["clear"] = not options["no_clear"]
        del options["no_clear"]

    return options
