# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from pathlib import Path

import click

# Current version number
from jml import __cmdname__, __version__

from .config import (
    load_config,
    load_default_config,
    load_options_config,
)
from .console import console
from .utils import configure_logger, resolve_path, files
from .versions import create_solution, create_version


@click.command(
    __cmdname__,
    help="""
    Erstellt Projektversionen aus einer Projektvorlage.
    """,
)
@click.version_option(version=__version__, prog_name=__cmdname__)
@click.argument(
    "source",
    metavar="IN",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path
    ),
)
@click.option(
    "-o",
    "--output-dir",
    "--out",
    metavar="OUT",
    help="Pfad des Zielordners. Standard ist das Verzeichnis in dem IN liegt.",
    type=click.Path(writable=True, path_type=Path),
)
@click.option(
    "-n",
    "--name",
    help="Name der Projektversionen. Standard ist der Ordnername von IN.",
    type=str,
)
@click.option(
    "-nf",
    "--name-format",
    metavar="FORMAT",
    help="Format für die Namen der Projektversionen. Angabe als Python-Formatstring. Kann die Variablen {project}, {version} und {date} enthalten. Standard: {project}_{version}",
)
@click.option(
    "-mls",
    "--solution-suffix",
    "--ml-suffix",
    metavar="SUFFIX",
    help="Suffix für die Musterlösung. Standard: ML",
)
@click.option(
    "-to",
    "--task-open",
    "--tag-open",
    metavar="TAG",
    help="Öffnende Aufgaben-Markierung.Standard: /*aufg*",
)
@click.option(
    "-tc",
    "--task-close",
    "--tag-close",
    metavar="TAG",
    help="Schließende Aufgaben-Markierung. Standard: *aufg*/",
)
@click.option(
    "-mlo",
    "--solution-open",
    "--ml-open",
    metavar="TAG",
    help="Öffnende Lösungs-Markierung. Standard: //ml*",
)
@click.option(
    "-mlc",
    "--solution-close",
    "--ml-close",
    metavar="TAG",
    help="Schließende Lösungs-Markierung. Standard: //*ml",
)
@click.option(
    "-i",
    "--include",
    metavar="PATTERN",
    multiple=True,
    help="Liste mit Suchmustern für Dateien, die nach JML-Kommentaren durchsucht werden sollen. Standard: *.java",
)
@click.option(
    "-e",
    "--exclude",
    metavar="PATTERN",
    multiple=True,
    help="Liste mit Suchmustern für Dateien, die komplett ignoriert werden und nicht in den Projektversionen auftauchen. Standard: *.class,*.ctxt,.DB_Store,Thumbs.db",
)
@click.option(
    "-v",
    "--ver",
    metavar="VER",
    multiple=True,
    # type=int,
    help="Liste von Versionen, die erstellt werden sollen.",
)
@click.option(
    "-root",
    "--project-root",
    metavar="PATH",
    help="Bestimmt ein Verzeichnis, das als Wurzelverzeichnis für mehrere Projekte dient. Wenn dies ein Prefix von IN ist, dann reflektiert die Ordnerstruktur in OUT die des Wurzelverzeichnisses. Für IN=/projects/foo/bar/my-project OUT=/projects/out project-root=/projects werden die Projektversionen dann in /projects/out/foo/bar erstellt.",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--encoding",
    default="utf-8",
    help="Zeichencodierung für Dateien. Standard: utf-8",
)
@click.option(
    "--no-clear",
    is_flag=True,
    help="Verhindert das Löschen der Projektversionen vor Ausführung.",
)
@click.option(
    "--delete-empty",
    is_flag=True,
    help="Leere Dateien aus den Projektversionen löschen.",
)
@click.option(
    "-z",
    "--create-zip",
    is_flag=True,
    help="Zusätzlich ZIP-Dateien zu den Projektversionen erstellen.",
)
@click.option(
    "--delete-solution",
    "--no-ml",
    is_flag=True,
    help="Keinen Musterlösung erstellen. Beachte, dass die Musterlösung immer erstellt wird, um die zu erstellenden Projektversionen zu ermitteln. Diese Option löscht den Ordner am Ende wieder.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Zeigt Informationen zur Fehlersuche an.",
)
@click.option(
    "--log-level",
    metavar="LEVEL",
    default=logging.WARNING,
    help="Setzt den Logging-Level.",
    type=int,
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Führt keine Operationen aus, sondern zeigt nur an, welche Änderungen vorgenommen würden. Impliziert --debug.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    source: Path,
    output_dir: Path,
    project_root: Path,
    ver: list[int],
    #
    debug: bool,
    log_level: int,
    dry_run: bool,
    #
    **options,
) -> None:
    console.print(
        f"[bold]{__cmdname__}[/] ([logging.keyword]{__version__}[/]) [[log.time]{datetime.now():%H:%M:%S.%f}[/]]"
    )

    # init logger
    configure_logger(log_level, debug, dry_run, console=console)
    logger = logging.getLogger("jml")

    if dry_run:
        files.enable_dry_run()
        console.print(
            "  this is a preview of the compilation process",
            style="red italic",
        )
        console.print("  run again without --dry-run to execute", style="red italic")

    source = resolve_path(source)

    # build config for this run
    ## load defaults
    config = load_default_config()
    ## read config from user home
    config = load_config(Path.home() / ".config", base=config)

    # resolve root directory from options or project config
    project_config = load_config(source, resolve=True)
    if project_root:
        config["project_root"] = resolve_path(project_root)
    else:
        if "project_root" in project_config and project_config["project_root"]:
            config["project_root"] = resolve_path(project_config["project_root"])
        else:
            config["project_root"] = source.parent
    project_root = config["project_root"]

    ## load project root config
    config = load_config(project_root, base=config, resolve=True)
    ## load project specific config
    config.merge(project_config)
    ## add cli options to config
    config.merge(load_options_config(options))

    ## cleanup some config options
    if not config["name"]:
        config["name"] = source.name

    # check tag options for incompatibilities
    if config.tasks.open == config.tasks.close:
        console.print(
            ":cross_mark: opening and closing task tags need to be unique:",
            style="red bold",
        )
        console.print(
            f"  current setting: [bold]`{config.tasks.open}` / `{config.tasks.close}`[/]"
        )
        ctx.exit(1)

    if config.solutions.open == config.solutions.close:
        console.print(
            ":cross_mark: opening and closing solution tags need to be unique:",
            style="red bold",
        )
        console.print(
            f"  current setting: [bold]`{config.solutions.open}` / `{config.solutions.close}`[/]"
        )
        ctx.exit(1)

    # prepare source and output_dir
    config["source_dir"] = source
    config["dry_run"] = dry_run

    if not config["output_dir"]:
        config["output_dir"] = source.parent / __cmdname__
    output_dir = config["output_dir"] = resolve_path(config["output_dir"])

    if output_dir.is_relative_to(source):
        console.print(
            ":cross_mark: output directory may not be inside the project folder:",
            style="red bold",
        )
        console.print(f"  current setting: [path]{output_dir}[/]")
        ctx.exit(1)

    if project_root and source.parent.is_relative_to(project_root):
        output_dir = config["output_dir"] = output_dir / source.parent.relative_to(
            project_root
        )

    # show config for debugging
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("config loaded:")
        console.print(config, highlight=True)

    #  run jml
    console.rule()
    logger.info(f":thread: compiling source project [name]{config['name']}[/]")
    logger.info(f"   from [path]{source}[/]")
    logger.info(f"     to [path]{output_dir}[/]")

    logger.info(":thread: Generating solution version..")
    generate_versions = set(ver)
    versions = create_solution(config, console=console)

    if max(versions) > 0:
        versions = {v + 1 for v in range(max(versions))}
    if generate_versions:
        generate_versions = {int(v) for v in generate_versions if int(v) in versions}
        # generate_versions = generate_versions.intersection(versions)
    else:
        generate_versions = versions
    logger.info(
        f"auto-discovered {len(generate_versions)} of {len(versions)} versions to generate: [jml.ver]{generate_versions}[/]"
    )

    for ver in sorted(generate_versions):
        logger.info(f":thread: generating version [jml.ver]{ver}[/]:")
        create_version(ver, config, console=console)


# When run as a single file outside module structure
if __name__ == "__main__":
    cli()
