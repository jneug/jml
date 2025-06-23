set positional-arguments := true

root := justfile_directory()

run *args:
  uv run jml {{ args }}

[private]
default:
    @just --list --unsorted

[group('docs')]
serve:
    uv run mkdocs serve

[group('docs')]
docs:
    uv run mkdocs build

[group('docs')]
deploy:
    uv run mkdocs gh-deploy

[group('test')]
test *args:
  uv run pytest {{ args }}
