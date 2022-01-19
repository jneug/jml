#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
import fnmatch
import os
import re
import shutil
import sys
import typing as t
import zipfile
from datetime import datetime

__version__ = "0.2.4"


parser = argparse.ArgumentParser(
    prog="jml", description="Generiert aus einem Basisprojekt mehrere Projektversionen."
)

parser.add_argument(
    "--version",
    action="version",
    version="%(prog)s, " + __version__,
    help="Programmversion anzeigen.",
)

parser.add_argument("srcdir", metavar="IN", help="Pfad des Basisprojektes")
parser.add_argument("outdir", metavar="OUT", help="Pfad des Zielordners")
parser.add_argument(
    "-n",
    "--name",
    dest="name",
    action="store",
    help="Name des Projektes. Standard ist der Name von IN",
)
parser.add_argument(
    "--no-clear",
    dest="clear",
    action="store_false",
    help="Löscht den Zielordner, bevor die Projektversionen erstellt werden",
)
parser.add_argument(
    "-to",
    "--tag-open",
    dest="opening tag",
    action="store",
    help="Öffnender Tag für Aufgaben",
)
parser.add_argument(
    "-tc",
    "--tag-close",
    dest="closing tag",
    action="store",
    help="Schließender Tag für Aufgaben",
)
parser.add_argument(
    "-mlo",
    "--ml-open",
    dest="opening ml tag",
    action="store",
    help="Öffnender Tag für Musterlösungen",
)
parser.add_argument(
    "-mlc",
    "--ml-close",
    dest="closing ml tag",
    action="store",
    help="Schließender Tag für Musterlösungen",
)
parser.add_argument(
    "-mls",
    "--ml-suffix",
    dest="ml suffix",
    action="store",
    help="Suffix für die Musterlösung",
)
parser.add_argument(
    "-nf",
    "--name-format",
    dest="name format",
    action="store",
    help="Format für die Namen der Projektversionen. Angabe als Python Formatstring. Kann die Variablen {project}, {version} und {date} enthalten.",
)
parser.add_argument(
    "-i",
    "--include",
    dest="include",
    action="extend",
    nargs="+",
    help="Liste mit Dateiendungen, die nach JML-Kommentaren durchsucht werden sollen",
)
parser.add_argument(
    "-e",
    "--exclude",
    dest="exclude",
    action="extend",
    nargs="+",
    help="Liste von Dateiendungen, die ignoriert werden",
)
parser.add_argument(
    "-v",
    "--versions",
    dest="versions",
    action="extend",
    type=str,
    help="Liste von Versionen, die erstellt werden sollen",
)
parser.add_argument(
    "--project-root",
    dest="project root",
    action="store",
    help="if set to a prefix of IN, the folder structure in OUT will reflect the structure of the project root. For IN=/projects/foo/bar/my-project OUT=/projects/out project-root=/projects the resulting versions will be written to /projects/out/foo/bar",
)
parser.add_argument(
    "--encoding",
    dest="encoding",
    action="store",
    help="Codierung für Dateien. Standard: utf-8",
)
parser.add_argument(
    "--delete-empty",
    dest="keep empty files",
    action="store_false",
    default=True,
    help="Als Standard werden leere Dateien in die Projektversionen kopiert. Diese Einstellung löscht leere Dateien.",
)
parser.add_argument(
    "-z",
    "--zip",
    dest="create zip",
    action="store_true",
    default=False,
    help="Erstellt zusätzlich ZIP-Dateien zu den Projektversionen.",
)
parser.add_argument(
    "--no-ml",
    dest="delete ml",
    action="store_true",
    default=False,
    help="Skip generating a ml version of the project. Note that the ml version is always generated, but this will delete the folder afterwards.",
)

parser.add_argument(
    "--debug",
    dest="debug",
    action="store_true",
    help="Zeigt Informationen zur Fehlersuche an.",
)


RE_VERSION = re.compile(r"^\d+$")
RE_VERSION2 = re.compile(r"^([!<>=]{0,2})(\d+)$")

CONFIG_FILE = ".jml"
CONFIG_SECTION = "settings"
DEFAULT_CONFIG = {
    "name": "",
    "opening tag": "/*aufg*",
    "closing tag": "*aufg*/",
    "opening ml tag": "//ml*",
    "closing ml tag": "//*ml",
    "ml suffix": "ML",
    "name format": "{project}_{version}",
    "include": "*.java",
    "+include": "",
    "exclude": "*.class,*.ctxt,.DS_Store,Thumbs.db,*.iml,.vscode,.eclipse",
    "+exclude": "",
    "create zip": "no",
    "create zip only": "no",
    "create zip dir": "",
    "encoding": "utf-8",
    "additional files": "",
    "project root": "",
    "clear": "yes",
    "delete ml": "no",
    "keep empty files": "yes",
    "keep empty folders": "yes",
}

DEBUG_FLAG = False


def debug(msg: str, indent: int = 0) -> None:
    """Shows a debug message if debugging is enabled."""
    if globals()["DEBUG_FLAG"]:
        if indent:
            print(indent * "  " + msg)
        else:
            print(msg)


def main() -> None:
    args = parser.parse_args()

    debug_flag = args.debug
    globals()["DEBUG_FLAG"] = debug_flag

    # check srcdir
    srcdir = args.srcdir = resolve_path(args.srcdir)
    if not os.path.isdir(srcdir):
        print(
            f"Quellverzeichnis <{srcdir}> ist nicht vorhanden! Bitte wähle ein gültiges Projektverzeichnis."
        )
        quit()

    # resolve final outdir (requires to get final project root from config)
    project_root = vars(args)["project root"]
    if project_root:
        project_root = resolve_path(project_root)

    # read project config first, to get final root dir
    proj_config = None
    proj_config_file = os.path.join(srcdir, CONFIG_FILE)
    if os.path.exists(proj_config_file):
        proj_config = configparser.ConfigParser(interpolation=None)
        proj_config.read(proj_config_file)
        debug(f"read config from source dir at <{proj_config_file}>")
        if not project_root and proj_config.has_option(
            CONFIG_SECTION, "project root"
        ):
            project_root = resolve_path(proj_config.get(CONFIG_SECTION, "project root"))

    outdir = args.outdir = resolve_path(args.outdir)
    if (
        project_root
        and os.path.commonprefix([project_root, srcdir]) == project_root
    ):
        outdir = args.outdir = os.path.dirname(
            os.path.join(outdir, srcdir[len(project_root) + len(os.sep) :])
        )

    # build config for this run
    config = configparser.ConfigParser(
        interpolation=None, converters={"list": lambda v: re.split(r"[,;\n]+", v)}
    )
    # running list of patterns
    excludes = set()
    includes = set()
    # set defaults
    config[CONFIG_SECTION] = DEFAULT_CONFIG
    settings = config[CONFIG_SECTION]

    # read default user config
    user_config_file = os.path.expanduser(os.path.join("~", CONFIG_FILE))
    if os.path.exists(user_config_file):
        config.read(user_config_file)
        debug(f"read config from user home at <{user_config_file}>")
        excludes.update(settings.getlist("+exclude"))  # type: ignore
        includes.update(settings.getlist("+include"))  # type: ignore
    # read project root config
    if project_root:
        root_config_file = os.path.join(project_root, CONFIG_FILE)
        if os.path.exists(root_config_file):
            config.read(root_config_file)
            debug(f"read config from project root at <{root_config_file}>")
            excludes.update(settings.getlist("+exclude"))  # type: ignore
            includes.update(settings.getlist("+include"))  # type: ignore
    # read project specific config
    if proj_config:
        config.read_dict(proj_config, source=proj_config_file)
        excludes.update(settings.getlist("+exclude"))  # type: ignore
        includes.update(settings.getlist("+include"))  # type: ignore
    # unset everything other than default keys
    for k in settings.keys():
        if k not in DEFAULT_CONFIG.keys():
            del settings[k]

    # add cli arguments
    merge_configs(
        settings,
        args,
        flags={"keep empty files": False, "create zip": True, "delete ml": True, "clear": False},
    )
    if project_root:
        settings["project root"] = project_root
    if not settings["name"]:
        settings["name"] = os.path.basename(srcdir)

    # set include sets
    excludes.update(settings.getlist("exclude"))  # type: ignore
    includes.update(settings.getlist("include"))  # type: ignore
    settings["exclude"] = ",".join(excludes)
    settings["include"] = ",".join(includes)
    del settings["+exclude"]
    del settings["+include"]

    # show config for debugging
    if debug_flag:
        debug("config loaded:")
        for k, v in sorted(settings.items()):
            debug(f"{k} = {v}", 1)

    # check tag options for incompatibilities
    if settings["opening tag"] == settings["closing tag"]:
        print(
            "Die öffnenden und schließenden Tags für Aufgaben müssen unterschiedlich sein."
        )
        print("  Bitte setze einzigartige Tags. Z.B. @jml und lmj@")
        print(
            "  Aktuell angegeben: {} / {}".format(
                settings["opening tag"],
                settings["closing tag"],
            )
        )
        quit()

    if settings["opening ml tag"] == settings["closing ml tag"]:
        print(
            "Die öffnenden und schließenden Tags für Musterlösungen müssen unterschiedlich sein."
        )
        print("  Bitte setze einzigartige Tags. Z.B. @jml und lmj@")
        print(
            "  Aktuell angegeben: {} / {}".format(
                settings["opening ml tag"],
                settings["closing ml tag"],
            )
        )
        quit()

    #  run jml
    debug("Compiling source project <{}>".format(settings["name"]))
    debug(f"from <{srcdir}>", 1)
    debug(f"  to <{outdir}>", 1)

    debug("Creating solution version:")
    versions = create_solution(config)

    versions = versions.intersection(args.versions if args.versions else versions)
    for ver in sorted(versions):
        if any(test_version(ver, v) for v in versions):
            debug(f"Creating version {ver}:")
            create_version(ver, config)


def create_solution(config: configparser.ConfigParser) -> t.Set[str]:
    """Creates the solution version of the project by removing all task markers.
    During compilation all version numbers in task markers are collected and
    the set of version numbers is returned.
    """
    # initialize some local vars
    srcdir = config.get(CONFIG_SECTION, "srcdir")
    outdir = config.get(CONFIG_SECTION, "outdir")
    name = config.get(CONFIG_SECTION, "name")

    versions = set()

    # prepare output name
    ver_name = config.get(CONFIG_SECTION, "name format").format(
        project=name,
        version=config.get(CONFIG_SECTION, "ml suffix"),
        date=datetime.now(),
    )
    outdir = os.path.join(outdir, ver_name)

    # prepare output folders
    if os.path.isdir(outdir) and config.getboolean(CONFIG_SECTION, "clear"):
        shutil.rmtree(outdir)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    # extract some config options to local scope
    include = config.getlist(CONFIG_SECTION, "include")  # type: ignore
    exclude = config.getlist(CONFIG_SECTION, "exclude")  # type: ignore
    encoding = config.get(CONFIG_SECTION, "encoding")

    tag_open = config.get(CONFIG_SECTION, "opening tag")
    tag_close = config.get(CONFIG_SECTION, "closing tag")
    ml_open = config.get(CONFIG_SECTION, "opening ml tag")
    ml_close = config.get(CONFIG_SECTION, "closing ml tag")

    keep_empty = config.getboolean(CONFIG_SECTION, "keep empty files")

    # compile files
    debug(f"creating version {ver_name} in {outdir}", 1)
    for root, dirs, files in os.walk(srcdir):
        subpath = root[len(srcdir) + 1 :]
        outroot = os.path.join(outdir, subpath)

        os.makedirs(outroot, exist_ok=True)

        for file in files:
            fullpath = os.path.join(root, file)
            fulloutpath = os.path.join(outroot, file)

            _, ext = os.path.splitext(file)
            ext = ext[1:]

            if file == ".jml":
                continue
            elif match_patterns(file, exclude):
                debug(f"{file:>32} X", 2)
                continue
            elif match_patterns(file, include):
                is_empty = True
                with open(fullpath, "r", encoding=encoding) as inf:
                    with open(fulloutpath, "w", encoding=encoding) as outf:
                        skip = False
                        line = inf.readline()
                        while line:
                            lline = line.lstrip()
                            if lline.startswith(ml_close) or lline.startswith(ml_open):
                                pass
                            elif lline.startswith(tag_close):
                                skip = False
                            elif lline.startswith(tag_open):
                                parts = lline.split()
                                if len(parts) > 1:
                                    v_match = RE_VERSION2.match(parts[1])
                                    if v_match is not None:
                                        for v in range(int(v_match.group(2))):
                                            versions.add(f"{v+1}")
                                skip = True
                            elif skip:
                                pass
                            else:
                                outf.write(line)
                                is_empty = False
                            line = inf.readline()
                if is_empty and not keep_empty:
                    os.remove(fulloutpath)
                    debug(f"{file:>32} X  (empty)", 2)
                else:
                    debug(f"{file:>32} !> {fulloutpath}", 2)
            else:
                shutil.copy(fullpath, fulloutpath)
                debug(f"{file:>32} -> {fulloutpath}", 2)

    # copy additional files
    additional_files = config.getlist(CONFIG_SECTION, "additional files")  # type: ignore
    for file in additional_files:
        if file:
            file = resolve_path(file, srcdir)
            if os.path.isfile(file):
                fulloutpath = os.path.join(outdir, os.path.basename(file))
                shutil.copy(file, fulloutpath)
                debug(f"{file:>32} -> {fulloutpath}", 2)

    if config.getboolean(CONFIG_SECTION, "delete ml"):
        shutil.rmtree(outdir)
        debug("removed compiled ml directory", 1)
    elif config.getboolean(CONFIG_SECTION, "create zip") or config.getboolean(CONFIG_SECTION, "create zip only"):
        create_zip(outdir, config[CONFIG_SECTION])
        if config.getboolean(CONFIG_SECTION, "create zip only"):
            shutil.rmtree(outdir)
            debug("removed compiled ml directory", 1)

    if not versions:
        versions.add("0")
    return versions


def create_version(version: str, config: configparser.ConfigParser) -> None:
    """Creates a specific project version by removing all solution markers
    and checking task markers for applicable version numbers.
    """
    # initialize some local vars
    srcdir = config.get(CONFIG_SECTION, "srcdir")
    outdir = config.get(CONFIG_SECTION, "outdir")
    name = config.get(CONFIG_SECTION, "name")

    # prepare output name
    if version == "0":
        ver_name = name
    else:
        ver_name = config.get(CONFIG_SECTION, "name format").format(
            project=name, version=version, date=datetime.now()
        )
    outdir = os.path.join(outdir, ver_name)

    # prepare output folders
    if os.path.isdir(outdir):
        if config.getboolean(CONFIG_SECTION, "clear"):
            shutil.rmtree(outdir)
            debug(f"removed target directory <{outdir}>", 1)
        else:
            debug(f"using existing target directory at <{outdir}>", 1)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
        debug(f"created target directory <{outdir}>", 1)

    # extract some config options to local scope
    include = config.getlist(CONFIG_SECTION, "include")  # type: ignore
    exclude = config.getlist(CONFIG_SECTION, "exclude")  # type: ignore
    encoding = config.get(CONFIG_SECTION, "encoding")

    tag_open = config.get(CONFIG_SECTION, "opening tag")
    tag_close = config.get(CONFIG_SECTION, "closing tag")
    ml_open = config.get(CONFIG_SECTION, "opening ml tag")
    ml_close = config.get(CONFIG_SECTION, "closing ml tag")

    keep_empty = config.getboolean(CONFIG_SECTION, "keep empty files")

    # compile files in the srcdir
    debug(f"creating version {ver_name} in {outdir}", 1)
    for root, dirs, files in os.walk(srcdir):
        subpath = root[len(srcdir) + 1 :]
        outroot = os.path.join(outdir, subpath)

        os.makedirs(outroot, exist_ok=True)

        for file in files:
            fullpath = os.path.join(root, file)
            fulloutpath = os.path.join(outroot, file)

            _, ext = os.path.splitext(file)
            ext = ext[1:]

            if file == ".jml":
                continue
            elif match_patterns(file, exclude):
                debug(f"{file:>32} X", 2)
                continue
            elif match_patterns(file, include):
                is_empty = True
                with open(fullpath, "r", encoding=encoding) as inf:
                    with open(fulloutpath, "w", encoding=encoding) as outf:
                        skip = False
                        line = inf.readline()
                        # if encoding != 'utf-8':
                        #   line = line.decode(encoding).encode()
                        while line:
                            lline = line.lstrip()
                            if lline.startswith(ml_close) or lline.startswith(
                                tag_close
                            ):
                                skip = False
                            elif lline.startswith(ml_open):
                                skip = True
                            elif lline.startswith(tag_open):
                                parts = lline.split()
                                if len(parts) > 1:
                                    skip = not test_version(version, parts[1])
                                else:
                                    skip = False
                            elif skip:
                                pass
                            else:
                                outf.write(line)
                                is_empty = False
                            line = inf.readline()
                if is_empty and not keep_empty:
                    os.remove(fulloutpath)
                    debug(f"{file:>32} X  (empty)", 2)
                else:
                    debug(f"{file:>32} !> {fulloutpath}", 2)
            else:
                shutil.copy(fullpath, fulloutpath)
                debug(f"{file:>32} -> {fulloutpath}", 2)

    # copy additional files
    additional_files = config.getlist(CONFIG_SECTION, "additional files")  # type: ignore
    for file in additional_files:
        if file:
            file = resolve_path(file, srcdir)
            if os.path.isfile(file):
                fulloutpath = os.path.join(outdir, os.path.basename(file))
                shutil.copy(file, fulloutpath)
                debug(f"{file:>32} -> {fulloutpath}", 2)

    # Create zip file if option is set
    if config.getboolean(CONFIG_SECTION, "create zip") or config.getboolean(CONFIG_SECTION, "create zip only"):
        create_zip(outdir, config[CONFIG_SECTION])
        if config.getboolean(CONFIG_SECTION, "create zip only"):
            shutil.rmtree(outdir)
            debug("removed compiled project version directory", 1)


def create_zip(path: str, settings: configparser.SectionProxy) -> None:
    """Creates a zip file from a project version directory."""
    if settings.getboolean("create zip") or settings.getboolean("create zip only"):
        dir, filename = os.path.split(path)

        # prepare output directory
        if settings["create zip dir"]:
            dir = resolve_path(settings["create zip dir"])
        if not os.path.exists(dir):
            os.makedirs(dir)

        # prepare output filename
        filename = f"{filename}.zip"
        outfile = os.path.join(dir, filename)
        if os.path.isfile(filename):
            os.remove(outfile)
        elif os.path.isdir(filename):
            debug(f"directory found at <{outfile}>! unable to create zip file.", 1)
            return

        # create zip file
        with zipfile.ZipFile(outfile, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(path):
                for file in files:
                    filepath = os.path.join(root, file)
                    relpath = os.path.relpath(filepath, start=path)
                    zipf.write(filepath, arcname=relpath)
            debug(f"created zip file at <{outfile}>", 1)


def merge_configs(
    config: configparser.SectionProxy,
    args: argparse.Namespace,
    flags: t.Dict[str, bool] = dict(),
    strict: bool = False,
):
    """Merges a configparser.SectionProxy with an argparse.Namespace
    object. All key/value pairs from argparse are copied to the config object.
    If strict is True, only keys that already exist are updated, otherwise
    new keys are also added.

    flags is a dict of argument names that are used as boolean flags with
    the store_true/store_false action. The keys are the names of the argument
    destination and the values the boolean that is stored (e.g. True for store_true).
    This is necessary because boolean flags are always set and will override
    any value already set in the config object. By providing the flags dict,
    the option is only overriden, if the flag was supplied with the arguments.
    """
    for k, v in vars(args).items():
        if v is not None:
            if not strict or k in config:
                if k in flags:
                    if flags[k] == bool(v):
                        config[k] = str(v)
                elif isinstance(v, list):
                    config[k] = ",".join(v)
                else:
                    config[k] = str(v)


def match_patterns(filename: str, patterns: t.List[str]) -> bool:
    """Matches a filename against a list of UNIX-like filename patterns.
    True is returned, if filename matches at least one pattern.
    """
    for p in patterns:
        if fnmatch.fnmatch(filename, p):
            return True
    return False


def resolve_path(path: str, base: str = None) -> str:
    """If path is a relative path, it is resolved to an absolute
    path by prefixing it with base. Otherwise it is returned as
    realpath. If base is omitted, os.getcwd() is used. Then this
    essentially replicates os.path.abspath()
    """
    if not os.path.isabs(path):
        if not base:
            base = os.getcwd()
        path = os.path.normpath(os.path.join(base, path))
    return os.path.realpath(path)


def test_version(version1: str, version2: str) -> bool:
    """Compares a version with a version string and checks if the first
    is in the range defined by the second. The second version can be
    prefixed by one of =, <, >, >=, <= or != to compare with a range of
    versions.
    """
    if RE_VERSION2.match(version1) is None:
        return False
    v2_match = RE_VERSION2.match(version2)
    if v2_match is None:
        return False

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


# When run as a single file outside module structure
if __name__ == "__main__":
    main()
