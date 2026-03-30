PortaCore - Simulatore di Insider Threat
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
build_windows.bat     compila eseguibile per Windows
build_unix.sh         compila eseguibile per Linux e Mac
build.sh              compila eseguibile nel Persistent Storage di Tails
config.json           configurazione
requirements.txt      dipendenze Python


SCENARI

1. port scan silenzioso
2. enumerazione cartelle SMB
3. SSH con credenziali deboli
4. esfiltrazione simulata via HTTP


VERSIONE PORTABLE - WINDOWS

Avvio diretto senza compilare:
  python avvia.py

Oppure compila un eseguibile standalone:
  doppio click su build_windows.bat
  oppure da PowerShell: .\build_windows.bat
  risultato: dist\PortaCore.exe
  avvio: tasto destro - Esegui come amministratore


VERSIONE PORTABLE - MAC

Avvio diretto senza compilare:
  sudo python3 avvia.py

Oppure compila un eseguibile standalone:
  bash build_unix.sh
  risultato: dist/PortaCore_mac
  avvio: sudo ./dist/PortaCore_mac


VERSIONE PORTABLE - LINUX

Avvio diretto senza compilare:
  sudo python3 avvia.py

Oppure compila un eseguibile standalone:
  bash build_unix.sh
  risultato: dist/PortaCore_linux
  avvio: sudo ./dist/PortaCore_linux


VERSIONE TAILS LINUX

Tutto gira in RAM. Log e report spariscono al riavvio.
Il programma si salva nel Persistent Storage e rimane disponibile.

Avvio diretto:
  bash avvia_tails.sh

Oppure compila nel Persistent Storage (una volta sola):
  bash build.sh
  risultato: /home/amnesia/Persistent/PortaCore/PortaCore
  avvio: sudo /home/amnesia/Persistent/PortaCore/PortaCore

Avvio senza lasciare tracce anche senza compilare:
  sudo python3 main.py --ram-mode


CONFIGURAZIONE

config.json accetta questi parametri:
  rete              range IP da scansionare, null per automatico
  porte_extra       porte aggiuntive da controllare
  pausa_scenari     secondi tra uno scenario e l'altro
  telegram_token    token bot Telegram per alert
  telegram_chat_id  chat ID Telegram per alert


DIPENDENZE

fpdf2 e paramiko
installate automaticamente da avvia.py nella cartella deps/
oppure manualmente con: pip install -r requirements.txt


NOTE

Progetto didattico, uso esclusivamente educativo.
