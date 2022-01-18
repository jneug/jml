=======================
Java Musterlösung (jml)
=======================

Java Musterlösung (kurz ``jml``) ist ein kleines Skript mit dem mehrere Projektversionen aus einer Musterlösung generiert werden können.

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

``jml`` kann auch ohne ``pip`` einfach als Skriptdatei genutzt werden. Dazu die aktuelle Version der Datei [jml.py](https://github.com/jneug/jml/blob/main/src/jml/jml.py) aus dem Repository kopieren und auf der Festplatte speichern. Das Skript kann dann mit Python 3 ausgeführt werden:

.. code-block:: console

   $ python3 jml.py --version
   jml, version 0.2.2


Benutzung
=========

``jml`` benötigt im einfachsten Fall den Pfad des Basisprojektes und den Pfad des Ausgabeordners:

.. code-block:: console

   $ jml ProjektOrdner pfad/zum/ausgabeordner

Nach Ausführung befinden sich in ``pfad/zum/ausgabeordner`` die Musterlösung und die Projektversionen.

Die Inhalte und Anzahl an Versionen werden durch die Inhalte der Dateien im Projektordner bestimmt.

Angenommen in ``ProjektOrdner`` liegt eine Datei mit dem Namen ``Example.java`` mit folgendem Inhalt:

.. code-block:: java

    class Example {
        /*aufg*
        // TODO: Erstelle eine Objektvariable "zahl" vom Typ int
        *aufg*/
        //ml*
        private int zahl;
        //*ml

        public int add( int pSummand ) {
            /*aufg*
            // TODO: Gib die Summe aus der Objektvariablen "zahl" und "pSummand" zurück.
            return 0;
            *aufg*/
            //ml*
            return zahl + pSummand;
            //*ml
        }
    }

Dann erzeugt ``jml`` diese Ordnerstruktur in ``pfad/zum/ausgabeordner``:

.. code-block:: plain

    ProjektOrdner_ML
    |- Example.java
    ProjektOrdner
    |- Example.java

Inhalt von ``ProjektOrdner_ML/Example.java``:

.. code-block:: java

    class Example {
        private int zahl;

        public int add( int pSummand ) {
            return zahl + pSummand;
        }
    }

Inhalt von ``ProjektOrdner/Example.java``:

.. code-block:: java

    class Example {
        // TODO: Erstelle eine Objektvariable "zahl" vom Typ int

        public int add( int pSummand ) {
            // TODO: Gib die Summe aus der Objektvariablen "zahl" und "pSummand" zurück.
            return 0;
        }
    }
