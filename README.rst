=======================
Java Musterlösung (jml)
=======================

.. image:: https://github.com/jneug/jml/raw/main/jml.png
    :width: 60%
    :align: center

Java Musterlösung (kurz ``jml``) ist ein kleines Skript mit dem mehrere Projektversionen aus einer Musterlösung generiert werden können.

``jml`` wurde ursprünglich für Java-Projekte entwickelt, kann aber durch diverse Optionen auch für andere Projekte genutzt werden.

Motivation
----------

Zur Differenzierung im Informatikunterricht erstelle ich gerne mehrere Projektversionen mit mehr oder weniger Hilfestellungen, um dem Leistungsstand der Schülerinnen und Schüler besser gerecht zu werden. Inklusive einer Musterlösung können so schnell drei bis vier Projektversionen entstehen, die parallel weiterentwickelt werden müssen.

Befindet sich ein Fehler im Code, sollen die Aufgaben angepasst werden oder hat sich einfach ein Rechtschreibfehler in einen Kommentar eingeschlichen, müssen alle Projektversionen angepasst werden. Dabei habe ich schnell mal eine Version vergessen oder einen neuen Fehler eingebaut.

Vor einigen Jahren habe ich den Prozess mit ``jml`` vereinfacht. Das Skript generiert aus einer Basisversion, die mit Markierungen für Aufgaben und Lösungen versehen ist, die verschiedenen Projektversionen, die für den Unterricht nötig sind. Anpassungen sind nur noch im Basisprojekt notwendig.

Beispiele zur Verwendung finden sich in `meinen Projekt-Repository`_ und den
dazugehörigen `Projektversionen`_.

.. _meinen Projekt-Repository: http://github.com/jneug/schule-projekte
.. _Projektversionen: http://github.com/jneug/schule-versionen

Installation
------------

Die Installation wird wie gewohnt mit pip durchgeführt:

.. code-block:: console

   $ pip3 install jml

Bei erfolgreicher Installation ist nun das ``jml`` Kommando verfügbar.

.. code-block:: console

   $ jml --version
   jml, version 0.4.3

`jml` benötigt Python 3.8 oder neuer.

Manuelle Installation
^^^^^^^^^^^^^^^^^^^^^

``jml`` kann auch ohne ``pip`` einfach als Skriptdatei genutzt werden. Es werden keine externen Abhängigkeiten genutzt. Dazu die aktuelle Version der Datei `jml.py <https://github.com/jneug/jml/blob/main/src/jml/jml.py>`_ aus dem Repository kopieren und auf der Festplatte speichern. Das Skript kann dann mit Python 3 ausgeführt werden:

.. code-block:: console

   $ python3 jml.py --version
   jml, version 0.4.3


Benutzung
---------

``jml`` benötigt im einfachsten Fall den Pfad des Basisprojektes und den Pfad des Ausgabeordners:

.. code-block:: console

   $ jml pfad/zum/Basisprojekt --out pfad/zum/ausgabeordner

Nach Ausführung befinden sich in ``pfad/zum/ausgabeordner`` die Musterlösung und die Projektversionen.

Die Inhalte und Anzahl an Versionen werden durch die Inhalte der Dateien im Basisprojekt bestimmt.

Angenommen in ``Basisprojekt`` liegt eine Datei mit dem Namen ``Beispiel.java`` mit folgendem Inhalt:

.. code-block:: java

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

Dann erzeugt ``jml`` diese Ordnerstruktur in ``pfad/zum/ausgabeordner``::

    pfad/zum/ausgabeordner/
    ├── Basisprojekt/
    │   └── Beispiel.java
    └── Basisprojekt_ML/
        └── Beispiel.java

Inhalt von ``Basisprojekt_ML/Beispiel.java``:

.. code-block:: java

    class Beispiel {
        private int zahl;

        public int add( int pAndereZahl ) {
            return zahl + pAndereZahl;
        }
    }

Inhalt von ``Basisprojekt/Beispiel.java``:

.. code-block:: java

    class Beispiel {
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

Dann werden statt der Version ``0`` die Projektversionen ``1`` und ``2`` erzeugt, da im zweiten Aufgaben-Marker eine konkrete Versionsnummer angegeben wurde::

    pfad/zum/ausgabeordner/
    ├── Basisprojekt_1/
    │   └── Beispiel.java
    ├── Basisprojekt_2/
    │   └── Beispiel.java
    └── Basisprojekt_ML/
        └── Beispiel.java

Es ist auch möglich eine Markierung für mehrere Projektversionen zu nutzen:

.. code-block:: java

    /*aufg* >1
    // Taucht nur in Projektversionen nach Version 1 auf.
    *aufg*/

    /*aufg* !=2
    // Taucht in allen Projektversionen außer 2 auf.
    *aufg*/

    /*aufg* <=2
    // Taucht nur in Projektversionen 1 und 2 auf.
    *aufg*/

Seit Version 0.3.4 ist es möglich, auch einem Lösungs-Tag eine Versionsnummer wie
für Aufgaben zu geben. Dadurch wird der Inhalt zusätzlich zur Musterlösung auch in
den spezifizierten Aufgabenversionen gesetzt:

.. code-block:: java

    //ml* >1
    // Taucht in der Musterlösung und Versionen größer 1 auf
    //*ml


Optionen
--------

Die Funktion von ``jml`` ist durch eine Vielzahl von Optionen anpassbar. Die Optionen können als Kommandozeilen-Argumente übergeben, oder in Konfigurationsdateien gespeichert werden.

Eine Übersicht der verfügbaren Kommandozeilen-Argumente ist mit ``-h`` abrufbar

.. code-block:: console

   $ jml -h

Alle Optionen (und noch eine Handvoll mehr) lassen sich auch in einer von mehreren Konfigurationsdateien festlegen. ``jml`` sucht dazu bei jedem Start nach ``.jml`` Dateien im Basisprojekt, im Wurzelverzeichnis (``--project-root``) und im Home-Ordner des angemeldeten Nutzers (``~/.jml``).

Die Konfigurationen werden dann in umgekehrter Reihenfolge geladen, die Einstellungen im Basisprojekt haben also die höchste Priorität. Sie werden nur noch von Kommandozeilen-Argumente überschrieben.

Für das Beispiel oben könnte der Aufbau so aussehen::

    ~/
    ├── .jml
    ├── pfad/zur/wurzel/
    │   ├── .jml
    │   └── Basisprojekt/
    │       ├── .jml
    │       └── Beispiel.java
    └── pfad/zum/ausgabeordner

Inhalt von ``~/.jml``:

.. code-block:: ini

   [settings]
   task open=/*<aufgabe>
   task close=</aufgabe>*/
   solution open=//<loesung>
   solution close=//</loesung>

Inhalt von ``~/pfad/zur/wurzel/.jml``:

.. code-block:: ini

   [settings]
   zip = yes
   ml suffix = Loesung
   name format = {project}-{version}
   include = *.java,*.txt

Inhalt von ``~/pfad/zur/wurzel/Basisprojekt/.jml``:

.. code-block:: ini

   [settings]
   task open=/*aufgabe*
   task close=*aufgabe*/
   encoding = iso-8859-1
   name = Maeusekampf

Der Aufruf von ``jml`` sieht dann so aus:

.. code-block:: console

   $ jml --project-root "~/pfad/zur/wurzel" "~/pfad/zur/wurzel/Basisprojekt"  --out "pfad/zum/ausgabeordner"

``jml`` lädt nun zunächst ``~/.jml`` und setzt die Start- und Endmarkierungen auf eine XML-Variante.

Danach wird ``~/pfad/zur/wurzel/.jml`` geladen, da dies per ``--project-root`` Argument als Wurzelverzeichnis gesetzt wurde. Für diese Projektgruppe werden ZIP-Dateien der Projektversionen erzeugt, außerdem wird das Suffix für die Musterlösung von ``ML`` auf ``Loesung`` geändert. Das Format der Projektnamen wird angepasst (``_`` durch ``-`` ersetzt) und es werden auch ``.txt`` Dateien nach den Aufgaben- und Lösungs-Markierungen durchsucht.

Als drittes wird ``~/pfad/zur/wurzel/Basisprojekt/.jml`` geladen. Hier werden speziell für dieses eine Projekt die Aufgaben-Marker erneut verändert und die Datei-Codierung auf ``iso-8859-1`` (statt ``utf-8``) festgelegt. Schließlich wird noch der Projektname auf ``Maeusekampf`` festgelgt, anstatt den Ordnernamen ``Basisprojekt`` zu verwenden.

Die Ausgabe sieht dann so aus (sofern die Aufgaben- und Lösungs-Markierungen in ``Beispiel.java`` angepasst wurden)::

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

Liste der Optionen
^^^^^^^^^^^^^^^^^^

Die Tabelle zeigt eine Übersicht aller Optionen, die in einer Konfigurationsdatei oder per Kommandozeilen-Argument gesetzt werden können.

+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|  Optionsname in Konfigurationsdateien | Kommandozeilen-Argument | Beschreibung                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
+=======================================+=========================+========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================+
| output dir                            | -o / --out              | Legt den Zielordner für die Ausgabe der Projektversionen fest. Beachte, dass der finale Ausgabeordner unterhalb von ``outdir`` abhängig von ``--project-root`` noch variieren kann.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name                                  | -n / --name             | Setzt den Namen der erstellten Projektversionen. Im Namensformat wird ``{project}`` durch den Namen ersetzt. Als Standard wird der Ordnername des Basisprojektes verwendet.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name format                           | --name-format           | Legt das Format fest, nach dem die Projektversionen benannt werden. Der Wert ist ein Python-Formatierungsstring und kann die Variablen ``{project}``  für den Namen, ``{version}`` für die Versionsnummer und ``{date}`` für das aktuelle Datum enthalten. Auf diese Weise können Projekte beispielsweise mit einer Jahreszahl versehen werden (``name format = {date:%Y}_{project}-v{version}``). Standard ist ``{project}_{version}``.                                                                                                                                                                                                                                                                                                                                                                                                                               |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| task open                             | -to / --tag-open        | Setzt die Anfangsmarkierung für Aufgaben. Die Markierung sollte nach einem öffnenden Block-Kommentar stehen, damit die Aufgabenstellung in der Basisversion auskommentiert ist. Standard ist ``/*aufg*``.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| task close                            | -tc / --tag-close       | Setzt die Endmarkierung für Aufgaben. Die Markierung sollte vor einem schließenden Block-Kommentar stehen, damit die Aufgabenstellung in der Basisversion auskommentiert ist. Standard ist ``*aufg*/``.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| task comment prefix                   |                         | Diese Option erlaubt die Modifikation der Zeilen in einer Aufgabe. Wenn die Option auf eine Zeichenkette gesetzt wird, wird in jeder Zeile in einer Aufgabe das erste vorkommen der Zeichenkette entfernt. Auf diese Weise können Aufgaben auch für Programmiersprachen, die keine Blockkommentare unterstützen, aaskommentiert werden. ``task comment prefix = #`` würde zum Beispiel Zeilenkommentare in Python entfernen. Beginnt die Zeichenkette allerdings mit einem ``/``, dann wird in den fortgeschrittenen Modus geschaltet. Hier wird direkt ein regulärer Ausdruck und eine Ersetzung angegeben. Dazu muss der Wert das Format ``/regex/replace/`` haben. ``/`` muss durch ``\/`` maskiert werden. In jeder Zeile wird dann ``regex`` durch ``replace`` ersetzt. Details sind in der `Python Dokumentation zu regulären Ausdrücken`_ zu finden.            |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| solution open                         | -mlo / --ml-open        | Setzt die Anfangsmarkierung für Lösungen. Die Markierung sollte nach einem Zeilen-Kommentar stehen, damit die Musterlösung in der Basisversion lauffähig bleibt. Standard ist ``/ml*``.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| solution close                        | -mlc / --ml-close       | Setzt die Endmarkierung für Lösungen. Die Markierung sollte nach einem Zeilen-Kommentar stehen, damit die Musterlösung in der Basisversion lauffähig bleibt. Standard ist ``//*ml``.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| solution comment prefix               |                         | Wie ``task comment prefix`` für Lösungen.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| solution suffix                       | -mls / --ml-suffix      | Setzt die Versionsnummer der Musterlösung. Standard ist ``ML``.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| clear                                 | --no-clear              | Verhindert, dass die Ordner der Projektversionen zuerst vollständig gelöscht werden. Vorhandene Dateien werden dann überschrieben, aber Dateien, die nicht im Basisprojekt sind (oder in den Excludes stehen) werden nicht berührt und verbleiben in den Projektversionen.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| project root                          | --project-root          | Setzt das Wurzelverzeichnis, anhand dessen die Ordnerstruktur im Zielordner festgelegt wird. Das Verzeichnis sollte ein Elternverzeichnis des Basisprojektes sein. Im Wurzelverzeichnis wird außerdem nach einer ``.jml`` Datei gesucht, die vor der Konfigurationsdatei im Basisprojekt geladen wird.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| include                               | -i / --include          | Setzt die Liste der `Suchmuster für Dateien`_, in denen nach Aufgaben- und Lösungs-Markierungen gesucht werden soll. Standard ist ``*.java``.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| +include                              |                         | Auftauchen und ergänzt die Liste der Includes um weitere Suchmuster, anstatt sie zu ersetzen.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| -include                              |                         | Auftauchen und entfernt Suchmuster aus der Liste der Includes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| exclude                               | -e / --exclude          | Setzt die Liste der `Suchmuster für Dateien`_, die komplett ignoriert werden soll. Diese Dateien tauchen nicht in den Projektverisonen auf. Excludes haben Vorrang vor Includes. Standard ist ``*.class,*.ctxt,.DS_Store,Thumbs.db,.vscode,.eclipse,*.iml``.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| +exclude                              |                         | Ergänzt die Liste der Excludes um weitere Suchmuster, anstatt sie zu ersetzen.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| -exclude                              |                         | Entfernt Suchmuster aus der Liste der Excludes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| additional files                      |                         | Eine Liste von Dateien, die zusätzlich in alle Projektversionen kopiert werden sollen. Die Dateien werden nicht nach Markierungen durchsucht und exakt kopiert.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| +additional files                     |                         | Ergänzt die Liste der zusätzlichen Dateien um weitere Dateien, anstatt sie zu ersetzen.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| -additional files                     |                         | Entfernt Dateien aus der Liste der zusätzlichen Dateien.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                       | -v / --versions         | Liste von Versionsnummern von Projektversionen, die erstellt werden sollen. Bezieht sich nicht auf die Musterlösung. Diese kann mit ``--delete-ml`` abgestellt werden.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| encoding                              | --encoding              | Zeichenkodierung der Dateien. Standard ist ``utf-8``.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| delete empty files                    | --delete-empty          | Wenn gesetzt werden Dateien, die nach dem kompilieren keinen Inhalt mehr haben, nicht in die Projektversionen kopiert.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| create zip                            | -z / --zip              | Erstellt zu jeder Projektversion zusätzlich eine ZIP-Datei mit demselben Namen.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| create zip only                       |                         | Erstellt nur die ZIP-Dateien. Impliziert ``create zip = yes``.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| creat zip dir                         |                         | Ausgabeverzeichnis für die ZIP-Dateien, falls dieses von OUT abweicht. Standard ist dasselbe Verzeichnis wie für die Ausgabe der Projektversionen. (Also OUT bzw. ein Unterverzeichnis von OUT, wenn ein Wurzelverzeichnis angegeben wurde.)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| delete solution                       | --no-ml                 | Löscht die Musterlösung nach Ablauf des Programms. Unabhängig von dieser Einstellung wird die Musterlösung immer als erstes erstellt, um in den Dateien nach Aufgaben-Markierungen zu suchen und so die zu erstellenden Projektversionen zu ermitteln. Diese Einstellung löscht den Ordner der Musterlösung aber danach wieder. Es wird dann auch keine ZIP-Datei mehr erstellt.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                       | --debug                 | Schaltet die Debug-Ausgaben ein.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                       | --dry-run               | Schaltet den Debug-Modus ein und gibt alle Änderungen auf der Konsole aus. Es werden aber keine Ordner und Dateien erstellt. Mit dieser Option kann vor der Ausführung geprüft werden, ob die Konfiguration korrekt ist.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
+---------------------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. _Suchmuster für Dateien: https://docs.python.org/3/library/fnmatch.html
.. _Python Dokumentation zu regulären Ausdrücken: https://docs.python.org/3/library/re.html

Beispiele
^^^^^^^^^

Das folgende Beispiel kopiert die ``.class`` Dateien mit in die Projektversionen und ignoriert dafür einige ausgewählte ``.java`` Quelltexte. Dies kann sinnvoll sein, wenn das Projekt einige vordefinierte Klassen enthält (zum Beispiel eine fertige GUI), die von den Schüler:innen aber nicht bearbeitet werden sollen.

.. code-block:: text

    ~/
    ├── wurzel/verzeichnis/
    │   ├── .jml
    │   ├── files/
    │   │   ├── .gitignore
    │   │   └── package.bluej
    │   └── Basisprojekt/
    │       └── .jml
    └── ausgabe/ordner

Inhalt von ``~/wurzel/verzeichnis/.jml``:

.. code-block:: ini

    [settings]
    output dir = ~/ausgabe/ordner
    task open = /*<aufg>
    task close = </aufg>*/
    solution open = //<ml>
    solution close = //</ml>
    name format = {project}-v{version}
    create zip only = yes
    additional files = ~/wurzel/verzeichnis/files/.gitignore,
        ~/wurzel/verzeichnis/files/package.bluej

Inhalt von ``~/wurzel/verzeichnis/Basisprojekt/.jml``:

.. code-block:: ini

    project root = ~/wurzel/verzeichnis
    +exclude = MyMailGUI.java,MyMailSettingsGUI.java
    -exclude = *.class

Andere Sprachen
"""""""""""""""

Mit diesen Einstellungen kann ``jml`` zum Beispiel auch für ein HTML-Projekt genutzt werden:

.. code-block:: text

    ~/
    ├── wurzel/verzeichnis/
    │   ├── files/
    │   │   ├── .gitignore
    │   │   └── package.bluej
    │   └── Basisprojekt/
    │   │   ├── .jml
    │       └── index.html
    └── ausgabe/ordner

Inhalt von ``~/wurzel/verzeichnis/Basisprojekt/.jml``:

.. code-block:: ini

    [settings]
    task open = <!--aufg
    task close = /aufg-->
    solution open = <!--ml-->
    solution close = <!--/ml-->
    include = *.html,*.htm


Sprachen ohne Blockkommentare
"""""""""""""""""""""""""""""

Einige Programmiersprachen (wie Python oder TeX) besitzen keine
Block-, sondern nur Zeilenkommentare. Für diese Fälle gibt es die
Optionen ``task comment prefix`` und ``solution comment prefix``,
mit denen eine Zeichenkette festgelegt werden kann, die am Anfang
jeder Zeile entfernt wird.

.. code-block:: text

    ~/
    ├── wurzel/verzeichnis/
    │   ├── files/
    │   │   ├── .gitignore
    │   │   └── package.bluej
    │   └── Basisprojekt/
    │   │   ├── .jml
    │       └── beispiel.py
    └── ausgabe/ordner

Inhalt von ``~/wurzel/verzeichnis/Basisprojekt/.jml``:

.. code-block:: ini

    [settings]
    task open = # aufgb:
    task close = # aufg
    task comment prefix = #
    solution open = # ml:
    solution close = # ml
    include = *.py


Markdown Beispiel
"""""""""""""""""

Markdown-Dokumente besitzen in der Original-Syntax keine Kommentare, daher werden die Markierungen im Basisprojekt angezeigt. Auch die Aufgabenstellungen lassen sich dann nicht verstecken. Ansonsten funktioniert ˋjmlˋ ohne weiteres auch mit Markdown-Dateien.

Wird die Markdown-Datei in HTML konvertiert, dann wird nach Konverter werden aber auch HTML-Kommentare interpretiert und in der Ausgabe versteckt. Daher könnte dieselbe Konfiguration wie oben verwendet werden.

Das Beispiel zeigt eine Konfiguration, um aus einer Markdown-Datei zwei Arbeitsblätter mit Rechenaufgaben zu generieren.

.. code-block:: ini

    [settings]
    task open = <!--aufg
    task close = /aufg-->
    solution open = <!--ml-->
    solution close = <!--/ml-->
    include = *.md,*.mdown,*.markdown

.. code-block:: text

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


TeX Beispiel
""""""""""""""

Für TeX wird die Python-Konfiguration oben angepasst, so dass ˋ%ˋ als Kommentarzeichen interpretiert wird:

.. code-block:: ini

    [settings]
    task open = %\begin{aufg}
    task close = %\end{aufg}
    task comment prefix = %
    solution open = %\begin{ml}
    solution close = %\end{ml}
    include = *.tex

Eine andere Herangehensweise wäre es, im Kopf der TeX-Datei Umgebungen zu definieren, die den Inhalt beim Satz der Basisversion verstecken. Dieses Vorgehen kann z.B. für den Satz von Klassenarbeiten mit mehreren Varianten hilfreich sein.

.. code-block:: ini

    [settings]
    task open = \begin{jmlaufgabe}
    task close = \end{jmlaufgabe}
    solution open = \begin{jml}
    solution close = \end{jml}
    include = *.tex


Erweiterte Ersetzungen
""""""""""""""""""""""

``task comment prefix`` und ``solution comment prefix`` können auch in einem
erweiterten Modus genutzt werden. Wenn die Optionen auf einen Wert im Format::

    /regex/replace/

gesetzt wird, wird ``regex`` als regulärer Ausdruck benutzt und die erste
Fundstelle durch ``replace`` ersetzt. Dabei lassen sich auch Gruppen aus
``regex`` in ``replace`` mit ``\1``, ``\2``, usw. referenzieren.

Ein Slash ``/`` muss durch ``\/`` maskiert werden, wenn er in ``regex`` oder
``replace`` vorkommen soll.

Dieser Modus kann hilfreich sein, um komplexere Kommentar-Syntax oder ganz
andere Einsatzzwecke zu ermöglichen.

Diese ``.jml`` Datei würde die Aufgaben-Markierungen auf ein HTML-Format
ändern und innerhalb des Aufgaben-Blocks in jeder Zeile die Kommentare
entfernen, die ein ``TODO:`` enthalten.

.. code-block:: ini

    [settings]
    task open = <!--aufg start-->
    task close = <!--aufg end-->
    task comment prefix = /<!-- TODO: (.+) -->/\\1/

Zum Beispiel würde aus


.. code-block:: html

    <!--aufg start-->
    <!-- Füge hier deine Lösung ein -->
    <!-- TODO: <div></div> -->
    <!--aufg end-->

dann die Ausgabe

.. code-block:: html

    <!-- Füge hier deine Lösung ein -->
    <div></div>

Wie man sieht, bleibt der Kommentar ohne ``TODO:`` erhalten.


Integration in IDEs
-------------------

In Entwicklungsumgebungen wie `Eclipse`_, `IntelliJ`_ und `vscode`_ lässt
sich ``jml`` relativ einfach als externes Tool einbinden. Die IDEs erlauben
in der Regel die Verwendung von Platzhaltervariablen, mit denen der Aufruf
von ``jml`` angepasst werden kann.

.. _Eclipse: https://www.eclipse.org
.. _IntelliJ: https://www.jetbrains.com/idea/
.. _vscode: https://vscodium.com
