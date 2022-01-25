#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
import fnmatch
import io
import logging
import os
import re
import shutil
import sys
import typing as t
import zipfile
from datetime import datetime


# Current version number
__version__ = "0.3.4"


# Some constants
RE_VERSION = re.compile(r"^\d+$")
RE_VERSION2 = re.compile(r"^([!<>=]{0,2})(\d+)$")
RE_REPLACE = re.compile(r"^(?<!\\)/(.*?)(?<!\\)/(.*)(?<!\\)/$")

ML_INT = -1

CONFIG_FILE = ".jml"
CONFIG_SECTION = "settings"
DEFAULT_CONFIG = {
    "name": "",
    "output dir": "",
    "task open": "/*aufg*",
    "task close": "*aufg*/",
    "task comment prefix": "",
    "solution open": "//ml*",
    "solution close": "//*ml",
    "solution comment prefix": "",
    "solution suffix": "ML",
    "name format": "{project}_{version}",
    "include": "*.java",
    "+include": "",
    "-include": "",
    "exclude": "*.class,*.ctxt,.DS_Store,Thumbs.db,*.iml,.vscode,.eclipse",
    "+exclude": "",
    "-exclude": "",
    "create zip": "no",
    "create zip only": "no",
    "create zip dir": "",
    "encoding": "utf-8",
    "additional files": "",
    "+additional files": "",
    "-additional files": "",
    "project root": "",
    "clear": "yes",
    "delete solution": "no",
    "keep empty files": "yes",
    "keep empty folders": "yes",
}

DEBUG_FLAG = False
DRY_RUN = False

logger = logging.getLogger("jml")


# Initialize argument parser
parser = argparse.ArgumentParser(
    prog="jml",
    description="Generiert aus einem Basisprojekt mehrere Projektversionen.",
    add_help=False,
)

# version and help
parser.add_argument(
    "-h",
    "--help",
    action="help",
    help="Diesen Hilfetext anzeigen.",
)
parser.add_argument(
    "--version",
    action="version",
    version="%(prog)s, " + __version__,
    help="Programmversion anzeigen.",
)

# arguments
parser.add_argument("srcdir", metavar="IN", help="Pfad des Basisprojektes")

# options
parser.add_argument(
    "-o",
    "--outdir",
    dest="output dir",
    metavar="OUT",
    help="Pfad des Zielordners. Standard ist das Verzeichnis in dem IN liegt.",
)
parser.add_argument(
    "-n",
    "--name",
    dest="name",
    action="store",
    help="Name der Projektversionen. Standard ist der Name von IN.",
)
parser.add_argument(
    "-nf",
    "--name-format",
    dest="name format",
    metavar="FORMAT",
    action="store",
    help="Format für die Namen der Projektversionen. Angabe als Python-Formatstring. Kann die Variablen {project}, {version} und {date} enthalten. Standard: {project}_{version}",
)
parser.add_argument(
    "-mls",
    "--ml-suffix",
    dest="solution suffix",
    metavar="SUFFIX",
    action="store",
    help="Suffix für die Musterlösung. Standard: ML",
)
parser.add_argument(
    "-to",
    "--tag-open",
    dest="task open",
    metavar="TAG",
    action="store",
    help="Öffnende Aufgaben-Markierung.Standard: /*aufg*",
)
parser.add_argument(
    "-tc",
    "--tag-close",
    dest="task close",
    metavar="TAG",
    action="store",
    help="Schließende Aufgaben-Markierung. Standard: *aufg*/",
)
parser.add_argument(
    "-mlo",
    "--ml-open",
    dest="solution open",
    metavar="TAG",
    action="store",
    help="Öffnende Lösungs-Markierung. Standard: //ml*",
)
parser.add_argument(
    "-mlc",
    "--ml-close",
    dest="solution close",
    metavar="TAG",
    action="store",
    help="Schließende Lösungs-Markierung. Standard: //*ml",
)
parser.add_argument(
    "-i",
    "--include",
    dest="include",
    action="extend",
    nargs="+",
    help="Liste mit Suchmustern für Dateien, die nach JML-Kommentaren durchsucht werden sollen. Standard: *.java",
)
parser.add_argument(
    "-e",
    "--exclude",
    dest="exclude",
    action="extend",
    nargs="+",
    help="Liste mit Suchmustern für Dateien, die komplett ignoriert werden und nicht in den Projektversionen auftauchen. Standard: *.class,*.ctxt,.DB_Store,Thumbs.db",
)
parser.add_argument(
    "-v",
    "--versions",
    dest="versions",
    metavar="VER",
    action="extend",
    nargs="+",
    type=str,
    help="Liste von Versionen, die erstellt werden sollen.",
)
parser.add_argument(
    "--project-root",
    dest="project root",
    metavar="PATH",
    action="store",
    help="Bestimmt ein Verzeichnis, das als Wurzelverzeichnis für mehrere Projekte dient. Wenn dies ein Prefix von IN ist, dann reflektiert die Ordnerstruktur in OUT die des Wurzelverzeichnisses. Für IN=/projects/foo/bar/my-project OUT=/projects/out project-root=/projects werden die Projektversionen dann in /projects/out/foo/bar erstellt.",
)
parser.add_argument(
    "--encoding",
    dest="encoding",
    action="store",
    help="Zeichencodierung für Dateien. Standard: utf-8",
)
parser.add_argument(
    "--no-clear",
    dest="clear",
    action="store_false",
    help="Verhindert das Löschen der Projektversionen vor Ausführung.",
)
parser.add_argument(
    "--delete-empty",
    dest="keep empty files",
    action="store_false",
    default=True,
    help="Leere Dateien aus den Projektversionen löschen.",
)
parser.add_argument(
    "-z",
    "--zip",
    dest="create zip",
    action="store_true",
    default=False,
    help="Zusätzlich ZIP-Dateien zu den Projektversionen erstellen.",
)
parser.add_argument(
    "--no-ml",
    dest="delete solution",
    action="store_true",
    default=False,
    help="Keinen Musterlösung erstellen. Beachte, dass die Musterlösung immer erstellt wird, um die zu erstellenden Projektversionen zu ermitteln. Diese Option löscht den Ordner am Ende wieder.",
)

parser.add_argument(
    "--debug",
    dest="debug",
    action="store_true",
    help="Zeigt Informationen zur Fehlersuche an.",
)
parser.add_argument(
    "--log-level",
    dest="log_level",
    metavar="LEVEL",
    action="store",
    default=logging.WARNING,
    type=int,
    help="Setzt den Logging-Level.",
)
parser.add_argument(
    "--dry-run",
    dest="dry_run",
    action="store_true",
    help="Führt keine Operationen aus, sondern zeigt nur an, welche Änderungen vorgenommen würden. Impliziert --debug.",
)


# main function
def main() -> None:
    args = parser.parse_args()
    configure_logger(args)

    print(f"jml ({__version__}) [{datetime.now():%H:%M:%S.%f}]")
    if DRY_RUN:
        print("  this is a preview of the compilation process")
        print("  run again without --dry-run to execute\n")

    # check srcdir
    srcdir = args.srcdir = resolve_path(args.srcdir)
    if not os.path.isdir(srcdir):
        print(f"Source directory {srcdir} not found! Please select a valid source.")
        quit()

    # resolve rootdir (requires to read project config to get final project root)
    project_root = vars(args)["project root"]
    if project_root:
        project_root = resolve_path(project_root)

    ## read project config, to get final rootdir
    proj_config = None
    proj_config_file = os.path.join(srcdir, CONFIG_FILE)
    if os.path.exists(proj_config_file):
        proj_config = configparser.ConfigParser(
            interpolation=None, converters={"list": lambda v: re.split(r"[,;\n]+", v)}
        )
        if read_config(proj_config, proj_config_file, resolve=False):
            if not project_root and proj_config.has_option(CONFIG_SECTION, "project root"):
                project_root = resolve_path(
                    proj_config.get(CONFIG_SECTION, "project root"), srcdir
                )

    # build config for this run
    config = configparser.ConfigParser(
        interpolation=None, converters={"list": lambda v: re.split(r"[,;\n]+", v)}
    )

    # set defaults
    config[CONFIG_SECTION] = DEFAULT_CONFIG
    settings = config[CONFIG_SECTION]

    # read default user config
    user_config_file = os.path.expanduser(os.path.join("~", CONFIG_FILE))
    if read_config(config, user_config_file):
        logger.debug(f"read config from user home at {user_config_file}")
    if not project_root and settings["project root"]:
        project_root = settings["project root"]
    # read project root config
    if project_root:
        root_config_file = os.path.join(project_root, CONFIG_FILE)
        if read_config(config, root_config_file):
            logger.debug(f"read config from project root at {root_config_file}")
    # read project specific config
    if proj_config:
        config.read_dict(proj_config, source=proj_config_file)
        resolve_config(config, base=srcdir)
        logger.debug(f"read config from source dir at {proj_config_file}")
    # unset everything other than default keys
    for k in settings.keys():
        if k not in DEFAULT_CONFIG.keys():
            del settings[k]

    # add cli arguments to config
    args_to_config(
        settings,
        args,
        flags={
            "keep empty files": False,
            "create zip": True,
            "delete solution": True,
            "clear": False,
        },
    )
    if project_root:
        settings["project root"] = project_root
    if not settings["name"]:
        settings["name"] = os.path.basename(srcdir)

    # show config for debugging
    if DEBUG_FLAG:
        logger.debug("config loaded:")
        for k, v in sorted(settings.items()):
            logger.debug(f"    {k} = {v}")

    # check tag options for incompatibilities
    if settings["task open"] == settings["task close"]:
        print("opening and closing task tags need to be unique.")
        print(f"  current setting: {settings['task open']} / {settings['task close']}")
        quit()

    if settings["solution open"] == settings["solution close"]:
        print("opening and closing solution tags need to be unique.")
        print(f"  current setting: {settings['solution open']} / {settings['solution close']}")
        quit()

    # prepare outdir
    outdir = vars(args)["output dir"]
    if not outdir:
        if not settings["output dir"]:
            # outdir = os.getcwd()
            outdir = os.path.join(os.path.dirname(srcdir), 'jml')
        else:
            outdir = settings["output dir"]
    else:
        outdir = resolve_path(outdir)
    if project_root and os.path.commonprefix([project_root, srcdir]) == project_root:
        outdir = os.path.dirname(
            os.path.join(outdir, srcdir[len(project_root) + len(os.sep) :])
        )
    settings["output dir"] = outdir

    #  run jml
    logger.info("compiling source project <{}>".format(settings["name"]))
    logger.info(f"  from {srcdir}")
    logger.info(f"    to {outdir}\n")

    logger.info("creating solution version:")
    versions = create_version(ML_INT, settings)

    if max(versions) > 0:
        versions = {v + 1 for v in range(max(versions))}
    if args.versions:
        versions = {int(v) for v in args.versions if int(v) in versions}
    logger.info(f"auto-discovered {len(versions)} versions to generate: {versions}")

    for ver in sorted(versions):
        logger.info(f"creating version {ver}:")
        create_version(ver, settings)


def create_version(version: int, settings: configparser.SectionProxy) -> t.Set[int]:
    """Creates a version of the base project by parsing files for markers and
    copying only lines suitable to the given version number. The solution version
    is created for version number -1.

    The result is a set of version numbers discovered in the task markers of the
    parsed files. The set will always contain all version numbers up to the maximum
    found number.
    """
    # initialize some local vars
    srcdir = settings["srcdir"]
    outdir = settings["output dir"]
    name = settings["name"]
    is_ml = version == ML_INT

    versions = set()

    # prepare output name
    if is_ml:
        ver_name = settings["name format"].format(
            project=name,
            version=settings["solution suffix"],
            date=datetime.now(),
        )
    elif version == 0:
        ver_name = name
    else:
        ver_name = settings["name format"].format(
            project=name, version=version, date=datetime.now()
        )
    outdir = os.path.join(outdir, ver_name)

    if srcdir == outdir:
        logger.warning(f"skipped {ver_name} (version {version})")
        logger.warning(f"  output path would override source folder at {srcdir}")
        return set()

    # prepare output folders
    if os.path.isdir(outdir):
        if settings.getboolean("clear"):
            remove_dir(outdir)
            logger.info(f"  removed target directory {outdir}")
        else:
            logger.debug(f"  using existing target directory at {outdir}")
    if not os.path.isdir(outdir):
        make_dirs(outdir)
        logger.info(f"  created target directory {outdir}")

    # extract some config options to local scope
    include = settings.getlist("include")  # type: ignore
    exclude = settings.getlist("exclude")  # type: ignore
    encoding = settings["encoding"]

    tag_open = settings["task open"]
    tag_close = settings["task close"]

    ml_open = settings["solution open"]
    ml_close = settings["solution close"]

    transform_func = create_transform(version, settings)

    keep_empty_files = settings.getboolean("keep empty files")

    strippos = len(srcdir) + 1

    # compile files in the srcdir
    print(f"  creating version {ver_name} in {outdir}")
    for root, dirs, files in os.walk(srcdir):
        subpath = root[strippos:]
        outroot = os.path.join(outdir, subpath)

        make_dirs(outroot)

        for file in files:
            fullpath = os.path.join(root, file)
            fulloutpath = os.path.join(outroot, file)

            if file == CONFIG_FILE:
                continue
            elif match_patterns(file, exclude):
                logger.info(f"    {file:>32} X")
                continue
            elif match_patterns(file, include):
                is_empty = True
                with open(fullpath, "r", encoding=encoding) as inf:
                    with open_file(fulloutpath, encoding=encoding) as outf:
                        skip = False
                        transform = None
                        line = inf.readline()
                        # if encoding != 'utf-8':
                        #   line = line.decode(encoding).encode()
                        while line:
                            lline = line.lstrip()
                            if lline.startswith(ml_close) or lline.startswith(
                                tag_close
                            ):
                                skip = False
                                transform = None
                            elif lline.startswith(ml_open):
                                skip = not is_ml
                                transform = transform_func
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
                                is_empty = is_empty or len(line.strip()) > 0
                            line = inf.readline()
                if is_empty and not keep_empty_files:
                    os.remove(fulloutpath)
                    logger.info(f"    {file:>32} X  (empty)")
                else:
                    logger.info(f"    {file:>32} !> {fulloutpath}")
            else:
                copy_file(fullpath, fulloutpath)
                logger.info(f"    {file:>32} -> {fulloutpath}")

    # copy additional files
    additional_files = settings.getlist("additional files")  # type: ignore
    for file in additional_files:
        if file:
            if os.path.isfile(file):
                fulloutpath = os.path.join(outdir, os.path.basename(file))
                copy_file(file, fulloutpath)
                logger.info(f"    {file:>32} -> {fulloutpath}")

    if is_ml and settings.getboolean("delete solution"):
        remove_dir(outdir)
        logger.info("  removed compiled ml directory")
    elif settings.getboolean("create zip") or settings.getboolean("create zip only"):
        create_zip(outdir, settings)
        if settings.getboolean("create zip only"):
            remove_dir(outdir)
            logger.info("  removed compiled version directory")

    if not versions:
        versions.add(0)
    return versions


def create_zip(path: str, settings: configparser.SectionProxy) -> None:
    """Creates a zip file from a project version directory."""
    if settings.getboolean("create zip") or settings.getboolean("create zip only"):
        dir, filename = os.path.split(path)

        # prepare output directory
        if settings["create zip dir"]:
            dir = resolve_path(settings["create zip dir"])
        if not os.path.exists(dir):
            make_dirs(dir)

        # prepare output filename
        filename = f"{filename}.zip"
        outfile = os.path.join(dir, filename)
        if os.path.isfile(outfile) and not DRY_RUN:
            os.remove(outfile)
        elif os.path.isdir(outfile):
            logger.warning(f"  directory found at {outfile}! unable to create zip file.")
            return

        # create zip file
        if not DRY_RUN:
            try:
                with zipfile.ZipFile(outfile, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            filepath = os.path.join(root, file)
                            relpath = os.path.relpath(filepath, start=path)
                            zipf.write(filepath, arcname=relpath)
            except OSError as oserr:
                logger.warning(f"  could not create zip at {outfile} ({oserr.strerror})")
                return
        logger.info(f"  created zip file at {outfile}")


def resolve_path(path: str, base: str = None) -> str:
    """If path is a relative path, it is resolved to an absolute
    path by prefixing it with base. Otherwise it is returned as
    realpath. If base is omitted, os.getcwd() is used. Then this
    essentially replicates os.path.abspath()
    """
    if not path:
        return ""
    if not os.path.isabs(path):
        if not base:
            base = os.getcwd()
        path = os.path.normpath(os.path.join(base, path))
    return os.path.realpath(path)


def configure_logger(args: argparse.Namespace) -> None:
    """Configures the logger for this run.
    """
    globals()["DRY_RUN"] = bool(args.dry_run)
    if DRY_RUN:
        # args.debug = True
        if args.log_level > logging.INFO:
            args.log_level = logging.INFO
    if args.debug:
        args.log_level = logging.DEBUG

    logging.basicConfig(level=args.log_level, format="%(message)s")


def read_config(config: configparser.ConfigParser, config_file: str, resolve: bool = True) -> bool:
    """Reads the ini file config_file into the given ConfigParser object
    and calls resolve_config.
    """
    if os.path.isfile(config_file):
        try:
            config.read(config_file)
        except configparser.DuplicateOptionError:
            logger.error(f"duplicate option in {config_file}")
            quit()
        except configparser.DuplicateSectionError:
            logger.error(f"duplicate section in {config_file}")
            quit()
        except configparser.MissingSectionHeaderError:
            logger.error(f"missing [settings] section in {config_file}")
            quit()
        except configparser.ParsingError:
            logger.error(f"error parsing config file {config_file}")
            quit()
        if resolve:
            resolve_config(config, base=os.path.dirname(config_file))
        return True
    return False


def resolve_config(config: configparser.ConfigParser, base: str = None) -> None:
    """Resolves the provided ConfigParser by making relative path absolute in
    relation to the given base path.
    """
    for opt in ("output dir", "create zip dir", "project root"):
        if config.has_option(CONFIG_SECTION, opt):
            path = config.get(CONFIG_SECTION, opt)
            config.set(CONFIG_SECTION, opt, resolve_path(path, base))

    for opt in ("exclude", "include", "additional files"):
        # get current list
        value = set(config.getlist(CONFIG_SECTION, opt))  # type: ignore
        # update list
        if config.has_option(CONFIG_SECTION, f"+{opt}"):
            add = config.getlist(CONFIG_SECTION, f"+{opt}")  # type: ignore
            config.remove_option(CONFIG_SECTION, f"+{opt}")
            value.update(add)
        if config.has_option(CONFIG_SECTION, f"-{opt}"):
            sub = config.getlist(CONFIG_SECTION, f"-{opt}")  # type: ignore
            config.remove_option(CONFIG_SECTION, f"-{opt}")
            value.difference_update(sub)
        # write new list back to config
        if opt == "additional files":
            # resolve paths for additional files
            new_value = set()
            for path in value:
                if path:
                    new_value.add(resolve_path(path, base))
            config.set(CONFIG_SECTION, opt, ",".join(new_value))
        else:
            config.set(CONFIG_SECTION, opt, ",".join(value))


def args_to_config(
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
    the option is only overridden, if the flag was supplied with the arguments.
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


def create_transform(version: int, settings: configparser.SectionProxy) -> t.Callable:
    transform = lambda line: line  # noqa: E731

    prefix = settings["task comment prefix"]
    if version == ML_INT:
        prefix = settings["solution comment prefix"]

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


def match_patterns(filename: str, patterns: t.List[str]) -> bool:
    """Matches a filename against a list of UNIX-like filename patterns.
    True is returned, if filename matches at least one pattern.
    """
    for p in patterns:
        if fnmatch.fnmatch(filename, p):
            return True
    return False


def test_version(version1: t.Union[str, int], version2: t.Union[str, int]) -> bool:
    """Compares a version with a version string and checks if the first
    is in the range defined by the second. The second version can be
    prefixed by one of =, <, >, >=, <= or != to compare with a range of
    versions.
    """
    if RE_VERSION2.match(str(version1)) is None:
        return False
    v2_match = RE_VERSION2.match(str(version2))
    if v2_match is None:
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
def open_file(path: str, mode: str = "w", encoding: str = "utf-8") -> t.IO[t.Any]:
    """Opens a file for reading/writing.
    """
    if mode[0] == "w" and DRY_RUN:
        return io.StringIO()
    else:
        try:
            return open(path, mode, encoding=encoding)
        except OSError as oserr:
            abort("could not open file", err=oserr)
            quit()


def copy_file(inpath: str, outpath: str) -> None:
    if not DRY_RUN:
        try:
            shutil.copy(inpath, outpath)
        except OSError as oserr:
            abort("could not copy file", err=oserr)


def remove_dir(inpath: str) -> None:
    if not DRY_RUN:
        try:
            shutil.rmtree(inpath)
        except OSError as oserr:
            abort(f"could not remove directory {inpath}", err=oserr)


def make_dirs(path: str, exist_ok: bool = True) -> None:
    if not DRY_RUN:
        try:
            os.makedirs(path, exist_ok=exist_ok)
        except OSError as oserr:
            abort("could not create directory", err=oserr)


def abort(message: str = "", err: OSError = None) -> None:
    """Shows an optional error message, shuts everything down and
    aborts the script with error code 1.
    """
    if message:
        logger.error(message)
    if err:
        logger.error(f"  ({err.errno}) {err.filename}: {err.strerror}")
    logging.shutdown()
    print("-- operation aborted --")
    quit(1)


# When run as a single file outside module structure
if __name__ == "__main__":
    main()
