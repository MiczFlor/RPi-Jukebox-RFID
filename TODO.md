# TODO - Display Component and Related Improvements

Diese Liste enthaelt offene Punkte, die Schritt fuer Schritt angegangen werden sollen.

## 1. Worker-Thread-Event-Handling korrigieren

Datei: src/jukebox/components/display/__init__.py

Aktuell wird self._update_event.clear() noch innerhalb von self._pending_lock ausgefuehrt. Dadurch kann ein gerade eintreffendes Update, das _pending_status setzt und set() aufruft, sofort wieder geloescht werden.

Loesung: clear() ausserhalb des Locks aufrufen.

## 2. Ueberfluessige globale Variablen bereinigen

Datei: src/jukebox/components/display/__init__.py

- IS_ENABLED wird deklariert und in initialize() als global markiert, aber nirgendwo verwendet.
- CONFIG_FILE wird als global markiert, obwohl es nur lokal benoetigt wird.

Loesung: Entweder IS_ENABLED tatsaechlich nutzen oder entfernen. CONFIG_FILE nicht global deklarieren.

## 3. Repeat-Info-Typ konsistent machen

Datei: src/jukebox/components/display/__init__.py und src/jukebox/components/display/epd2in9b_V3.py

- _format_repeat() gibt leeren String oder Strings wie repeat_one / repeat_all zurueck.
- epd2in9b_V3.py definiert repeat_info: str = None.

Loesung: Einheitlichen Typ verwenden, z. B. str = '' statt str = None, oder absichtlich Optional[str].

## 4. Coverart-Information weiterreichen

Datei: src/jukebox/components/display/__init__.py

- _format_status() liest coverart aus dem Playerstatus.
- Der Key enthaelt coverart, aber display.show() bekommt coverart nicht uebergeben.

Loesung: Entscheiden, ob Coverart auf dem Display angezeigt werden soll. Falls ja:
- coverart an display.show() uebergeben.
- In epd2in9b_V3_image_factory.py / epd2in9b_V4_image_factory.py die Bilderzeugung erweitern.
- Falls nein: coverart aus _format_status() und dem Key entfernen.

## 5. Verhalten bei Stop definieren

Datei: src/jukebox/components/display/epd2in9b_V3.py und src/jukebox/components/display/epd2in9b_V4.py

- clear() ist aktuell leer mit dem Kommentar: E-Ink is to laty for clearing all the time, so keep it on display

Loesung: Beim Stop bleibt das letzte Bild stehen. Gewuenscht?
- Wenn ja: Dokumentieren.
- Wenn nein: Ein Standby-/Pause-Bild oder einen definierten Ruhezustand zeichnen.

## 6. Waveshare-Treiber nicht als Kopie im Repository halten

Betroffene Dateien: src/jukebox/components/display/waveshare_epd/* (ueber 70 Dateien)

- Die komplette Waveshare-EPD-Bibliothek ist ins Repository kopiert.
- Das blaeht das Projekt stark auf und erschwert Updates der Treiber.

Moegliche Loesungen:
- Waveshare-Bibliothek als Git-Submodule einbinden.
- Alternativ per pip / requirements.txt referenzieren, falls ein offizielles Paket existiert.
- Mindestens pruefen, ob alle 70 Treiberdateien wirklich benoetigt werden oder nur die fuer die unterstuetzten Displays (2.9 V3 / V4).

## 7. Weitere Tests ergaenzen

Datei: test/display/test_eink_displays.py

- Aktuell werden nur BMP-Bilder erzeugt und deren Groesse geprueft.
- Sinnvoll waeren zusatzliche Tests fuer:
  - _format_status()
  - _format_repeat()
  - _create_display() mit unbekanntem Display-Typ
  - Verhalten bei fehlender Konfiguration
