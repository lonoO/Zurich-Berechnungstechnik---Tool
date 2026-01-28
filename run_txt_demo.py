# Importiert das @dataclass-Dekorator-Tool zur einfachen Definition von Datenklassen
from dataclasses import dataclass

# Importiert Path für plattformunabhängige Dateipfade
from pathlib import Path

# Importiert date, um das aktuelle Datum für den Brief zu erzeugen
from datetime import date

# Importiert das csv-Modul zum Einlesen und Schreiben von CSV/TXT-Dateien
import csv


# Ermittelt das Verzeichnis, in dem diese Python-Datei liegt
# Dadurch funktionieren relative Pfade unabhängig vom Startort
BASE_DIR = Path(__file__).resolve().parent

# Pfad zur Eingabedatei contracts.txt
DATA_FILE = BASE_DIR / "contracts.txt"

# Pfad zum Ausgabeordner
OUT_DIR = BASE_DIR / "output"

# Pfad zum Unterordner für die Briefe
LETTERS_DIR = OUT_DIR / "letters"


# -------------------------
# Datenmodell
# -------------------------

# Definiert eine Datenklasse für einen Versicherungsvertrag
# @dataclass erzeugt automatisch __init__, __repr__ etc.
@dataclass
class Vertrag:
    vertragsnr: int        # Vertragsnummer
    kundenname: str        # Name des Kunden
    jahreszins: float      # Jahreszins (z. B. 0.02 = 2 %)
    monatsbeitrag: float   # Monatlicher Beitrag
    monatskosten: float    # Monatliche Kosten
    startbetrag: float     # Anfangswert des Vertrags
    monate: int            # Anzahl der Monate für die Berechnung


# -------------------------
# Mathematische Funktionen
# -------------------------

# Berechnet den Monatszins aus dem Jahreszins
def monatszins(jahreszins: float) -> float:
    return jahreszins / 12.0


# Berechnet den nächsten Vertragswert auf Basis des aktuellen Werts
def folgewert(v_t: float, beitrag: float, kosten: float, i: float) -> float:
    # Nettozufluss = Beitrag minus Kosten
    netto = beitrag - kosten

    # Formel: V_(t+1) = V_t * (1 + i) + Netto
    return v_t * (1 + i) + netto


# Berechnet den kompletten Zeitplan der Vertragswerte
def berechne_zeitplan(v: Vertrag):
    # Monatszins berechnen
    i = monatszins(v.jahreszins)

    # Startwert setzen
    wert = v.startbetrag

    # Liste für Monatswerte
    zeitplan = []

    # Schleife über alle Monate
    for m in range(1, v.monate + 1):
        # Neuen Vertragswert berechnen
        wert = folgewert(wert, v.monatsbeitrag, v.monatskosten, i)

        # Plausibilitätsprüfung: Vertragswert darf nicht negativ sein
        if wert < 0:
            raise ValueError(f"Negativer Vertragswert bei Vertrag {v.vertragsnr}")

        # Monat und Wert speichern
        zeitplan.append((m, round(wert, 2)))

    # Zeitplan zurückgeben
    return zeitplan


# -------------------------
# Import der Vertragsdaten
# -------------------------

# Liest die Vertragsdaten aus einer TXT-Datei
def import_vertraege_txt(path: Path):
    # Liste für alle Verträge
    vertraege = []

    # Öffnet die Datei im Lese-Modus
    with path.open("r", encoding="utf-8") as f:
        # DictReader liest jede Zeile als Dictionary (Header → Wert)
        reader = csv.DictReader(f, delimiter=";")

        # Iteriert über alle Zeilen der Datei
        for row in reader:
            # Erstellt ein Vertrag-Objekt aus der Zeile
            vertraege.append(
                Vertrag(
                    vertragsnr=int(row["vertragsnr"]),
                    kundenname=row["kundenname"],
                    jahreszins=float(row["jahreszins"]),
                    monatsbeitrag=float(row["monatsbeitrag"]),
                    monatskosten=float(row["monatskosten"]),
                    startbetrag=float(row["startbetrag"]),
                    monate=int(row["monate"]),
                )
            )

    # Gibt die Liste der Verträge zurück
    return vertraege


# -------------------------
# Brief-Erstellung
# -------------------------

# Erstellt einen formellen Kundenbrief als Text
def erstelle_brief(v: Vertrag, endwert: float) -> str:
    # Aktuelles Datum im deutschen Format
    heute = date.today().strftime("%d.%m.%Y")

    # Rückgabe des vollständigen Brieftextes
    return (
        f"{heute}\n\n"
        f"Betreff: Vertragswertinformation – Vertrag {v.vertragsnr}\n\n"
        f"Sehr geehrte/r {v.kundenname},\n\n"
        f"der berechnete Vertragswert nach {v.monate} Monaten beträgt:\n\n"
        f"{endwert:.2f} EUR\n\n"
        f"Mit freundlichen Grüßen\n\n"
        f"Ihre Zurich Versicherung\n"
    )


# -------------------------
# Hauptprogramm
# -------------------------

def main():
    # Erstellt den Ausgabeordner, falls er noch nicht existiert
    OUT_DIR.mkdir(exist_ok=True)

    # Erstellt den Briefe-Ordner inklusive Elternordner
    LETTERS_DIR.mkdir(parents=True, exist_ok=True)

    # Importiert alle Verträge aus der TXT-Datei
    vertraege = import_vertraege_txt(DATA_FILE)

    # Öffnet die Ergebnisdatei zum Schreiben
    with (OUT_DIR / "results.csv").open("w", newline="", encoding="utf-8") as f:
        # CSV-Writer mit Semikolon als Trennzeichen
        writer = csv.writer(f, delimiter=";")

        # Header der Ergebnisdatei
        writer.writerow(["vertragsnr", "kundenname", "endwert"])

        # Verarbeitung jedes Vertrags
        for v in vertraege:
            # Zeitplan berechnen
            zeitplan = berechne_zeitplan(v)

            # Letzter Wert ist der Endwert
            endwert = zeitplan[-1][1]

            # Ergebnis in CSV schreiben
            writer.writerow([v.vertragsnr, v.kundenname, endwert])

            # Kundenbrief erzeugen
            brief = erstelle_brief(v, endwert)

            # Brief als TXT-Datei speichern
            (LETTERS_DIR / f"brief_{v.vertragsnr}.txt").write_text(brief, encoding="utf-8")

    # Abschlussmeldung
    print("Fertig. Ergebnisse und Briefe erstellt.")


# Startpunkt des Programms
# Dieser Block wird nur ausgeführt, wenn das Skript direkt gestartet wird
if __name__ == "__main__":
    main()
