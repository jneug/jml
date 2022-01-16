#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import shutil
import sys
import typing as t
import zipfile

__version__ = "0.0.4"


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
    "-c",
    "--clear",
    dest="clear",
    action="store_true",
    help="Löscht den Zielordner, bevor die Projektversionen erstellt werden",
)
parser.add_argument(
    "-to",
    "--tag-open",
    dest="tag_open",
    action="store",
    default="jml*",
    help="Öffnender Tag für Aufgaben",
)
parser.add_argument(
    "-tc",
    "--tag-close",
    dest="tag_close",
    action="store",
    default="*jml",
    help="Schließender Tag für Aufgaben",
)
parser.add_argument(
    "-mlo",
    "--ml-open",
    dest="ml_open",
    action="store",
    help="Öffnender Tag für Musterlösungen",
)
parser.add_argument(
    "-mlc",
    "--ml-close",
    dest="ml_close",
    action="store",
    help="Schließender Tag für Musterlösungen",
)
# TODO: Replace with projectname format
# Like -f "%(project)s-%(version)s" or -f "{date:"%Y"}.{project}-{version}"
parser.add_argument(
    "-mls",
    "--ml-suffix",
    dest="ml_suffix",
    action="store",
    default="ML",
    help="Suffix für die Musterlösung",
)
parser.add_argument(
    "-vs",
    "--ver-sep",
    dest="sep",
    action="store",
    default="_",
    help="Trennzeichen zwischen Projektname und Versionsnummer",
)
parser.add_argument(
    "-i",
    "--include",
    dest="include",
    action="extend",
    nargs="+",
    default=["java"],
    help="Liste mit Dateiendungen, die nach JML-Kommentaren durchsucht werden sollen",
)
parser.add_argument(
    "-e",
    "--exclude",
    dest="exclude",
    action="extend",
    nargs="+",
    default=["class", "ctxt", "Thumbs.db", ".DS_Store"],
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
    "--preset",
    dest="preset",
    choices=["xml", "de", "de-xml"],
    help="Setzt die Tags auf eine Vorgabe.",
)
parser.add_argument(
    "--project-root",
    dest="root",
    action="store",
    help="if set to a prefix of IN, the folder structure in OUT will reflect the structure of the project root. For IN=/projects/foo/bar/my-project OUT=/projects/out project-root=/projects the resulting versions will be written to /projects/out/foo/bar",
)
parser.add_argument(
    "--keep-empty",
    dest="keep_empty",
    action="store_true",
    help="Als Standard werden leere Dateien nicht in Projektversionen kopiert. Diese Einstellung behält leere Dateien bei.",
)
parser.add_argument(
    "--encoding",
    dest="encoding",
    action="store",
    default="utf-8",
    help="Codierung für Dateien. Standard: utf-8",
)
parser.add_argument(
    "-z",
    "--zip",
    dest="create_zip",
    action="store_true",
    default=False,
    help="Erstellt zusätzlich ZIP-Dateien zu den Projektversionen.",
)
parser.add_argument(
    "--no-ml",
    dest="delete_ml",
    action="store_true",
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

DEBUG_FLAG = False


def debug(msg: str) -> None:
    """Shows a debug message if debugging is enabled."""
    if globals()["DEBUG_FLAG"]:
        print(msg)


def main() -> None:
    args = parser.parse_args()
    globals()["DEBUG_FLAG"] = args.debug

    # load tag presets first
    if args.preset:
        if args.preset == "xml":
            args.tag_open = "<jml>"
            args.tag_close = "</jml>"
        elif args.preset == "de":
            args.tag_open = "aufg*"
            args.tag_close = "*aufg"
            args.ml_open = "ml*"
            args.ml_close = "*ml"
        elif args.preset == "de-xml":
            args.tag_open = "<aufg>"
            args.tag_close = "</aufg>"
            args.ml_open = "<ml>"
            args.ml_close = "</ml>"

    # check tag options
    if args.tag_open == args.tag_close:
        print(
            "Die öffnenden und schließenden Tags für Aufgaben müssen unterschiedlich sein."
        )
        print("Bitte setze einzigartige Tags. Z.B. @jml und lmj@")
        quit()

    if args.ml_open and args.ml_open == args.ml_close:
        print(
            "Die öffnenden und schließenden Tags für Musterlösungen müssen unterschiedlich sein."
        )
        print("Bitte setze einzigartige Tags. Z.B. @jml und lmj@")
        quit()

    # use same tags if only one given
    if not args.ml_open:
        args.ml_open = args.tag_open
    if not args.ml_close:
        args.ml_close = args.tag_close

    #  check dirs
    if os.path.isdir(args.srcdir):
        if not args.name:
            args.name = os.path.basename(args.srcdir)

        if args.root and os.path.commonprefix([args.root, args.srcdir]) == args.root:
            args.outdir = os.path.dirname(
                os.path.join(args.outdir, args.srcdir[len(args.root) + 1 :])
            )

        debug(
            f"Compiling project <{args.name}>\n  from <{args.srcdir}>\n  to <{args.outdir}>"
        )
        debug(f"Creating {args.ml_suffix} version:")
        versions = create_ml(args)

        if not args.versions:
            args.versions = versions
        for ver in versions:
            if any(test_version(ver, v) for v in args.versions):
                debug(f"Creating version {ver}:")
                create_version(ver, args)
    else:
        print(f"{args.srcdir} does not exist")


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


def create_zip(dir: str, args: argparse.Namespace) -> None:
    """Creates a zip file from a project version dir.
    """
    with zipfile.ZipFile(f"{dir}.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dir):
            for file in files:
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, start=dir)
                zipf.write(filepath, arcname=relpath)


def create_version(version: str, args: argparse.Namespace) -> None:
    """Creates a specific project version by removing all solution markers
    ans checking task markers for applicable version numbers.
    """
    # Prepare project name
    if version == "0":
        ver_name = args.name
    else:
        ver_name = f"{args.name}{args.sep}{version}"
    outdir = os.path.join(args.outdir, ver_name)

    # prepare output folders
    if os.path.isdir(outdir) and args.clear:
        shutil.rmtree(outdir)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    # compile files in the srcdir
    for root, dirs, files in os.walk(args.srcdir):
        subpath = root[len(args.srcdir) + 1 :]
        outroot = os.path.join(outdir, subpath)

        os.makedirs(outroot, exist_ok=True)

        for file in files:
            fullpath = os.path.join(root, file)
            fulloutpath = os.path.join(outroot, file)

            _, ext = os.path.splitext(file)
            ext = ext[1:]

            if ext in args.exclude:
                continue
            elif ext in args.include:
                is_empty = True
                with open(fullpath, "r", encoding=args.encoding) as inf:
                    with open(fulloutpath, "w", encoding=args.encoding) as outf:
                        skip = False
                        line = inf.readline()
                        # if args.encoding != 'utf-8':
                        #   line = line.decode(args.encoding).encode()
                        while line:
                            lline = line.lstrip()
                            if lline.startswith(f"//{args.ml_close}"):
                                skip = False
                            elif lline.startswith(f"{args.tag_close}*/"):
                                skip = False
                            elif lline.startswith(f"//{args.ml_open}"):
                                skip = True
                            elif lline.startswith(f"/*{args.tag_open}"):
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
                if is_empty and not args.keep_empty:
                    os.remove(fulloutpath)
            else:
                shutil.copy(fullpath, fulloutpath)

    # Create zip file if option is set
    if args.create_zip:
        create_zip(outdir, args)


def create_ml(args: argparse.Namespace) -> t.Set[str]:
    """Creates the solution version of the project by removing all task markers.
    During compilation all version numbers in task markers are collected and
    the set of version numbers is returned.
    """
    versions = set()

    ver_name = f"{args.name}{args.sep}{args.ml_suffix}"
    outdir = os.path.join(args.outdir, ver_name)

    # prepare output folders
    if os.path.isdir(outdir) and args.clear:
        shutil.rmtree(outdir)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    for root, dirs, files in os.walk(args.srcdir):
        subpath = root[len(args.srcdir) + 1 :]
        outroot = os.path.join(outdir, subpath)

        os.makedirs(outroot, exist_ok=True)

        for file in files:
            fullpath = os.path.join(root, file)
            fulloutpath = os.path.join(outroot, file)

            _, ext = os.path.splitext(file)
            ext = ext[1:]

            debug(f"working on {fullpath}")

            if ext in args.exclude:
                continue
            elif ext in args.include:
                is_empty = True
                with open(fullpath, "r", encoding=args.encoding) as inf:
                    with open(fulloutpath, "w", encoding=args.encoding) as outf:
                        skip = False
                        line = inf.readline()
                        while line:
                            lline = line.lstrip()
                            if lline.startswith(f"//{args.ml_close}"):
                                pass
                            elif lline.startswith(f"//{args.ml_open}"):
                                pass
                            elif lline.startswith(f"{args.tag_close}*/"):
                                skip = False
                            elif lline.startswith(f"/*{args.tag_open}"):
                                parts = lline.split()
                                if len(parts) > 1:
                                    ver = parts[1].lstrip("<>!=")
                                    versions.add(ver)
                                skip = True
                            elif skip:
                                pass
                            else:
                                outf.write(line)
                                is_empty = False
                            line = inf.readline()
                if is_empty and not args.keep_empty:
                    os.remove(fulloutpath)
            else:
                shutil.copy(fullpath, fulloutpath)

    if args.delete_ml:
        shutil.rmtree(outdir)
    elif args.create_zip:
        create_zip(outdir, args)

    if not versions:
        versions.add("0")
    return versions


# When run as a single file outside module structure
if __name__ == "__main__":
    main()
