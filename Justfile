set positional-arguments := true

root := justfile_directory()

[private]
default:
    @just --list --unsorted

[group('docs')]
docs:
    mkdocs build

[group('docs')]
serve:
    mkdocs serve
