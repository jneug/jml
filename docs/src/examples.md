# Anwendungsbeispiele

Das folgende Beispiel kopiert die `.class` Dateien mit in die Projektversionen und ignoriert dafür einige ausgewählte `.java` Quelltexte. Dies kann sinnvoll sein, wenn das Projekt einige vordefinierte Klassen enthält (zum Beispiel eine fertige GUI), die von den Schüler:innen aber nicht bearbeitet werden sollen.

```
~/
├── wurzel/verzeichnis/
│   ├── .jml
│   ├── files/
│   │   ├── .gitignore
│   │   └── package.bluej
│   └── Basisprojekt/
│       └── .jml
└── ausgabe/ordner
```

Inhalt von `~/wurzel/verzeichnis/jml.toml`:

```toml
output_dir = "~/ausgabe/ordner"
name_format = "{project}-v{version}"

[tasks]
open = "/*<aufg>"
close = "</aufg>*/"
[solutions]
open = "//<ml>"
close = "//</ml>"
[zip]
only_zip = true

[[files]]
name = ".gitignore"
source = "~/wurzel/verzeichnis/files/.gitignore"
[[files]]
name = "package.bluej"
source = "~/wurzel/verzeichnis/files/package.bluej"
```

Inhalt von `~/wurzel/verzeichnis/Basisprojekt/jml.toml`:

```toml
project_root = "~/wurzel/verzeichnis"

[sources]
exclude = [
	"MyMailGUI.java", 
	"MyMailSettingsGUI.java" 
	"-*.class"
]
```

## Andere Sprachen

Mit diesen Einstellungen kann `jml` zum Beispiel auch für ein HTML-Projekt genutzt werden:

```
~/
├── wurzel/verzeichnis/
│   ├── files/
│   │   ├── .gitignore
│   │   └── package.bluej
│   └── Basisprojekt/
│   │   ├── .jml
│       └── index.html
└── ausgabe/ordner
```

Inhalt von `~/wurzel/verzeichnis/Basisprojekt/jml.toml`:

```toml
[tasks]
open = "<!--aufg"
close = "/aufg-->"
[solutions]
open = "<!--ml-->"
close = "<!--/ml-->"
[sources]
include = ["*.html", "*.htm", "-*.java"]
```

### Sprachen ohne Blockkommentare

Einige Programmiersprachen (wie Python oder TeX) besitzen keine
Block-, sondern nur Zeilenkommentare. Für diese Fälle gibt es die
Optionen `task.line.prefix` und `solutions.line.prefix`,
mit denen eine Zeichenkette festgelegt werden kann, die am Anfang
jeder Zeile entfernt wird.

```
~/
├── wurzel/verzeichnis/
│   ├── files/
│   │   ├── .gitignore
│   │   └── package.bluej
│   └── Basisprojekt/
│   │   ├── .jml
│       └── beispiel.py
└── ausgabe/ordner
```

Inhalt von `~/wurzel/verzeichnis/Basisprojekt/jml.toml`:

```toml
[tasks]
open = "# aufgb:"
close = "# aufg"
line.prefix = "#"
[solutions]
open = "# ml:"
close = "# ml"
[sources]
include = ["*.py"]
```

## Markdown Beispiel

Markdown-Dokumente besitzen in der Original-Syntax keine Kommentare, daher werden die Markierungen im Basisprojekt angezeigt. Auch die Aufgabenstellungen lassen sich dann nicht verstecken. Ansonsten funktioniert `jml` ohne weiteres auch mit Markdown-Dateien.

Wird die Markdown-Datei in HTML konvertiert, dann wird nach Konverter werden aber auch HTML-Kommentare interpretiert und in der Ausgabe versteckt. Daher könnte dieselbe Konfiguration wie oben verwendet werden.

Das Beispiel zeigt eine Konfiguration, um aus einer Markdown-Datei zwei Arbeitsblätter mit Rechenaufgaben zu generieren.

```toml
[tasks]
open = "<!--aufg"
close = "/aufg-->"
[solutions]
open = "<!--ml-->"
close = "<!--/ml-->"
[sources]
include = ["*.md","*.mdown","*.markdown"]
```

```md
# Kopfrechnen

## Aufgabe 1
<!--aufg 1
1. \[ 5+8\cdot 12 = \]
/aufg-->
<!--aufg 2
1.
/aufg-->
<!--ml-->
### Variante 1
1. \[ 5+8\cdot 12 = 101 \]

### Variante 2
<!--/ml-->

Weitere Aufgaben ...
```


## TeX Beispiel

Für TeX wird die Python-Konfiguration oben angepasst, so dass `%` als Kommentarzeichen interpretiert wird:

```toml
[tasks]
open = "%\\begin{aufg}"
close = "%\\end{aufg}"
line.prefix = "%"
[solutions]
open = "%\\begin{ml}"
close = "%\\end{ml}"
[sources]
include = ["*.tex"]

Eine andere Herangehensweise wäre es, im Kopf der TeX-Datei Umgebungen zu definieren, die den Inhalt beim Satz der Basisversion verstecken. Dieses Vorgehen kann z.B. für den Satz von Klassenarbeiten mit mehreren Varianten hilfreich sein.

```toml
[tasks]
open = "\\begin{jmlaufgabe}"
close = "\\end{jmlaufgabe}"
[solutions]
open = \begin{jml}
close = \end{jml}
[sources]
include = ["*.tex"]
```

## Erweiterte Ersetzungen

`task.line.prefix` und `solution.line.prefix` können auch zusammen mit 
den Optionen `task.line.replace` und `solutions.line.replace` genutzt werden, 
um das Prefix nicht einfach zu entfernen, sondern um eine eigene Ersetzung zu definieren.
Dabei lassen sich auch Gruppen aus `prefix` in `replace` mit `\1`, `\2`, usw. referenzieren.

Dieser Modus kann hilfreich sein, um komplexere Kommentar-Syntax oder ganz
andere Einsatzzwecke zu ermöglichen.

Diese `jml.toml` Datei würde die Aufgaben-Markierungen auf ein HTML-Format
ändern und innerhalb des Aufgaben-Blocks in jeder Zeile die Kommentare
entfernen, die ein `TODO:` enthalten:

```toml
[tasks]
open = "<!--aufg start-->"
close = "<!--aufg end-->"
line.prefix = "<!-- TODO: (.+) -->"
line.replace = "\\1"

Zum Beispiel würde aus


```html
<!--aufg start-->
<!-- Füge hier deine Lösung ein -->
<!-- TODO: <div></div> -->
<!--aufg end-->
```

dann die Ausgabe

```html
<!-- Füge hier deine Lösung ein -->
<div></div>
```

Wie man sieht, bleibt der Kommentar ohne `TODO:` erhalten.
