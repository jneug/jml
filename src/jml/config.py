# -*- coding: utf-8 -*-

import importlib
import logging
from collections.abc import MutableMapping, Mapping, MutableSequence, Sequence
from pathlib import Path

import toml

from .utils import is_url, resolve_path

CONFIG_FILE = "jml.toml"


class ConfigDict(MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._data = {}
        data = data or {}
        self.update(data)
        self.update(kwargs)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, ConfigDict):
            value = ConfigDict(value)
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"ConfigDict({self._data})"

    # Ermöglicht config.key statt config['key']
    def __getattr__(self, attr: str) -> any:
        if attr.startswith("_"):
            raise AttributeError(attr)
        try:
            return self._data[attr]
        except KeyError as e:
            raise AttributeError(f"{attr}") from e

    def __setattr__(self, attr: str, value: any) -> None:
        if attr == "_data":
            super().__setattr__(attr, value)
        else:
            self[attr] = value

    def __delattr__(self, attr: str) -> None:
        try:
            del self[attr]
        except KeyError as e:
            raise AttributeError(attr) from e

    def ensure_dict(self, key: str) -> None:
        if key not in self:
            self[key] = ConfigDict()

    def merge(self, other: Mapping) -> None:
        for key, value in other.items():
            if key in ("include", "exclude"):
                self.resolve_source_set(key, value)
            elif (
                key in self
                and isinstance(self[key], ConfigDict)
                and isinstance(value, Mapping)
            ):
                self[key].merge(ConfigDict(value))
            elif (
                key in self
                and isinstance(self[key], MutableSequence)
                and isinstance(value, Sequence)
            ):
                self[key].extend(value)
            else:
                self[key] = ConfigDict(value) if isinstance(value, Mapping) else value

    def merge_left(self, other: Mapping) -> None:
        for key, value in other.items():
            if (
                key in self
                and isinstance(self[key], ConfigDict)
                and isinstance(value, Mapping)
            ):
                self[key].merge_left(ConfigDict(value))
            elif (
                key in self
                and isinstance(self[key], MutableSequence)
                and isinstance(value, Sequence)
            ):
                value.extend(self[key])
                self[key] = list(value)
            elif key not in self:
                self[key] = ConfigDict(value) if isinstance(value, Mapping) else value

    def resolve_paths(self, root: Path) -> None:
        pass

    def resolve_source_set(self, key: str, source_set: Sequence) -> None:
        self_set = self.get(key, set())

        for pattern in source_set:
            if pattern.startswith("-"):
                pattern = pattern[1:]
                self_set.discard(pattern)
            else:
                if pattern[0:2] == "\\-":
                    pattern = pattern[1:]
                self_set.add(pattern)

        self[key] = set(self_set)

    def __rich_repr__(self):
        yield from sorted(self.items(), key=lambda i: i[0])


# init logger
logger = logging.getLogger("jml")


def load_default_config() -> ConfigDict:
    config_file = importlib.resources.files() / CONFIG_FILE
    return load_config(config_file, config_file=None)


def load_config(
    path: Path,
    config_file: str = CONFIG_FILE,
    resolve: bool | Path = False,
    base: dict = None,
) -> ConfigDict | None:
    if config_file:
        path = path / config_file

    config = ConfigDict()
    if path.exists():
        config = ConfigDict(toml.load(path))
        logger.debug(f"loaded config from [path]{path}[/]")
        config = resolve_source_sets(config, base=base)

        if resolve:
            config = resolve_config(
                path, config, root=resolve if type(resolve) is not bool else None
            )

    if base:
        # config = {**base, **config}
        config.merge_left(base)

    return config if config else None


def resolve_config(
    config_file: Path, config: ConfigDict, root: Path | None = None
) -> ConfigDict:
    """Resolves the provided config by making relative path absolute in
    relation to the given config_file path.
    """
    if not root:
        root = config_file.parent

    for opt in ("output_dir", "project_root", "files_cache"):
        if opt in config:
            if config[opt]:
                config[opt] = resolve_path(config[opt], root=root)
            else:
                del config[opt]
    if "zip" in config and "dir" in config["zip"]:
        config["zip"]["dir"] = resolve_path(config["zip"]["dir"], root=root)

    if "files" in config:
        for i, file in enumerate(config["files"]):
            if not is_url(file["source"]):
                file["source"] = str(resolve_path(file["source"], root=root))
                config["files"][i] = file

    return config


def resolve_source_sets(
    config: ConfigDict, base: ConfigDict | None = None
) -> ConfigDict:
    if "sources" in config:
        for opt in ("exclude", "include"):
            value = set(base.get("sources", {}).get(opt, [])) if base else set()

            if opt in config["sources"]:
                remove = set()

                for pattern in config["sources"][opt]:
                    if pattern.startswith("-"):
                        pattern = pattern[1:]
                        remove.add(pattern)
                    else:
                        if pattern[0:2] == "\\-":
                            pattern = pattern[1:]
                        value.add(pattern)

                config["sources"][opt] = value.difference(remove)
    return config


def load_options_config(options: dict) -> ConfigDict:
    """
    Creates a compatible config dictionary from the click options
    passed to the main click command.
    """
    options_config = ConfigDict()
    for k, v in options.items():
        if v is not None:
            if k.startswith("task"):
                options_config.ensure_dict("tasks")
                options_config.tasks[k[5:]] = v
            elif k.startswith("solution"):
                options_config.ensure_dict("solutions")
                options_config.solutions[k[10:]] = v
            elif k in ("include", "exclude", "encoding"):
                options_config.ensure_dict("sources")
                options_config.sources[k] = v
            elif k == "delete_empty" and v:
                options_config.ensure_dict("sources")
                options_config.sources.keep_empty_files = False
                options_config.sources.keep_empty_dirs = False
            elif k == "no_clear" and v:
                options_config.clear = False
            elif k == "create_zip" and v:
                options_config.ensure_dict("zip")
                options_config.zip.create = True
            elif k == "delete_solution" and v:
                options_config.ensure_dict("solutions")
                options_config.solutions.delete = True
            else:
                options_config[k] = v

    return options_config
