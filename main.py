"""
Simulatore di Audit - main.py
Entry point del progetto. Collega scanner, scenari, logger e report.

Utilizzo:
  sudo python3 main.py              # modalita' normale
  sudo python3 main.py --ram-mode   # nessuna traccia su disco (Tails)

IMPORTANTE: usare SOLO su reti di cui si e' proprietari o
su cui si ha esplicita autorizzazione scritta.
"""

import json
import os
import sys
import tempfile
from datetime import datetime

from logger          import Logger
from scanner         import esegui_scansione, salva_risultati
from scenario_engine import ScenarioEngine
from report_engine   import ReportEngine


# ─── Configurazione ───────────────────────────────────────────────
CONFIG_PATH = "config.json"

# Modalita' RAM: tutto in /tmp, nessuna traccia su disco
RAM_MODE = "--ram-mode" in sys.argv

CONFIG_DEFAULT = {
    "rete": None,           # None = rileva automaticamente
    "porte_extra": [],      # porte aggiuntive da scansionare
    "pausa_scenari": 3,     # secondi tra uno scenario e l'altro
    "telegram_token": "",   # token bot Telegram (opzionale)
    "telegram_chat_id": ""  # chat ID Telegram (opzionale)
}


# ─── Funzioni di supporto ──────────────────────────────────────────

def carica_config():
    """Carica config.json se esiste, altrimenti usa i valori default."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            try:
                config = json.load(f)
                # Unisce con i default per campi mancanti
                return {**CONFIG_DEFAULT, **config}
            except json.JSONDecodeError:
                print("[WARN] config.json non valido, uso configurazione default.")
    return CONFIG_DEFAULT.copy()


def invia_alert_telegram(token, chat_id, messaggio):
    """Invia un messaggio Telegram (opzionale)."""
    if not token or not chat_id:
        return
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        dati = json.dumps({
            "chat_id": chat_id,
            "text": messaggio,
            "parse_mode": "HTML"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=dati,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
        print("[✓] Alert Telegram inviato.")
    except Exception as e:
        print(f"[WARN] Telegram non disponibile: {e}")


def stampa_banner():
    print("""
  
 ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝
 ██║  ███╗███████║██║   ██║███████╗   ██║
 ██║   ██║██╔══██║██║   ██║╚════██║   ██║
 ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║
  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝
       █████╗ ██╗   ██╗██████╗ ██╗████████╗
      ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝
      ███████║██║   ██║██║  ██║██║   ██║
      ██╔══██║██║   ██║██║  ██║██║   ██║
      ██║  ██║╚██████╔╝██████╔╝██║   ██║
      ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝

  Simulatore di Insider Threat per Audit Etico
  Usare SOLO su reti autorizzate.
    """)


# ─── Main ──────────────────────────────────────────────────────────

def main():
    stampa_banner()

    # 1. Carica configurazione
    config = carica_config()
    nome_sessione = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Modalita RAM: reindirizza log e report in /tmp
    if RAM_MODE:
        tmp_dir = tempfile.mkdtemp(prefix="simulatore_audit_")
        os.environ["AUDIT_LOG_DIR"]    = os.path.join(tmp_dir, "logs")
        os.environ["AUDIT_REPORT_DIR"] = os.path.join(tmp_dir, "reports")
        print(f"[*] Modalita RAM attiva — nessuna traccia su disco")
        print(f"[*] Cartella temporanea: {tmp_dir}")
    else:
        tmp_dir = None

    print(f"[*] Sessione: {nome_sessione}\n")

    # 2. Inizializza logger
    log_dir = os.environ.get("AUDIT_LOG_DIR", "logs")
    logger = Logger(nome_sessione, cartella=log_dir)
    logger.info("main", "avvio", {"sessione": nome_sessione, "ram_mode": RAM_MODE})

    try:
        # 3. Scansione rete
        print("─" * 50)
        print("[FASE 1] Scansione della rete")
        print("─" * 50)
        logger.info("main", "fase_1_scanner", "avvio scansione rete")

        dispositivi = esegui_scansione(config.get("rete"))
        salva_risultati(dispositivi)

        logger.info("main", "fase_1_completata",
                    {"dispositivi_trovati": len(dispositivi)})

        if not dispositivi:
            print("\n[!] Nessun dispositivo trovato. Verifica la connessione di rete.")
            logger.warn("main", "nessun_dispositivo", "audit terminato")
            return

        # Alert Telegram — fase 1
        invia_alert_telegram(
            config["telegram_token"],
            config["telegram_chat_id"],
            f"🔍 <b>Simulatore di Audit</b> — Fase 1 completata\n"
            f"Dispositivi trovati: {len(dispositivi)}"
        )

        # 4. Esecuzione scenari
        print("\n" + "─" * 50)
        print("[FASE 2] Esecuzione scenari insider threat")
        print("─" * 50)
        logger.info("main", "fase_2_scenari", "avvio scenari")

        engine = ScenarioEngine(logger, dispositivi)
        risultati = engine.esegui_tutti()

        logger.info("main", "fase_2_completata",
                    {"scenari_eseguiti": len(risultati)})

        # Alert Telegram — fase 2
        alert_count = sum(1 for r in risultati if r.get("rilevabile"))
        invia_alert_telegram(
            config["telegram_token"],
            config["telegram_chat_id"],
            f"⚠️ <b>Simulatore di Audit</b> — Fase 2 completata\n"
            f"Scenari eseguiti: {len(risultati)}\n"
            f"Scenari rilevabili: {alert_count}"
        )

        # 5. Generazione report PDF
        print("\n" + "─" * 50)
        print("[FASE 3] Generazione report PDF")
        print("─" * 50)
        logger.info("main", "fase_3_report", "avvio generazione PDF")

        percorso_json = f"logs/audit_{nome_sessione}.json"
        report = ReportEngine(
            nome_sessione=nome_sessione,
            dispositivi=dispositivi,
            risultati_scenari=risultati,
            percorso_json_log=percorso_json
        )
        percorso_pdf = report.genera_pdf()

        logger.info("main", "fase_3_completata", {"pdf": percorso_pdf})

        # Alert Telegram — report pronto
        invia_alert_telegram(
            config["telegram_token"],
            config["telegram_chat_id"],
            f"✅ <b>Simulatore di Audit</b> — Audit completato\n"
            f"Report: {percorso_pdf}"
        )

        # 6. Riepilogo finale a schermo
        print("\n" + "=" * 50)
        print("  AUDIT COMPLETATO")
        print("=" * 50)
        print(f"  Dispositivi scansionati : {len(dispositivi)}")
        print(f"  Scenari eseguiti        : {len(risultati)}")
        print(f"  Scenari rilevabili      : {alert_count}")
        print(f"  Report PDF              : {percorso_pdf}")
        print(f"  Log sessione            : logs/audit_{nome_sessione}.log")
        print("=" * 50 + "\n")

    except KeyboardInterrupt:
        print("\n\n[!] Audit interrotto dall'utente.")
        logger.warn("main", "interrotto", "KeyboardInterrupt")

    finally:
        logger.chiudi()


if __name__ == "__main__":
    main()
