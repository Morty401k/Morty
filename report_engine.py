"""
Simulatore di Audit - report_engine.py
Genera il report PDF finale con i risultati dell'audit.
Usa FPDF2 (leggera) invece di ReportLab — ottimizzato per 512MB RAM.

Installazione: pip install fpdf2
"""

import json
import os
from datetime import datetime


# ─── Configurazione ───────────────────────────────────────────────
CARTELLA_REPORT = "reports"


# ─── Classe principale ─────────────────────────────────────────────

class ReportEngine:
    def __init__(self, nome_sessione, dispositivi, risultati_scenari, percorso_json_log=None):
        """
        Parametri:
          nome_sessione       - nome della sessione (es. "2024-03-15_10-22-00")
          dispositivi         - lista da scanner.py
          risultati_scenari   - lista da scenario_engine.py
          percorso_json_log   - (opzionale) percorso al file .json del logger
        """
        self.nome_sessione     = nome_sessione
        self.dispositivi       = dispositivi
        self.risultati         = risultati_scenari
        self.percorso_json_log = percorso_json_log
        self.data_report       = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        os.makedirs(CARTELLA_REPORT, exist_ok=True)
        self.percorso_pdf = os.path.join(
            CARTELLA_REPORT, f"simulatore_audit_report_{nome_sessione}.pdf"
        )

    def _calcola_statistiche(self):
        """Calcola le statistiche riassuntive dai risultati."""
        totale   = len(self.risultati)
        alert    = sum(1 for r in self.risultati if r.get("rilevabile"))
        scenari  = {}
        for r in self.risultati:
            s = r.get("scenario", "sconosciuto")
            scenari[s] = scenari.get(s, 0) + 1

        return {
            "totale_scenari":    totale,
            "scenari_rilevabili": alert,
            "scenari_non_rilevati": totale - alert,
            "per_tipo": scenari
        }

    def _colore_rischio(self, pdf, rilevabile):
        """Imposta il colore del testo in base al rischio."""
        if rilevabile:
            pdf.set_text_color(180, 30, 30)   # rosso — rilevato
        else:
            pdf.set_text_color(30, 130, 60)   # verde — non rilevato

    def genera_pdf(self):
        """Genera il report PDF completo."""
        try:
            from fpdf import FPDF
        except ImportError:
            print("[ERRORE] fpdf2 non installato. Esegui: pip install fpdf2")
            return None

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ── Intestazione ──────────────────────────────────────────
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, "Simulatore di Audit - Report di Audit", ln=True, align="C")

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 7, f"Sessione: {self.nome_sessione}", ln=True, align="C")
        pdf.cell(0, 7, f"Generato il: {self.data_report}", ln=True, align="C")
        pdf.ln(8)

        # Linea separatrice
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

        # ── Sezione 1: Riepilogo ──────────────────────────────────
        stats = self._calcola_statistiche()

        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 9, "1. Riepilogo esecutivo", ln=True)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 7,
            f"Dispositivi scansionati: {len(self.dispositivi)}\n"
            f"Scenari eseguiti totali: {stats['totale_scenari']}\n"
            f"Scenari con attivita rilevabile: {stats['scenari_rilevabili']}\n"
            f"Scenari non rilevati dai sistemi: {stats['scenari_non_rilevati']}"
        )
        pdf.ln(4)

        # Barra di rischio semplice
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "Livello di esposizione:", ln=True)
        pdf.set_font("Helvetica", "", 11)

        if stats["totale_scenari"] > 0:
            percentuale = stats["scenari_rilevabili"] / stats["totale_scenari"] * 100
        else:
            percentuale = 0

        if percentuale >= 75:
            livello, colore = "ALTO", (180, 30, 30)
        elif percentuale >= 40:
            livello, colore = "MEDIO", (200, 130, 0)
        else:
            livello, colore = "BASSO", (30, 130, 60)

        pdf.set_text_color(*colore)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, f"  {livello} ({percentuale:.0f}% degli scenari rilevabili)", ln=True)
        pdf.set_text_color(50, 50, 50)
        pdf.ln(4)

        # ── Sezione 2: Dispositivi trovati ────────────────────────
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 9, "2. Dispositivi rilevati in rete", ln=True)
        pdf.ln(2)

        if not self.dispositivi:
            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(0, 7, "  Nessun dispositivo trovato.", ln=True)
        else:
            # Intestazione tabella
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(45, 8, "IP", border=1, fill=True)
            pdf.cell(75, 8, "Hostname", border=1, fill=True)
            pdf.cell(70, 8, "Porte aperte", border=1, fill=True, ln=True)

            pdf.set_font("Helvetica", "", 10)
            for d in self.dispositivi:
                porte = ", ".join(str(p) for p in d.get("porte_aperte", []))
                pdf.set_text_color(50, 50, 50)
                pdf.cell(45, 7, d.get("ip", ""), border=1)
                pdf.cell(75, 7, d.get("hostname", "")[:35], border=1)
                pdf.cell(70, 7, porte[:35] if porte else "nessuna", border=1, ln=True)

        pdf.ln(6)

        # ── Sezione 3: Risultati scenari ──────────────────────────
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 9, "3. Risultati degli scenari", ln=True)
        pdf.ln(2)

        if not self.risultati:
            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(0, 7, "  Nessuno scenario eseguito.", ln=True)
        else:
            for i, r in enumerate(self.risultati, 1):
                scenario  = r.get("scenario", "sconosciuto").replace("_", " ").title()
                target    = r.get("target", "?")
                rilevabile = r.get("rilevabile", False)

                # Titolo scenario
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(30, 30, 30)
                pdf.cell(0, 8, f"  {i}. {scenario} — Target: {target}", ln=True)

                # Esito
                pdf.set_font("Helvetica", "", 10)
                self._colore_rischio(pdf, rilevabile)
                esito_testo = "RILEVABILE dai sistemi di sicurezza" if rilevabile \
                              else "Non rilevato — gap di sicurezza identificato"
                pdf.cell(0, 6, f"     Esito: {esito_testo}", ln=True)

                # Dettagli specifici per scenario
                pdf.set_text_color(80, 80, 80)
                if r.get("porte_aperte"):
                    pdf.cell(0, 6,
                        f"     Porte aperte: {', '.join(str(p) for p in r['porte_aperte'])}",
                        ln=True)
                if r.get("shares"):
                    pdf.cell(0, 6,
                        f"     Share SMB trovate: {len(r['shares'])}",
                        ln=True)
                if r.get("tentativi"):
                    pdf.cell(0, 6,
                        f"     Tentativi SSH: {len(r['tentativi'])}",
                        ln=True)
                pdf.ln(3)

        # ── Sezione 4: Raccomandazioni ────────────────────────────
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 9, "4. Raccomandazioni", ln=True)
        pdf.ln(2)

        raccomandazioni = [
            ("Monitoraggio traffico interno",
             "Implementare un IDS/IPS interno per rilevare scansioni di porte "
             "e accessi anomali alle risorse condivise."),
            ("Hardening SMB",
             "Disabilitare SMBv1, limitare l'accesso alle share solo agli utenti "
             "autorizzati e abilitare il logging degli accessi."),
            ("Politica password SSH",
             "Disabilitare il login SSH con password e usare solo chiavi crittografiche. "
             "Abilitare fail2ban per bloccare tentativi ripetuti."),
            ("DLP (Data Loss Prevention)",
             "Installare un sistema DLP per monitorare e bloccare trasferimenti "
             "di file non autorizzati verso l'esterno."),
            ("Audit periodici",
             "Eseguire Simulatore di Audit regolarmente (es. ogni trimestre) per verificare "
             "che le misure di sicurezza siano efficaci nel tempo."),
        ]

        for titolo, testo in raccomandazioni:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(0, 7, f"  • {titolo}", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 6, f"    {testo}")
            pdf.ln(2)

        # ── Piè di pagina ─────────────────────────────────────────
        pdf.ln(8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.multi_cell(0, 5,
            "Simulatore di Audit e' uno strumento di audit etico per uso su reti autorizzate. "
            "Questo report e' riservato e destinato esclusivamente al personale tecnico autorizzato."
        )

        # Salva PDF
        pdf.output(self.percorso_pdf)
        print(f"[✓] Report PDF generato: {self.percorso_pdf}")
        return self.percorso_pdf


# ─── Test standalone ───────────────────────────────────────────────
if __name__ == "__main__":
    # Dati fittizi per test
    dispositivi_test = [
        {"ip": "192.168.1.1",  "hostname": "router",    "porte_aperte": [80, 443]},
        {"ip": "192.168.1.10", "hostname": "pc-ufficio", "porte_aperte": [22, 445]},
    ]
    risultati_test = [
        {"scenario": "port_scan_silenzioso",    "target": "192.168.1.1",  "porte_aperte": [80, 443], "rilevabile": False},
        {"scenario": "smb_enumerazione",        "target": "192.168.1.10", "shares": ["docs", "backup"], "rilevabile": True},
        {"scenario": "ssh_credenziali_deboli",  "target": "192.168.1.10", "tentativi": 3, "successo": False, "rilevabile": True},
        {"scenario": "esfiltrazione_simulata",  "target": "192.168.1.1",  "inviato": False, "rilevabile": False},
    ]

    engine = ReportEngine(
        nome_sessione="test_2024-03-15",
        dispositivi=dispositivi_test,
        risultati_scenari=risultati_test
    )
    engine.genera_pdf()
