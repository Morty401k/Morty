Simulatore di Audit - Insider Threat Tool
Progetto scolastico 3AL 2025/2026 - EasyTech ICT


DESCRIZIONE

Strumento di audit etico che simula comportamenti sospetti di un
dipendente malintenzionato su una rete aziendale. Produce un
report PDF con i gap di sicurezza identificati.

Usare solo su reti di propria proprieta' o con autorizzazione
scritta. L'uso non autorizzato e' illegale.


FILE

main.py               entry point principale
scanner.py            scansione rete e porte
scenario_engine.py    scenari insider threat
logger.py             log con timestamp
report_engine.py      generazione report PDF
avvia.py              launcher portable Windows/Mac/Linux
avvia_tails.sh        launcher per Tails Linux
config.json           configurazione
requirements.txt      dipendenze Python


SCENARI

1. port scan silenzioso
2. enumerazione cartelle SMB
3. SSH con credenziali deboli
4. esfiltrazione simulata via HTTP


INSTALLAZIONE

pip install -r requirements.txt


AVVIO

Windows
  python avvia.py

Mac / Linux
  sudo python3 avvia.py

Tails Linux
  bash avvia_tails.sh

Manuale con modalita RAM (nessuna traccia)
  sudo python3 main.py --ram-mode


TAILS - PERSISTENT STORAGE

I log e i report vengono salvati in RAM e spariscono al riavvio.
Il programma si salva nel Persistent Storage e rimane disponibile.

Per compilare l'eseguibile su Tails:
  pip install pyinstaller fpdf2 paramiko --break-system-packages
  pyinstaller --onefile --name SimulatoreAudit avvia.py
  cp dist/SimulatoreAudit /home/amnesia/Persistent/


CONFIGURAZIONE

config.json accetta questi parametri:
  rete              range IP da scansionare, null per automatico
  porte_extra       porte aggiuntive da controllare
  pausa_scenari     secondi tra uno scenario e l'altro
  telegram_token    token bot Telegram per alert
  telegram_chat_id  chat ID Telegram per alert


DIPENDENZE

fpdf2 e paramiko (installate automaticamente da avvia.py)


NOTE

Progetto didattico, uso esclusivamente educativo.
