# Changelog
Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/)
und diese Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.5] - 2022-03-04
### Added
- ML-Tags können nun um eine Versionsnummer ergänzt werden, um den Inhalt auch in Versionen aufzunehmen. `//ml* >2` würde den Inhalt in `//*ml` die Musterlösung und alle Versionen größer `2` aufnehmen.

### Fixed
- Mit `--debug` wird die geladene Konfiguration wieder korrekt angezeigt.

## [0.3.4] - 2022-01-25
### Changed
- Ohne `--debug` werden nun trotzdem einige minimale informative Ausgaben gemacht.

### Fixed
- Verbesserte Fehlerbehandlung bei falschen Dateirechten. `jml` bricht nun mit einer Fehlermeldung ab, wenn auf Dateien oder Ordner keine Schreib- / Leserechte bestehen.
- Verbesserte Erkennung, ob das Quellverzeichnis versehentlich überschrieben wird.

## [0.3.3] - 2022-01-24
### Added
- Option `--log-level` zum Setzen eine individuellen Log-Levels. `--debug` setzt den Log-Level auf `logging.DEBUG` (`10`), `--dry-run` auf `logging.INFO` (`20`). Standard ist `logging.WARNING` (`30`) und gibt nur Fehler und Warnungen aus.
- Neues Logo.

### Changed
- Verbesserte Erkennung von Versionsnummern. Der text zwischen den ersten beiden Leerzeichen (nach `task open`) wird nun als Versionsnummer erkannt. Dies erlaubt es, kurze Kommentare zu den Aufgaben einzufügen. Ist der erkannte Text keine Versionsnummer (also eine Zahl, die optional mit einem Vergleichsoperator versehen ist), dann wird die Versionsnummer `0` angenommen und die Aufgabe jeder Version hinzugefügt.

### Changed
- Konsolenausgabe verbessert.
- Debugging nun mit nativem `logging` Modul umgesetzt.

## [0.3.1] - 2022-01-23
### Fixed
- Problem beim Ermitteln des korrekten Wurzelverzeichnisses behoben.

## [0.3.0] - 2022-01-22
### Added
- `--dry-run` Option, um sich Änderungen nur anzeigen zu lassen, ohne sie auszuführen.

### Changed
- Hilfeausgabe mit `-h` / `--help` verbessert.

## [0.2.10] - 2022-01-22
### Changed
- `task comment prefix` / `solution comment prefix` Optionen erkennen erweiterten Modus nun zuverlässiger. Dadurch kann `//` als normales Prefix verwendet werden.

## [0.2.9] - 2022-01-22
### Added
- Optionen `task comment prefix` und `solution comment prefix`, um ein Prefix aus Zeilen in Aufgaben / Lösungen zu entfernen.

### Changed
- Tag-Optionen umbenannt und vereinheitlicht (z.B. `opening tag` -> `task open`, `opening ml tag` -> `solution open`, ...).

### Fixed
- Projektversion `0` wurde manchmal nicht korrekt erstellt.

## [0.2.6] - 2022-01-22
### Added
- Pfadnamen sind nun relativ zur Konfigurationsdatei, in der sie vorkommen. Optionen auf der Kommandozeile sind weiter relativ zum Arbeitsverzeichnis.
- `+additional files` / `-additional files` Optionen.

### Changed
- Ausgabeordner ist jetzt ein optionales Argument und kann alternativ auch in Konfigurationsdateien über `output dir` gesetzt werden.

## [0.2.5] - 2022-01-22
### Added
- `-include` / `-exclude` erlauben das selektive löschen von Suchmustern für Dateien.

### Changed
- Verbesserte Hilfetexte.
