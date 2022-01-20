=======================
Java Musterlösung (jml)
=======================

Java Musterlösung (kurz ``jml``) ist ein kleines Skript mit dem mehrere Projektversionen aus einer Musterlösung generiert werden können.

``jml`` wurde ursprünglich für Java-Projekte entwickelt, kann aber durch diverse Optionen auch für andere Projekte genutzt werden.

Motivation
----------

Zur Differenzierung im Informatikunterricht erstelle ich gerne mehrere Projektversionen mit mehr oder weniger Hilfestellungen, um dem Leistungsstand der Schülerinnen und Schüler besser gerecht zu werden. Inklusive einer Musterlösung können so schnell drei bis vier Projektversionen entstehen, die parallel weiterentwickelt werden müssen.

Befindet sich ein Fehler im Code, sollen die Aufgaben angepasst werden oder hat sich einfach ein Rechtschreibfehler in einen Kommentar eingeschlichen, müssen alle Projektversionen angepasst werden. Dabei habe ich schnell mal eine Version vergessen oder einen neuen Fehler eingebaut.

Vor einigen Jahren habe ich den Prozess mit ``jml`` vereinfacht. Das Skript generiert aus einer Basisversion, die mit Markierungen für Aufgaben und Lösungen versehen ist, die verschiedenen Projektversionen, die für den Unterricht nötig sind. Anpassungen sind nur noch im Basisprojekt notwendig.

Installation
------------

Die Installation wird wie gewohnt mit pypi durchgeführt:

.. code-block:: console

   $ pip3 install jml

Bei erfolgreicher Installation ist nun das ``jml`` Kommando verfügbar.

.. code-block:: console

   $ jml --version
   jml, version 0.2.4

Manuelle Installation
^^^^^^^^^^^^^^^^^^^^^

``jml`` kann auch ohne ``pip`` einfach als Skriptdatei genutzt werden. Dazu die aktuelle Version der Datei `jml.py <https://github.com/jneug/jml/blob/main/src/jml/jml.py>`_ aus dem Repository kopieren und auf der Festplatte speichern. Das Skript kann dann mit Python 3 ausgeführt werden:

.. code-block:: console

   $ python3 jml.py --version
   jml, version 0.2.4


Benutzung
---------

``jml`` benötigt im einfachsten Fall den Pfad des Basisprojektes und den Pfad des Ausgabeordners:

.. code-block:: console

   $ jml pfad/zum/ProjektOrdner pfad/zum/ausgabeordner

Nach Ausführung befinden sich in ``pfad/zum/ausgabeordner`` die Musterlösung und die Projektversionen.

Die Inhalte und Anzahl an Versionen werden durch die Inhalte der Dateien im Projektordner bestimmt.

Angenommen in ``ProjektOrdner`` liegt eine Datei mit dem Namen ``Beispiel.java`` mit folgendem Inhalt:

.. code-block:: java

    class Example {
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

Dann erzeugt ``jml`` diese Ordnerstruktur in ``pfad/zum/ausgabeordner``::

    pfad/zum/ausgabeordner/
    ├── ProjektOrdner/
    │   └── Beispiel.java
    └── ProjektOrdner_ML/
        └── Beispiel.java

Inhalt von ``ProjektOrdner_ML/Beispiel.java``:

.. code-block:: java

    class Example {
        private int zahl;

        public int add( int pAndereZahl ) {
            return zahl + pAndereZahl;
        }
    }

Inhalt von ``ProjektOrdner/Beispiel.java``:

.. code-block:: java

    class Example {
        // TODO: Erstelle eine Objektvariable "zahl" vom Typ int

        public int add( int pAndereZahl ) {
            // TODO: Gib die Summe aus der Objektvariablen "zahl" und "pAndereZahl" zurück.
            return 0;
        }
    }


Mehrere Versionen
^^^^^^^^^^^^^^^^^

Als Standard wird wie oben nur die Projektversion ``0`` erstellt. ``jml`` kann aber auch mehrere Projekte erstellen, wenn die Aufgaben-Markierungen mit einer entsprechenden Nummer versehen werden.

Angenommen die ``Beispiel.java`` von oben sieht so aus:

.. code-block:: java

    class Example {
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

Dann wird werden statt der Version ``0`` die Projektversionen ``1`` und ``2`` erzeugt, da im zweiten Aufgaben-Marker eine konkrete Versionsnummer angegeben wurde::

    pfad/zum/ausgabeordner/
    ├── ProjektOrdner_1/
    │   └── Beispiel.java
    ├── ProjektOrdner_2/
    │   └── Beispiel.java
    └── ProjektOrdner_ML/
        └── Beispiel.java

Es ist auch möglich eine Markierung für mehrere Projektversionen zu nutzen:

.. code-block:: java

    /*aufg* >1
    // Taucht nur in Projektversionen nach Version 1 auf.
    *aufg*/

    /*aufg* !=2
    // Taucht in allen Projektversionen außer 2 auf.
    *aufg*/

    /*aufg* <= 2
    // Taucht nur in Projektversionen 1 und 2 auf.
    *aufg*/


Optionen
--------

Die Funktion von ``jml`` ist durch eine Vielzahl von Optionen anpassbar. Die Optionen können als Kommandozeilen-Argumente übergeben, oder in Konfigurationsdateien gespeichert werden.

Eine Übersicht der verfügbaren Kommandozeilen-Argumente ist mit ``-h`` abrufbar

.. code-block:: console

   $ jml -h

Alle Optionen (und noch eine Handvoll mehr) lassen sich auch in einer von mehreren Konfigurationsdateien festlegen. ``jml`` sucht dazu bei jedem Start nach ``.jml`` Dateien im Basisprojekt, im Gruppenverzeichnis (``--project-root``) und im Home-Ordner des angemeldeten Nutzers (``~/.jml``).

Die Konfigurationen werden dann in umgekehrter Reihenfolge geladen, die Einstellungen im Basisprojekt haben also die höchste Priorität. Sie werden nur noch von Kommandozeilen-Argumente überschrieben.

Für das Beispiel oben könnte der Aufbau so aussehen::

    ~/
    ├── .jml
    ├── pfad/zur/gruppe/
    │   ├── .jml
    │   └── ProjektOrdner/
    │       ├── .jml
    │       └── Beispiel.java
    └── pfad/zum/ausgabeordner

Inhalt von ``~/.jml``:

.. code-block:: ini

   [settings]
   opening tag=/*<aufgabe>
   closing tag=</aufgabe>*/
   opening ml tag=//<loesung>
   closing ml tag=//</loesung>

Inhalt von ``~/pfad/zur/gruppe/.jml``:

.. code-block:: ini

   [settings]
   zip = yes
   ml suffix = Loesung
   name format = {project}-{version}
   include = *.java,*.txt

Inhalt von ``~/pfad/zur/gruppe/ProjektOrdner/.jml``:

.. code-block:: ini

   [settings]
   opening tag=/*aufgabe*
   closing tag=*aufgabe*/
   encoding = iso-8859-1
   name = Maeusekampf

Der Aufruf von ``jml`` sieht dann so aus:

.. code-block:: console

   $ jml --project-root "~/pfad/zur/gruppe" "~/pfad/zur/gruppe/ProjektOrdner" "pfad/zum/ausgabeordner"

``jml`` lädt nun zunächst ``~/.jml`` und setzt die Start- und Endmarkierungen auf eine XML-Variante.

Danach wird ``~/pfad/zur/gruppe/.jml`` geladen, da dies per ``--project-root`` Argument als Gruppenverzeichnis gesetzt wurde. Für diese Projektgruppe werden ZIP-Dateien der Projektversionen erzeugt, außerdem wird das Suffix für die Musterlösung von ``ML`` auf ``Loesung`` geändert. Das Format der Projektnamen wird angepasst (``_`` durch ``-`` ersetzt) und es werden auch ``.txt`` Dateien nach den Aufgaben- und Lösungs-Markierungen durchsucht.

Als drittes wird ``~/pfad/zur/gruppe/ProjektOrdner/.jml`` geladen. Hier werden speziell für dieses eine Projekt die Aufgaben-Marker erneut verändert und die Datei-Codierung auf ``iso-8859-1`` (statt ``utf-8``) festgelegt. Schließlich wird noch der Projektname auf ``Maeusekampf`` festgelgt, anstatt den Ordnernamen ``ProjektOrdner`` zu verwenden.

Die Ausgabe sieht dann so aus (sofern die Aufgaben- und Lösungs-Markierungen in ``Beispiel.java`` angepasst wurden)::

    ~/
    ├── .jml
    ├── pfad/zur/gruppe/
    │   ├── .jml
    │   └── ProjektOrdner/
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

Liste der Optionen
^^^^^^^^^^^^^^^^^^

Die Tabelle zeigt eine Übersicht aller Optionen, die in einer Konfigurationsdatei gesetzt werden können und der dazugehörigen Kommandozeilen-Argumente.

+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Optionsname in Konfigurationsdateien  | Kommandozeilen-Argument  | Beschreibung                                                                                                                                                                                                                                                                                                                                                                                                                              |
+=======================================+==========================+===========================================================================================================================================================================================================================================================================================================================================================================================================================================+
| name                                  | -n / --name              | Setzt den Namen der erstellten Projektversionen. Im Namensformat wird ``{project}`` durch den Namen ersetzt. Als Standard wird der Ordnername des Basisprojektes verwendet.                                                                                                                                                                                                                                                               |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name format                           | --name-format            | Legt das Format fest, nach dem die Projektversionen benannt werden. Der Wert ist ein Python-Formatierungsstring und kann die Variablen ``{project}``  für den Namen, ``{version}`` für die Versionsnummer und ``{date}`` für das aktuelle Datum enthalten. Auf diese Weise können Projekte beispielsweise mit einer Jahreszahl versehen werden (``name format = {date:%Y}_{project}-v{version}``). Standard ist ``{project}_{version}``.  |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ml suffix                             | -mls / --ml-suffix       | Setzt die Versionsnummer der Musterlösung. Standard ist ``ML``.                                                                                                                                                                                                                                                                                                                                                                           |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| opening tag                           | -to / --tag-open         | Setzt die Anfangsmarkierung für Aufgaben. Die Markierung sollte nach einem öffnenden Block-Kommentar stehen, damit die Aufgabenstellung in der Basisversion auskommentiert ist. Standard ist ``/*aufg*``.                                                                                                                                                                                                                                 |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| closing tag                           | -tc / --tag-close        | Setzt die Endmarkierung für Aufgaben. Die Markierung sollte vor einem schließenden Block-Kommentar stehen, damit die Aufgabenstellung in der Basisversion auskommentiert ist. Standard ist ``*aufg*/``.                                                                                                                                                                                                                                   |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| opening ml tag                        | -mlo / --ml-open         | Setzt die Anfangsmarkierung für Lösungen. Die Markierung sollte nach einem Zeilen-Kommentar stehen, damit die Musterlösung in der Basisversion lauffähig bleibt. Standard ist ``/ml*``.                                                                                                                                                                                                                                                   |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| closing ml tag                        | -mlc / --ml-close        | Setzt die Endmarkierung für Lösungen. Die Markierung sollte nach einem Zeilen-Kommentar stehen, damit die Musterlösung in der Basisversion lauffähig bleibt. Standard ist ``//*ml``.                                                                                                                                                                                                                                                      |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| clear                                 | --no-clear               | Verhindert, dass die Ordner der Projektversionen zuerst vollständig gelöscht werden. Vorhandene Dateien werden dann überschrieben, aber Dateien, die nicht im Basisprojekt sind (oder in den Excludes stehen) werden nicht berührt und verbleiben in den Projektversionen.                                                                                                                                                                |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| project root                          | --project-root           | Setzt das Wurzelverzeichnis, anhand dessen die Ordnerstruktur im Zielordner festgelegt wird. Das Verzeichnis sollte ein Elternverzeichnis des Basisprojektes sein. Im Wurzelverzeichnis wird außerdem nach einer ``.jml`` Datei gesucht, die vor der Konfigurationsdatei im Basisprojekt geladen wird.                                                                                                                                    |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| include                               | -i / --include           | Setzt die Liste der `Suchmuster für Dateien`_, in denen nach Aufgaben- und Lösungs-Markierungen gesucht werden soll. Standard ist ``*.java``.                                                                                                                                                                                                                                                                                             |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| +include                              |                          | Kann nur in Konfigurationsdateien auftauchen und ergänzt die Liste der Includes um weitere Suchmuster, anstatt sie zu ersetzen.                                                                                                                                                                                                                                                                                                           |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| -include                              |                          | Kann nur in Konfigurationsdateien auftauchen und entfernt Suchmuster aus der Liste der Includes.                                                                                                                                                                                                                                                                                                                                          |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| exclude                               | -e / --exclude           | Setzt die Liste der `Suchmuster für Dateien`_, die komplett ignoriert werden soll. Diese Dateien tauchen nicht in den Projektverisonen auf. Excludes haben Vorrang vor Includes. Standard ist ``*.class,*.ctxt,.DS_Store,Thumbs.db,.vscode,.eclipse,*.iml``.                                                                                                                                                                              |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| +exclude                              |                          | Kann nur in Konfigurationsdateien auftauchen und ergänzt die Liste der Excludes um weitere Suchmuster, anstatt sie zu ersetzen.                                                                                                                                                                                                                                                                                                           |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| -exclude                              |                          | Kann nur in Konfigurationsdateien auftauchen und entfernt Suchmuster aus der Liste der Excludes.                                                                                                                                                                                                                                                                                                                                          |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| additional files                      |                          | Eine Liste von Dateien, die zusätzlich in alle Projektversionen kopiert werden sollen. Die Dateien werden nicht nach Markierungen durchsucht und exakt kopiert.                                                                                                                                                                                                                                                                           |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                       | -v / --versions          | Liste von Versionsnummern von Projektversionen, die erstellt werden sollen. Bezieht sich nicht auf dei Musterlösung. Diese kann mit ``--delete-ml`` abgestellt werden.                                                                                                                                                                                                                                                                    |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| encoding                              | --encoding               | Zeichenkodierung der Dateien. Standard ist ``utf-8``.                                                                                                                                                                                                                                                                                                                                                                                     |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| delete empty files                    | --delete-empty           | Wenn gesetzt werden Dateien, die nach dem kompilieren keinen Inhalt mehr haben, nicht in die Projektversionen kopiert.                                                                                                                                                                                                                                                                                                                    |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| create zip                            | -z / --zip               | Erstellt zu jeder Projektversion zusätzlich eine ZIP-Datei mit demselben Namen.                                                                                                                                                                                                                                                                                                                                                           |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| create zip only                       |                          | Erstellt nur die ZIP-Dateien. Impliziert ``create zip = yes``.                                                                                                                                                                                                                                                                                                                                                                            |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| creat zip dir                         |                          | Ausgabeverzeichnis für die ZIP-Dateien, falls dieses von OUT abweicht. Standard ist dasselbe Verzeichnis wie für die Ausgabe der Projektversionen. (Also OUT bzw. ein Unterverzeichnis von OUT, wenn ein Wurzelverzeichnis angegeben wurde.)                                                                                                                                                                                              |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| delete ml                             | --no-ml                  | Löscht die Musterlösung nach Ablauf des Programms. Unabhängig von dieser Einstellung wird die Musterlösung immer als erstes erstellt, um in den Dateien nach Aufgaben-Markierungen zu suchen und so die zu erstellenden Projektversionen zu ermitteln. Diese Einstellung löscht den Ordner der Musterlösung aber danach wieder. Es wird dann auch keine ZIP-Datei mehr erstellt.                                                          |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                       | --debug                  | Schaltet die Debug-Ausgaben ein.                                                                                                                                                                                                                                                                                                                                                                                                          |
+---------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. _Suchmuster für Dateien: https://docs.python.org/3/library/fnmatch.html

Beispiele
^^^^^^^^^

Das folgende Beispiel kopiert die ``.class`` Dateien mit in die Projektversionen und ignoriert dafür einige der ``.java`` Quelltexte. Dies kann sinnvoll sein, wenn das Projekt einige vordefinierte Klassen enthält (zum Beispiel eine fertige GUI), die von den Schüler:innen aber nicht bearbeitet werden sollen.

.. code-block:: text

    ~/
    ├── wurzel/verzeichnis/
    │   ├── .jml
    │   ├── files/
    │   │   ├── .gitignore
    │   │   └── package.bluej
    │   └── ProjektOrdner/
    │       └── .jml
    └── ausgabe/ordner

Inhalt von ``~/wurzel/verzeichnis/.jml``:

.. code-block:: ini

    [settings]
    opening tag = /*<aufg>
    closing tag = </aufg>*/
    opening ml tag = //<ml>
    closing ml tag = //</ml>
    name format = {project}-v{version}
    create zip only = yes
    additional files = ~/wurzel/verzeichnis/files/.gitignore,
        ~/wurzel/verzeichnis/files/package.bluej

Inhalt von ``~/wurzel/verzeichnis/ProjektOrdner.jml``:

.. code-block:: ini

    project root = ~/wurzel/verzeichnis
    +exclude = MyMailGUI.java,MyMailSettingsGUI.java
    -exclude = *.class


Mit diesen Einstellungen kann ``jml`` zum Beispiel mit auch für ein HTML-prjekt genutzt werden:

.. code-block:: text

    ~/
    ├── wurzel/verzeichnis/
    │   ├── .jml
    │   ├── files/
    │   │   ├── .gitignore
    │   │   └── package.bluej
    │   └── ProjektOrdner/
    │       └── .jml
    └── ausgabe/ordner

Inhalt von ``~/wurzel/verzeichnis/ProjektOrdner/.jml``:

.. code-block:: ini

    [settings]
    opening tag = <!--aufg
    closing tag = aufg-->
    opening ml tag = <!--ml
    closing ml tag = ml-->
    include = *.html,*.htm
