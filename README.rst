=======================
Java Musterlösung (jml)
=======================

Java Musterlösung (kurz ``jml``) ist ein kleines Skript mit dem mehrere Projektversionen aus einer Musterlösung generiert werden können.

Motivation
==========

Zur Differenzierung im Informatikunterricht erstelle ich gerne mehrere Projektversionen mit mehr oder weniger Hilfestellungen, um dem Leistungsstand der Schülerinnen und Schüler besser gerecht zu werden. Inklusive einer Musterlösung können so schnell drei bis vier Projektversionen entstehen, die parallel weiterentwickelt werden müssen.

Befindet sich ein Fehler im Code, sollen die Aufgaben angepasst werden oder hat sich einfach ein Rechtschreibfehler in einen Kommentar eingeschlichen, müssen alle Projektversionen angepasst werden. Dabei habe ich schnell mal eine Version vergessen oder einen neuen Fehler eingebaut.

Vor einigen Jahren habe ich den Prozess mit ``jml`` vereinfacht. Das Skript generiert aus einer Basisversion, die mit Markierungen für Aufgaben und Lösungen versehen ist, die verschiedenen Projektversionen, dei für den Unterricht nötig sind. Anpassungen sind nur noch im Basisprojekt notwendig.

Installation
============

Die Installation wird wie gewohnt mit pypi durchgeführt:

.. code-block:: console

   $ pip3 install jml

Bei erfolgreicher Installation ist nun das ``jml`` Kommando verfügbar.

.. code-block:: console

   $ jml --version
   jml, version 0.2.2


Manuelle Installation
---------------------

jml kann auch ohne pip einfach als Skriptdatei genutzt werden. Dazu die aktuelle Version der Datei [jml.py]() aus dem Repository kopieren und auf der Festplatte speichern.
