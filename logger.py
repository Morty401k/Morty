"""
Simulatore di Audit - logger.py
Registra tutte le azioni di Simulatore di Audit con timestamp.
Ottimizzato per Raspberry Pi Zero 2 W (512MB RAM):
- scrive direttamente su file, niente buffer in memoria
- rotazione automatica del log se supera 5MB
"""

import os
import json
from datetime import datetime


# ─── Configurazione ───────────────────────────────────────────────
CARTELLA_LOG  = "logs"
DIMENSIONE_MAX = 5 * 1024 * 1024  # 5MB max per file di log


# ─── Classe principale ─────────────────────────────────────────────

class Logger:
    def __init__(self, nome_sessione=None, cartella=None):
        """
        Inizializza il logger.
        cartella: percorso custom (es. /tmp/... per modalita RAM).
                  Se None usa la cartella di default logs/
        """
        cartella_log = cartella or os.environ.get("AUDIT_LOG_DIR", CARTELLA_LOG)
        os.makedirs(cartella_log, exist_ok=True)

        if nome_sessione is None:
            nome_sessione = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.nome_sessione = nome_sessione
        self.percorso_log  = os.path.join(cartella_log, f"audit_{nome_sessione}.log")
        self.percorso_json = os.path.join(cartella_log, f"audit_{nome_sessione}.json")
        self.eventi        = []  # lista leggera, svuotata dopo ogni flush

        self._scrivi_intestazione()

    def _scrivi_intestazione(self):
        """Scrive l'intestazione del file di log."""
        intestazione = (
            f"{'='*60}\n"
            f"  Simulatore di Audit - Sessione: {self.nome_sessione}\n"
            f"  Avvio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"{'='*60}\n\n"
        )
        with open(self.percorso_log, "w", encoding="utf-8") as f:
            f.write(intestazione)

    def _controlla_dimensione(self):
        """Ruota il file di log se supera DIMENSIONE_MAX."""
        if os.path.getsize(self.percorso_log) > DIMENSIONE_MAX:
            nuovo = self.percorso_log.replace(".log", "_old.log")
            os.rename(self.percorso_log, nuovo)
            self._scrivi_intestazione()

    def log(self, modulo, azione, dettagli="", livello="INFO"):
        """
        Registra un evento.

        Parametri:
          modulo   - chi ha generato l'evento (es. "scanner", "scenario")
          azione   - cosa è successo (es. "porta_aperta", "accesso_smb")
          dettagli - informazioni aggiuntive (stringa o dizionario)
          livello  - INFO | WARN | ALERT | ERRORE
        """
        timestamp = datetime.now().isoformat()

        # Formatta i dettagli se è un dizionario
        if isinstance(dettagli, dict):
            dettagli_str = json.dumps(dettagli, ensure_ascii=False)
        else:
            dettagli_str = str(dettagli)

        # Riga testuale per il .log
        riga = f"[{timestamp}] [{livello:6}] [{modulo:16}] {azione}"
        if dettagli_str:
            riga += f" | {dettagli_str}"
        riga += "\n"

        # Scrivi subito su file (niente buffer — sicuro su 512MB)
        self._controlla_dimensione()
        with open(self.percorso_log, "a", encoding="utf-8") as f:
            f.write(riga)

        # Mantieni anche struttura JSON in memoria (leggera)
        self.eventi.append({
            "timestamp": timestamp,
            "livello":   livello,
            "modulo":    modulo,
            "azione":    azione,
            "dettagli":  dettagli_str
        })

        # Stampa a schermo con colori ANSI
        colori = {
            "INFO":   "\033[0m",    # bianco
            "WARN":   "\033[93m",   # giallo
            "ALERT":  "\033[91m",   # rosso
            "ERRORE": "\033[95m"    # viola
        }
        reset = "\033[0m"
        colore = colori.get(livello, reset)
        print(f"{colore}{riga.strip()}{reset}")

    def flush_json(self):
        """
        Salva tutti gli eventi accumulati nel file JSON
        e svuota la lista in memoria.
        """
        if not self.eventi:
            return

        # Legge gli eventi già salvati (se il file esiste)
        esistenti = []
        if os.path.exists(self.percorso_json):
            with open(self.percorso_json, "r", encoding="utf-8") as f:
                try:
                    esistenti = json.load(f)
                except json.JSONDecodeError:
                    esistenti = []

        esistenti.extend(self.eventi)

        with open(self.percorso_json, "w", encoding="utf-8") as f:
            json.dump(esistenti, f, indent=2, ensure_ascii=False)

        self.eventi = []  # svuota memoria

    def chiudi(self):
        """Chiude la sessione e salva tutto."""
        self.flush_json()
        chiusura = (
            f"\n{'='*60}\n"
            f"  Fine sessione: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"{'='*60}\n"
        )
        with open(self.percorso_log, "a", encoding="utf-8") as f:
            f.write(chiusura)
        print(f"\n[✓] Log salvato in: {self.percorso_log}")
        print(f"[✓] JSON salvato in: {self.percorso_json}")


# ─── Scorciatoie per i livelli ─────────────────────────────────────

    def info(self, modulo, azione, dettagli=""):
        self.log(modulo, azione, dettagli, livello="INFO")

    def warn(self, modulo, azione, dettagli=""):
        self.log(modulo, azione, dettagli, livello="WARN")

    def alert(self, modulo, azione, dettagli=""):
        self.log(modulo, azione, dettagli, livello="ALERT")

    def errore(self, modulo, azione, dettagli=""):
        self.log(modulo, azione, dettagli, livello="ERRORE")


# ─── Test standalone ───────────────────────────────────────────────
if __name__ == "__main__":
    logger = Logger()

    logger.info("scanner",  "avvio_scansione",  "rete: 192.168.1.0/24")
    logger.info("scanner",  "dispositivo_trovato", {"ip": "192.168.1.10", "porte": [22, 80]})
    logger.warn("scenario", "accesso_smb",      {"ip": "192.168.1.10", "share": "\\\\docs"})
    logger.alert("scenario","esfiltrazione",    {"file": "report.pdf", "dimensione": "2.1MB"})
    logger.errore("scanner","timeout",          "IP 192.168.1.99 non raggiungibile")

    logger.chiudi()
