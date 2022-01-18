=======================
Java Musterlösung (jml)
=======================

Java Musterlösung (kurz ``jml``) ist ein kleines Skript mit dem mehrere Projektversionen aus einer Musterlösung generiert werden können.

``jml`` wurde ursprünglich für Java-Projekte entwickelt, kann aber durch diverse Optionen auch für andere Projekte genutzt werden.

Motivation
----------

Zur Differenzierung im Informatikunterricht erstelle ich gerne mehrere Projektversionen mit mehr oder weniger Hilfestellungen, um dem Leistungsstand der Schülerinnen und Schüler besser gerecht zu werden. Inklusive einer Musterlösung können so schnell drei bis vier Projektversionen entstehen, die parallel weiterentwickelt werden müssen.

Befindet sich ein Fehler im Code, sollen die Aufgaben angepasst werden oder hat sich einfach ein Rechtschreibfehler in einen Kommentar eingeschlichen, müssen alle Projektversionen angepasst werden. Dabei habe ich schnell mal eine Version vergessen oder einen neuen Fehler eingebaut.

Vor einigen Jahren habe ich den Prozess mit ``jml`` vereinfacht. Das Skript generiert aus einer Basisversion, die mit Markierungen für Aufgaben und Lösungen versehen ist, die verschiedenen Projektversionen, dei für den Unterricht nötig sind. Anpassungen sind nur noch im Basisprojekt notwendig.

Installation
------------

Die Installation wird wie gewohnt mit pypi durchgeführt:

.. code-block:: console

   $ pip3 install jml

Bei erfolgreicher Installation ist nun das ``jml`` Kommando verfügbar.

.. code-block:: console

   $ jml --version
   jml, version 0.2.2

Manuelle Installation
^^^^^^^^^^^^^^^^^^^^^

``jml`` kann auch ohne ``pip`` einfach als Skriptdatei genutzt werden. Dazu die aktuelle Version der Datei `jml.py <https://github.com/jneug/jml/blob/main/src/jml/jml.py>`_ aus dem Repository kopieren und auf der Festplatte speichern. Das Skript kann dann mit Python 3 ausgeführt werden:

.. code-block:: console

   $ python3 jml.py --version
   jml, version 0.2.2


Benutzung
=========

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

Dann erzeugt ``jml`` diese Ordnerstruktur in ``pfad/zum/ausgabeordner``:

.. code-block:: plain

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
-----------------

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

Dann wird werden statt der Version ``0`` die Projektversionen ``1`` und ``2`` erzeugt, da im zweiten Aufgaben-Marker eine konkrete Versionsnummer angegeben wurde.

.. code-block:: plain

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
========

Die Funktion von ``jml`` ist durch eine Vielzahl von Optionen anpassbar. Die Optionen können als Kommandozeilen-Argumente übergeben, oder in Konfigurationsdateien gespeichert werden.

Eine Übersicht der verfügbaren Kommandozeilen-Argumente ist mit ``-h`` abrufbar

.. code-block:: console

   $ jml -h

