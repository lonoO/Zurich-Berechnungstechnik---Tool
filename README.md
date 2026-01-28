# Zurich Berechnungstechnik – Vertragswert Tool (Python GUI)

Kleines Praxisprojekt (Werkstudenten-nah), inspiriert durch Aufgaben aus der Berechnungstechnik:
- Import von Vertragsdaten aus einer TXT-Datei
- Monatlich wiederkehrende Berechnung von Vertragswerten
- Plausibilitätschecks
- Export als CSV + automatische Erstellung von Kundenbriefen (TXT)
- GUI zur Bedienung (Tkinter)

## Features
- **Import**: `contracts.txt` (Semikolon-getrennt)
- **Berechnung**: Monatliche Fortschreibung des Vertragswerts
- **Export**:
  - `results.csv` (Endwert je Vertrag)
  - `letters/brief_<vertragsnr>.txt` (Brief je Vertrag)
- **GUI**:
  - Datei auswählen
  - Output-Ordner wählen
  - Daten laden
  - Berechnen + Export
  - Brief-Vorschau

## Datenformat (contracts.txt)
Die Datei muss eine Header-Zeile besitzen und Semikolon `;` als Trennzeichen verwenden.

Beispiel:
```txt
vertragsnr;kundenname;jahreszins;monatsbeitrag;monatskosten;startbetrag;monate
1;Max Mustermann;0.02;150;5;1000;12
2;Erika Musterfrau;0.015;200;7.5;2500;12
