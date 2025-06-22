# Java Musterlösung (jml)

![](https://github.com/jneug/jml/raw/main/jml.png)

Java Musterlösung (kurz `jml`) ist ein Tool mit dem mehrere Projektversionen aus einer Musterlösung generiert werden können.

`jml` wurde ursprünglich für Java-Projekte entwickelt, kann aber durch diverse Optionen auch für andere Projekte genutzt werden.

## Motivation

Zur Differenzierung im Informatikunterricht erstelle ich gerne mehrere Projektversionen mit mehr oder weniger Hilfestellungen, um dem Leistungsstand der Schülerinnen und Schüler besser gerecht zu werden. Inklusive einer Musterlösung können so schnell drei bis vier Projektversionen entstehen, die parallel weiterentwickelt werden müssen.

Befindet sich ein Fehler im Code, sollen die Aufgaben angepasst werden oder hat sich einfach ein Rechtschreibfehler in einen Kommentar eingeschlichen, müssen alle Projektversionen angepasst werden. Dabei habe ich schnell mal eine Version vergessen oder einen neuen Fehler eingebaut.

Vor einigen Jahren habe ich den Prozess mit `jml` vereinfacht. Das Skript generiert aus einer Basisversion, die mit Markierungen für Aufgaben und Lösungen versehen ist, die verschiedenen Projektversionen, die für den Unterricht nötig sind. Anpassungen sind nur noch im Basisprojekt notwendig.

Beispiele zur Verwendung finden sich in [meinem Projekt-Repository](http://github.com/jneug/schule-projekte) und den
dazugehörigen [Projektversionen](http://github.com/jneug/schule-versionen).


## Installation

Die Installation wird wie gewohnt mit pip durchgeführt:

``console
$ pip3 install jml
``

Bei erfolgreicher Installation ist nun das `jml` Kommando verfügbar.

``console
$ jml --version
jml, version 0.3.6
``

`jml` benötigt Python 3.8 oder neuer.

### Manuelle Installation

`jml` kann auch ohne `pip` einfach als Skriptdatei genutzt werden. Es werden keine externen Abhängigkeiten genutzt. Dazu die aktuelle Version der Datei `jml.py <https://github.com/jneug/jml/blob/main/src/jml/jml.py>`_ aus dem Repository kopieren und auf der Festplatte speichern. Das Skript kann dann mit Python 3 ausgeführt werden:

``console
$ python3 jml.py --version
jml, version 0.3.6
``


## Benutzung

`jml` benötigt im einfachsten Fall den Pfad des Basisprojektes und den Pfad des Ausgabeordners:

``console
$ jml pfad/zum/Basisprojekt --out pfad/zum/ausgabeordner
``

Nach Ausführung befinden sich in `pfad/zum/ausgabeordner` die Musterlösung und die Projektversionen.

Die Inhalte und Anzahl an Versionen werden durch die Inhalte der Dateien im Basisprojekt bestimmt.

Angenommen in `Basisprojekt` liegt eine Datei mit dem Namen `Beispiel.java` mit folgendem Inhalt:

``java
class Beispiel {
	/*aufg*
	// TODO: Erstelle eine Objektvariable "zahl" vom Typ int
	*aufg*/
	//ml*
	private int zahl;
	//*ml

	public int add( int pAndereZahl ) {
		/*aufg*
		// TODO: Gib die Summe aus der Objektvariablen "zahl" und "pAndereZahl" zurück.
		return 0;
		*aufg*/
		//ml*
		return zahl + pAndereZahl;
		//*ml
	}
}
``

Dann erzeugt `jml` diese Ordnerstruktur in `pfad/zum/ausgabeordner`

```
pfad/zum/ausgabeordner/
├── Basisprojekt/
│   └── Beispiel.java
└── Basisprojekt_ML/
	└── Beispiel.java
```

Inhalt von `Basisprojekt_ML/Beispiel.java`:

```java

    class Beispiel {
        private int zahl;

        public int add( int pAndereZahl ) {
            return zahl + pAndereZahl;
        }
    }

Inhalt von `Basisprojekt/Beispiel.java`:

```java
class Beispiel {
	// TODO: Erstelle eine Objektvariable "zahl" vom Typ int

	public int add( int pAndereZahl ) {
		// TODO: Gib die Summe aus der Objektvariablen "zahl" und "pAndereZahl" zurück.
		return 0;
	}
}
```

### Mehrere Versionen

Als Standard wird wie oben nur die Projektversion `0` erstellt. `jml` kann aber auch mehrere Projekte erstellen, wenn die Aufgaben-Markierungen mit einer entsprechenden Nummer versehen werden.

Angenommen die `Beispiel.java` von oben sieht so aus:

```java
class Beispiel {
	/*aufg*
	// TODO: Erstelle eine Objektvariable "zahl" vom Typ int
	*aufg*/
	//ml*
	private int zahl;
	//*ml

	public int add( int pAndereZahl ) {
		/*aufg*
		// TODO: Gib die Summe aus der Objektvariablen "zahl" und "pSummand" zurück.
		return 0;
		*aufg*/
		//ml*
		return zahl + pAndereZahl;
		//*ml
	}

	/*aufg* 2
	public int sub( int pAndereZahl ) {
		// TODO: Gib die Differenz aus der Objektvariablen "zahl" und "pSummand" zurück.
		return 0;
	}
	*aufg*/

}
```

Dann werden statt der Version `0` die Projektversionen `1` und `2` erzeugt, da im zweiten Aufgaben-Marker eine konkrete Versionsnummer angegeben wurde:

```
pfad/zum/ausgabeordner/
├── Basisprojekt_1/
│   └── Beispiel.java
├── Basisprojekt_2/
│   └── Beispiel.java
└── Basisprojekt_ML/
	└── Beispiel.java
```

Es ist auch möglich eine Markierung für mehrere Projektversionen zu nutzen:

```java
/*aufg* >1
// Taucht nur in Projektversionen nach Version 1 auf.
*aufg*/

/*aufg* !=2
// Taucht in allen Projektversionen außer 2 auf.
*aufg*/

/*aufg* <=2
// Taucht nur in Projektversionen 1 und 2 auf.
*aufg*/
```

Seit Version 0.3.4 ist es möglich, auch einem Lösungs-Tag eine Versionsnummer wie
für Aufgaben zu geben. Dadurch wird der Inhalt zusätzlich zur Musterlösung auch in
den spezifizierten Aufgabenversionen gesetzt:

```java
//ml* >1
// Taucht in der Musterlösung und Versionen größer 1 auf
//*ml
```


## Optionen

Die Funktion von `jml` ist durch eine Vielzahl von Optionen anpassbar. Die Optionen können als Kommandozeilen-Argumente übergeben, oder in Konfigurationsdateien gespeichert werden.

Eine Übersicht der verfügbaren Kommandozeilen-Argumente ist mit `-h` abrufbar

```console
$ jml -h
```

Alle Optionen (und noch eine Handvoll mehr) lassen sich auch in einer von mehreren Konfigurationsdateien festlegen. `jml` sucht dazu bei jedem Start nach `.jml` Dateien im Basisprojekt, im Wurzelverzeichnis (`--project-root`) und im Home-Ordner des angemeldeten Nutzers (`~/.jml`).

Die Konfigurationen werden dann in umgekehrter Reihenfolge geladen, die Einstellungen im Basisprojekt haben also die höchste Priorität. Sie werden nur noch von Kommandozeilen-Argumente überschrieben.

Für das Beispiel oben könnte der Aufbau so aussehen::
```
~/
├── .config/jml.toml
├── pfad/zur/wurzel/
│   ├── jml.toml
│   └── Basisprojekt/
│       ├── jml.toml
│       └── Beispiel.java
└── pfad/zum/ausgabeordner
```

Inhalt von `~/.config/jml.toml`:

```toml
[tasks]
open = "/*<aufgabe>"
close = "</aufgabe>*/"
[solutions]
open = "//<loesung>"
close = "//</loesung>"
```

Inhalt von `~/pfad/zur/wurzel/jml.toml`:

```toml
name_format = {project}-{version}

[sources]
include = *.java,*.txt

[solutions]
suffix = "Loesung"

[zip]
create = true
```

Inhalt von `~/pfad/zur/wurzel/Basisprojekt/jml.toml`:

```toml
name = Maeusekampf

[sources]
encoding = iso-8859-1

[tasks]
open=/*aufgabe*
close=*aufgabe*/
```

Der Aufruf von `jml` sieht dann so aus:

```console
$ jml --project-root "~/pfad/zur/wurzel" "~/pfad/zur/wurzel/Basisprojekt"  --out "pfad/zum/ausgabeordner"
```

`jml` lädt nun zunächst `~/.config/jml.toml` und setzt die Start- und Endmarkierungen auf eine XML-Variante.

Danach wird `~/pfad/zur/wurzel/jml.toml` geladen, da dies per `--project-root` Argument als Wurzelverzeichnis gesetzt wurde. Für diese Projektgruppe werden ZIP-Dateien der Projektversionen erzeugt, außerdem wird das Suffix für die Musterlösung von `ML` auf `Loesung` geändert. Das Format der Projektnamen wird angepasst (`_` durch `-` ersetzt) und es werden auch `.txt` Dateien nach den Aufgaben- und Lösungs-Markierungen durchsucht.

Als drittes wird `~/pfad/zur/wurzel/Basisprojekt/jml.toml` geladen. Hier werden speziell für dieses eine Projekt die Aufgaben-Marker erneut verändert und die Datei-Codierung auf `iso-8859-1` (statt `utf-8`) festgelegt. Schließlich wird noch der Projektname auf `Maeusekampf` geändert, anstatt den Ordnernamen `Basisprojekt` zu verwenden.

Die Ausgabe sieht dann so aus (sofern die Aufgaben- und Lösungs-Markierungen in `Beispiel.java` angepasst wurden):
```
~/
├── .jml
├── pfad/zur/wurzel/
│   ├── .jml
│   └── Basisprojekt/
│       ├── .jml
│       └── Beispiel.java
└── pfad/zum/ausgabeordner/
	├── Maeusekampf-Loesung/
	│   └── Beispiel.java
	├── Maeusekampf-1/
	│   └── Beispiel.java
	├── Maeusekampf-2/
	│   └── Beispiel.java
	├── Maeusekampf-Loesung.zip
	├── Maeusekampf-1.zip
	└── Maeusekampf-2.zip
```
