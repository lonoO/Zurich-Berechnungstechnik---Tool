# Importiert das @dataclass-Dekorator-Tool zur einfachen Definition von Datenklassen
from dataclasses import dataclass

# Importiert Path für plattformunabhängige Dateipfade
from pathlib import Path

# Importiert date, um das aktuelle Datum für den Brief zu erzeugen
from datetime import date

# Importiert csv zum Einlesen/Schreiben der Vertragsdaten und Ergebnisse
import csv

# Importiert tkinter für die GUI
import tkinter as tk

# Importiert filedialog/messagebox für Dateiauswahl und Meldungen
from tkinter import filedialog, messagebox



# Datenmodell


# Datenklasse für einen Vertrag (eine Zeile in der contracts.txt)
@dataclass
class Vertrag:
    vertragsnr: int        # Vertragsnummer
    kundenname: str        # Kundenname
    jahreszins: float      # Jahreszins als Dezimalzahl (z.B. 0.02 für 2%)
    monatsbeitrag: float   # Monatlicher Beitrag
    monatskosten: float    # Monatliche Kosten
    startbetrag: float     # Startwert
    monate: int            # Anzahl Monate



# Mathe / Berechnung


# Umrechnung Jahreszins -> Monatszins: damit Monatsrechnung konsistent ist
def monatszins(jahreszins: float) -> float:
    # i = r / 12 (vereinfachtes Modell)
    return jahreszins / 12.0


# Update-Formel: Wert nach einem Monat:
def folgewert(v_t: float, beitrag: float, kosten: float, i: float) -> float:
    # Nettozufluss pro Monat
    # Kosten = Gebühren Verwaltung, Depot, Risiko usw.
    netto = beitrag - kosten

    
    return v_t * (1.0 + i) + netto


# Zeitreihe / Herz  (Monat 1..N) berechnen: Verlauf jeden Monat wird berechnet  
def berechne_zeitplan(v: Vertrag):
    i = monatszins(v.jahreszins)
    wert = v.startbetrag
    zeitplan = []

    # Einfache Plausibilitätschecks (praxisnah)
    if v.monate <= 0:
        raise ValueError("Monate müssen > 0 sein.")
    if v.startbetrag < 0:
        raise ValueError("Startbetrag darf nicht negativ sein.")
    if v.monatsbeitrag < 0 or v.monatskosten < 0:
        raise ValueError("Beitrag/Kosten dürfen nicht negativ sein.")

    # Schleife von 1 bis v.monate
    for m in range(1, v.monate + 1):
        # Wert ehemals Startbetrag wird zu folgewert bestehend aus:
        # aktuellem Wert + Monatsbeitrag - Monatskosten + Zinsen (i)
        wert = folgewert(wert, v.monatsbeitrag, v.monatskosten, i)

        if wert < 0:
            raise ValueError(f"Negativer Vertragswert bei Vertrag {v.vertragsnr} (Monat {m}).")
        
        # Liste Zeitplan bekommt über append Tupel angehängt
        # bps.: (2, 500.00) 
        zeitplan.append((m, round(wert, 2)))

    return zeitplan



# Import / Export


# Verträge aus TXT-Datei lesen
def import_vertraege_txt(path: Path):
    # Erwartete Header (muss exakt so heißen)
    expected = ["vertragsnr", "kundenname", "jahreszins", "monatsbeitrag", "monatskosten", "startbetrag", "monate"]
    vertraege = []

    # utf-8-sig
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")

        if reader.fieldnames is None:
            raise ValueError("Keine Header-Zeile gefunden (erste Zeile leer?).")

        # Header normalisieren (Leerzeichen entfernen)
        header = [h.strip() for h in reader.fieldnames]
        reader.fieldnames = header

        # Header prüfen
        if header != expected:
            raise ValueError(f"Header passt nicht.\nErwartet: {expected}\nBekommen: {header}")

        for row in reader:
            # Werte trimmen
            row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

            # Leere Werte abfangen
            for k in expected:
                if row.get(k) in (None, ""):
                    raise ValueError(f"Leerer Wert in Spalte '{k}' in Zeile: {row}")

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

    return vertraege


# Brieftext erzeugen
def erstelle_brief(v: Vertrag, endwert: float) -> str:
    heute = date.today().strftime("%d.%m.%Y")

    return (
        f"{heute}\n\n"
        f"Betreff: Vertragswertinformation – Vertrag {v.vertragsnr}\n\n"
        f"Sehr geehrte/r {v.kundenname},\n\n"
        f"der berechnete Vertragswert nach {v.monate} Monaten beträgt:\n\n"
        f"{endwert:.2f} EUR\n\n"
        f"Mit freundlichen Grüßen\n\n"
        f"Ihre Zurich Versicherung\n"
    )


# Ergebnisse schreiben: CSV + Briefe
def export_ergebnisse(vertraege, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    letters_dir = out_dir / "letters"
    letters_dir.mkdir(parents=True, exist_ok=True)

    results_path = out_dir / "results.csv"

    with results_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["vertragsnr", "kundenname", "endwert"])

        for v in vertraege:
            zeitplan = berechne_zeitplan(v)
            endwert = zeitplan[-1][1]
            writer.writerow([v.vertragsnr, v.kundenname, f"{endwert:.2f}"])

            brief = erstelle_brief(v, endwert)
            (letters_dir / f"brief_{v.vertragsnr}.txt").write_text(brief, encoding="utf-8")

    return results_path, letters_dir



# GUI


class ZurichApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Fenster-Setup
        self.title("Zurich Berechnungstechnik – Vertragswert Tool")
        self.geometry("920x520")

        # Zustände
        self.input_file: Path | None = None
        self.out_dir: Path | None = None
        self.vertraege = []

        # Layout
        self._build_ui()

    def _build_ui(self):
        # Oberer Bereich: Dateipfade
        frame_top = tk.Frame(self)
        frame_top.pack(fill="x", padx=12, pady=10)

        # Eingabedatei Auswahl
        tk.Label(frame_top, text="Input (contracts.txt):").grid(row=0, column=0, sticky="w")
        self.lbl_input = tk.Label(frame_top, text="(keine Datei gewählt)", anchor="w")
        self.lbl_input.grid(row=0, column=1, sticky="we", padx=8)

        btn_input = tk.Button(frame_top, text="Datei wählen", command=self.choose_input)
        btn_input.grid(row=0, column=2, padx=6)

        # Output Ordner Auswahl
        tk.Label(frame_top, text="Output Ordner:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.lbl_out = tk.Label(frame_top, text="(kein Ordner gewählt)", anchor="w")
        self.lbl_out.grid(row=1, column=1, sticky="we", padx=8, pady=(8, 0))

        btn_out = tk.Button(frame_top, text="Ordner wählen", command=self.choose_out_dir)
        btn_out.grid(row=1, column=2, padx=6, pady=(8, 0))

        frame_top.grid_columnconfigure(1, weight=1)

        # Buttons
        frame_btns = tk.Frame(self)
        frame_btns.pack(fill="x", padx=12)

        self.btn_load = tk.Button(frame_btns, text="Daten laden", command=self.load_data)
        self.btn_load.pack(side="left")

        self.btn_run = tk.Button(frame_btns, text="Berechnen + Export", command=self.run_export, state="disabled")
        self.btn_run.pack(side="left", padx=8)

        self.btn_preview = tk.Button(frame_btns, text="Brief-Vorschau", command=self.preview_letter, state="disabled")
        self.btn_preview.pack(side="left")

        # Tabelle / Anzeige
        frame_mid = tk.Frame(self)
        frame_mid.pack(fill="both", expand=True, padx=12, pady=10)

        tk.Label(frame_mid, text="Geladene Verträge (Vorschau):").pack(anchor="w")
        self.txt_table = tk.Text(frame_mid, height=12)
        self.txt_table.pack(fill="both", expand=True, pady=6)

        # Log
        tk.Label(self, text="Log:").pack(anchor="w", padx=12)
        self.txt_log = tk.Text(self, height=6)
        self.txt_log.pack(fill="x", padx=12, pady=(0, 10))

    def log(self, msg: str):
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")

    def choose_input(self):
        path = filedialog.askopenfilename(
            title="contracts.txt auswählen",
            filetypes=[("Text/CSV", "*.txt *.csv"), ("Alle Dateien", "*.*")]
        )
        if path:
            self.input_file = Path(path)
            self.lbl_input.config(text=str(self.input_file))
            self.log(f"Input gesetzt: {self.input_file}")

    def choose_out_dir(self):
        path = filedialog.askdirectory(title="Output-Ordner auswählen")
        if path:
            self.out_dir = Path(path)
            self.lbl_out.config(text=str(self.out_dir))
            self.log(f"Output gesetzt: {self.out_dir}")

    def load_data(self):
        if not self.input_file:
            messagebox.showerror("Fehler", "Bitte zuerst eine contracts.txt auswählen.")
            return

        try:
            self.vertraege = import_vertraege_txt(self.input_file)
            self._render_table(self.vertraege)
            self.log(f"{len(self.vertraege)} Verträge geladen.")
            self.btn_run.config(state="normal")
            self.btn_preview.config(state="normal")
        except Exception as e:
            messagebox.showerror("Import-Fehler", str(e))
            self.log(f"IMPORT FEHLER: {e}")

    def _render_table(self, vertraege):
        self.txt_table.delete("1.0", "end")
        header = "vertragsnr | kundenname | jahreszins | monatsbeitrag | monatskosten | startbetrag | monate\n"
        self.txt_table.insert("end", header)
        self.txt_table.insert("end", "-" * 100 + "\n")
        for v in vertraege:
            line = f"{v.vertragsnr} | {v.kundenname} | {v.jahreszins} | {v.monatsbeitrag} | {v.monatskosten} | {v.startbetrag} | {v.monate}\n"
            self.txt_table.insert("end", line)

    def run_export(self):
        if not self.vertraege:
            messagebox.showerror("Fehler", "Keine Verträge geladen.")
            return
        if not self.out_dir:
            messagebox.showerror("Fehler", "Bitte zuerst einen Output-Ordner auswählen.")
            return

        try:
            results_path, letters_dir = export_ergebnisse(self.vertraege, self.out_dir)
            self.log(f"Export OK: {results_path}")
            self.log(f"Briefe OK: {letters_dir}")
            messagebox.showinfo("Fertig", f"Ergebnisse: {results_path}\nBriefe: {letters_dir}")
        except Exception as e:
            messagebox.showerror("Berechnungs-/Export-Fehler", str(e))
            self.log(f"EXPORT FEHLER: {e}")

    def preview_letter(self):
        if not self.vertraege:
            messagebox.showerror("Fehler", "Bitte zuerst Daten laden.")
            return

        # Nimmt einfach den ersten Vertrag als Vorschau
        v = self.vertraege[0]
        try:
            endwert = berechne_zeitplan(v)[-1][1]
            brief = erstelle_brief(v, endwert)

            win = tk.Toplevel(self)
            win.title(f"Brief-Vorschau – Vertrag {v.vertragsnr}")
            win.geometry("700x500")

            txt = tk.Text(win)
            txt.pack(fill="both", expand=True)
            txt.insert("end", brief)
        except Exception as e:
            messagebox.showerror("Vorschau-Fehler", str(e))
            self.log(f"VORSCHAU FEHLER: {e}")


# Programmstart
if __name__ == "__main__":
    app = ZurichApp()
    app.mainloop()
