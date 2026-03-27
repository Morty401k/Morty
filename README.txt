================================================================
  Simulatore di Audit - Simulatore di Insider Threat per Audit Etico
================================================================

  Progetto scolastico - 3AL 2025/2026
  Realizzato per: EasyTech (ICT)
  Hardware consigliato: Raspberry Pi Zero 2 W (512MB RAM)

================================================================
  DESCRIZIONE
================================================================

Simulatore di Audit e' uno strumento di audit etico che simula il
comportamento di un dipendente malintenzionato (insider threat)
all'interno di una rete aziendale.

L'obiettivo e' testare se i sistemi di sicurezza esistenti
riescono a rilevare comportamenti sospetti, e produrre un
report PDF con i gap di sicurezza identificati.

IMPORTANTE: usare SOLO su reti di propria proprieta' o su cui
si ha esplicita autorizzazione scritta. L'uso non autorizzato
e' illegale.

================================================================
  STRUTTURA DEL PROGETTO
================================================================

  Simulatore di Audit/
  |
  |-- main.py               Entry point - avvia tutto
  |-- scanner.py            Scansione rete e porte aperte
  |-- scenario_engine.py    4 scenari insider threat
  |-- logger.py             Log su file con timestamp
  |-- report_engine.py      Generazione report PDF
  |-- config.json           Configurazione personalizzabile
  |-- requirements.txt      Dipendenze Python
  |
  |-- logs/                 (creata automaticamente)
  |   |-- audit_SESSIONE.log
  |   |-- audit_SESSIONE.json
  |
  |-- reports/              (creata automaticamente)
      |-- simulatore_audit_report_SESSIONE.pdf

================================================================
  SCENARI SIMULATI
================================================================

  1. Port scan silenzioso
     Scansiona porte sensibili su tutti i dispositivi in rete.
     Simula: dipendente che cerca servizi aperti.

  2. Enumerazione SMB
     Rileva cartelle condivise Windows (porta 445).
     Simula: accesso non autorizzato a documenti aziendali.

  3. SSH con credenziali deboli
     Tenta login SSH con password comuni (admin/admin ecc.).
     Simula: accesso remoto con credenziali rubate o deboli.

  4. Esfiltrazione simulata
     Invia un file fittizio via HTTP verso un server interno.
     Simula: furto di dati verso l'esterno.

================================================================
  INSTALLAZIONE
================================================================

  Requisiti:
    - Python 3.9 o superiore
    - pip

  1. Clona o copia i file nella cartella del progetto

  2. Installa le dipendenze:

       pip install -r requirements.txt

     oppure su Linux/Raspberry con sistema gestito:

       pip install -r requirements.txt --break-system-packages

  3. (Opzionale) Configura Telegram in config.json per
     ricevere alert in tempo reale sul telefono.

================================================================
  UTILIZZO
================================================================

  Avvio standard (Linux / Raspberry Pi):

    sudo python3 main.py

  Avvio su Windows (PowerShell):

    python main.py

  Simulatore di Audit eseguira' automaticamente le 3 fasi:

    [FASE 1] Scansione rete
    [FASE 2] Esecuzione scenari
    [FASE 3] Generazione report PDF

  Il report viene salvato in: reports/simulatore_audit_report_*.pdf

================================================================
  CONFIGURAZIONE (config.json)
================================================================

  rete            Specifica manualmente la rete da scansionare
                  (es. "192.168.1.0/24"). null = automatica.

  porte_extra     Lista di porte aggiuntive da controllare
                  (es. [8443, 9090]).

  pausa_scenari   Secondi di pausa tra uno scenario e l'altro.
                  Default: 3.

  telegram_token  Token del bot Telegram per gli alert.
                  Lascia vuoto per disabilitare.

  telegram_chat_id  ID della chat Telegram per gli alert.

================================================================
  DIPENDENZE
================================================================

  fpdf2           Generazione PDF leggera (ottimizzata 512MB)
  paramiko        Connessioni SSH per lo scenario credenziali

  Moduli standard Python (gia' inclusi):
    socket, subprocess, ipaddress, json, os, time, datetime,
    urllib.request

================================================================
  TEST IN AMBIENTE SICURO
================================================================

  Metodo 1 - Rete di casa (piu' semplice):
    Avvia direttamente sulla tua rete domestica.
    E' legale perche' sei il proprietario.

  Metodo 2 - VirtualBox (piu' professionale):
    1. Crea due VM Linux su VirtualBox
    2. Imposta entrambe su "Rete interna"
    3. Avvia Simulatore di Audit sulla VM1
    4. La VM2 fa da bersaglio

================================================================
  AUTORE E LICENZA
================================================================

  Progetto didattico - uso esclusivamente educativo.
  Vietato l'uso su reti non autorizzate.

================================================================
