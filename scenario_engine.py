"""
Simulatore di Audit - scenario_engine.py
Simula comportamenti sospetti di un insider threat sulla rete.
Gli scenari vengono eseguiti in sequenza (ottimizzato per 512MB RAM).

IMPORTANTE: usare SOLO su reti di cui si è proprietari o
su cui si ha esplicita autorizzazione scritta.
"""

import socket
import subprocess
import os
import time
import json
from datetime import datetime


# ─── Configurazione ───────────────────────────────────────────────
TIMEOUT     = 2      # secondi per ogni connessione
PAUSA_TRA_SCENARI = 3  # secondi di pausa tra uno scenario e l'altro


# ─── Classe principale ─────────────────────────────────────────────

class ScenarioEngine:
    def __init__(self, logger, dispositivi):
        """
        Parametri:
          logger      - istanza di Logger (da logger.py)
          dispositivi - lista di dispositivi trovati da scanner.py
        """
        self.logger      = logger
        self.dispositivi = dispositivi
        self.risultati   = []  # raccoglie l'esito di ogni scenario

    # ──────────────────────────────────────────────────────────────
    # SCENARIO 1 — Port scan silenzioso
    # Simula un dipendente che cerca servizi aperti in silenzio
    # ──────────────────────────────────────────────────────────────
    def scenario_port_scan(self, ip, porte_extra=None):
        """
        Tenta connessioni TCP su porte sensibili.
        Registra ogni porta aperta come evento WARN.
        """
        nome = "port_scan_silenzioso"
        self.logger.info("scenario", f"[{nome}] avvio", {"target": ip})

        porte = [21, 22, 23, 25, 80, 110, 139, 443, 445, 3306, 3389, 8080]
        if porte_extra:
            porte += porte_extra

        trovate = []
        for porta in porte:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(TIMEOUT)
                esito = s.connect_ex((ip, porta))
                s.close()
                if esito == 0:
                    trovate.append(porta)
                    self.logger.warn(
                        "scenario",
                        f"[{nome}] porta_aperta",
                        {"ip": ip, "porta": porta}
                    )
            except Exception as e:
                self.logger.errore("scenario", f"[{nome}] errore_porta", str(e))

        esito_scenario = {
            "scenario": nome,
            "target":   ip,
            "porte_aperte": trovate,
            "rilevabile": len(trovate) > 0
        }
        self.risultati.append(esito_scenario)
        self.logger.info("scenario", f"[{nome}] completato", esito_scenario)
        return esito_scenario

    # ──────────────────────────────────────────────────────────────
    # SCENARIO 2 — Enumerazione cartelle SMB condivise
    # Simula accesso a cartelle di rete Windows (\\server\share)
    # ──────────────────────────────────────────────────────────────
    def scenario_smb_enum(self, ip):
        """
        Prova a listare le cartelle condivise via SMB (porta 445).
        Non effettua login — rileva solo se il servizio risponde.
        """
        nome = "smb_enumerazione"
        self.logger.info("scenario", f"[{nome}] avvio", {"target": ip})

        # Controlla se la porta SMB è aperta
        smb_aperto = False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(TIMEOUT)
            if s.connect_ex((ip, 445)) == 0:
                smb_aperto = True
            s.close()
        except Exception:
            pass

        if not smb_aperto:
            self.logger.info("scenario", f"[{nome}] smb_chiuso", {"ip": ip})
            esito_scenario = {"scenario": nome, "target": ip, "smb_aperto": False, "rilevabile": False}
            self.risultati.append(esito_scenario)
            return esito_scenario

        self.logger.alert(
            "scenario",
            f"[{nome}] smb_raggiungibile",
            {"ip": ip, "nota": "servizio SMB esposto — potenziale accesso cartelle condivise"}
        )

        # Prova con smbclient se disponibile (solo Linux)
        shares = []
        try:
            risultato = subprocess.run(
                ["smbclient", "-L", ip, "-N", "--no-pass"],
                capture_output=True, text=True, timeout=TIMEOUT + 2
            )
            for riga in risultato.stdout.splitlines():
                if "Disk" in riga or "IPC" in riga:
                    shares.append(riga.strip())
                    self.logger.alert(
                        "scenario",
                        f"[{nome}] share_trovata",
                        {"ip": ip, "share": riga.strip()}
                    )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.logger.warn("scenario", f"[{nome}] smbclient_non_disponibile",
                             "installa smbclient per enumerazione completa")

        esito_scenario = {
            "scenario":   nome,
            "target":     ip,
            "smb_aperto": True,
            "shares":     shares,
            "rilevabile": True
        }
        self.risultati.append(esito_scenario)
        self.logger.info("scenario", f"[{nome}] completato", esito_scenario)
        return esito_scenario

    # ──────────────────────────────────────────────────────────────
    # SCENARIO 3 — Tentativo SSH con credenziali deboli
    # Simula un dipendente che prova password banali su SSH
    # ──────────────────────────────────────────────────────────────
    def scenario_ssh_debole(self, ip):
        """
        Tenta login SSH con credenziali comuni (admin/admin, root/root ecc.).
        Non usa dizionari pesanti — solo 5 coppie tipiche degli insider.
        """
        nome = "ssh_credenziali_deboli"
        self.logger.info("scenario", f"[{nome}] avvio", {"target": ip})

        # Controlla se SSH è aperto
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(TIMEOUT)
            if s.connect_ex((ip, 22)) != 0:
                self.logger.info("scenario", f"[{nome}] ssh_chiuso", {"ip": ip})
                esito_scenario = {"scenario": nome, "target": ip, "ssh_aperto": False, "rilevabile": False}
                self.risultati.append(esito_scenario)
                return esito_scenario
            s.close()
        except Exception:
            pass

        credenziali_test = [
            ("admin",  "admin"),
            ("root",   "root"),
            ("user",   "password"),
            ("pi",     "raspberry"),   # default Raspberry Pi
            ("admin",  "1234"),
        ]

        successo = False
        tentativi = []

        try:
            import paramiko
            for utente, password in credenziali_test:
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(ip, port=22, username=utente,
                                   password=password, timeout=TIMEOUT)
                    successo = True
                    self.logger.alert(
                        "scenario",
                        f"[{nome}] LOGIN_RIUSCITO",
                        {"ip": ip, "utente": utente, "password": password}
                    )
                    client.close()
                    tentativi.append({"utente": utente, "esito": "SUCCESSO"})
                    break
                except paramiko.AuthenticationException:
                    self.logger.warn("scenario", f"[{nome}] tentativo_fallito",
                                     {"ip": ip, "utente": utente})
                    tentativi.append({"utente": utente, "esito": "fallito"})
                except Exception as e:
                    self.logger.errore("scenario", f"[{nome}] errore", str(e))
                    break
                time.sleep(0.5)  # pausa tra tentativi

        except ImportError:
            self.logger.warn("scenario", f"[{nome}] paramiko_mancante",
                             "installa paramiko: pip install paramiko")

        esito_scenario = {
            "scenario":   nome,
            "target":     ip,
            "ssh_aperto": True,
            "tentativi":  tentativi,
            "successo":   successo,
            "rilevabile": True
        }
        self.risultati.append(esito_scenario)
        self.logger.info("scenario", f"[{nome}] completato", esito_scenario)
        return esito_scenario

    # ──────────────────────────────────────────────────────────────
    # SCENARIO 4 — Esfiltrazione simulata (file piccoli via HTTP)
    # Simula un dipendente che invia file fuori dalla rete
    # ──────────────────────────────────────────────────────────────
    def scenario_esfiltrazione_simulata(self, ip):
        """
        Crea un file fittizio e tenta di inviarlo via HTTP POST
        a un server interno. Simula esfiltrazione dati.
        NON invia dati reali — solo un file di testo fittizio.
        """
        nome = "esfiltrazione_simulata"
        self.logger.info("scenario", f"[{nome}] avvio", {"target": ip})

        # Crea file fittizio
        contenuto = json.dumps({
            "simulazione": True,
            "dati_fittizi": "questo non è un documento reale",
            "timestamp": datetime.now().isoformat()
        })
        percorso_tmp = "/tmp/simulatore_audit_test.json"
        with open(percorso_tmp, "w") as f:
            f.write(contenuto)

        self.logger.warn("scenario", f"[{nome}] file_creato",
                         {"percorso": percorso_tmp, "dimensione": f"{len(contenuto)}B"})

        # Tenta invio via HTTP (porta 80)
        inviato = False
        try:
            import urllib.request
            url = f"http://{ip}/upload"
            dati = contenuto.encode("utf-8")
            req = urllib.request.Request(url, data=dati, method="POST")
            req.add_header("Content-Type", "application/json")
            urllib.request.urlopen(req, timeout=TIMEOUT)
            inviato = True
            self.logger.alert("scenario", f"[{nome}] DATI_INVIATI",
                              {"url": url, "dimensione": f"{len(dati)}B"})
        except Exception:
            # Il server probabilmente non ha /upload — normale
            self.logger.info("scenario", f"[{nome}] server_non_ha_risposto",
                             {"nota": "nessun endpoint /upload trovato — normale in test"})

        # Pulisci il file temporaneo
        try:
            os.remove(percorso_tmp)
        except Exception:
            pass

        esito_scenario = {
            "scenario":  nome,
            "target":    ip,
            "inviato":   inviato,
            "rilevabile": inviato
        }
        self.risultati.append(esito_scenario)
        self.logger.info("scenario", f"[{nome}] completato", esito_scenario)
        return esito_scenario

    # ──────────────────────────────────────────────────────────────
    # Esegui tutti gli scenari su tutti i dispositivi
    # ──────────────────────────────────────────────────────────────
    def esegui_tutti(self):
        """
        Esegue tutti e 4 gli scenari su ogni dispositivo trovato.
        Sequenziale — un dispositivo alla volta, uno scenario alla volta.
        """
        if not self.dispositivi:
            self.logger.warn("scenario", "nessun_dispositivo", "lista vuota da scanner")
            return []

        print(f"\n[*] Avvio scenari su {len(self.dispositivi)} dispositivi...\n")

        for dispositivo in self.dispositivi:
            ip = dispositivo["ip"]
            print(f"\n{'─'*50}")
            print(f"[*] Target: {ip} ({dispositivo.get('hostname', '?')})")
            print(f"{'─'*50}")

            self.scenario_port_scan(ip)
            time.sleep(PAUSA_TRA_SCENARI)

            self.scenario_smb_enum(ip)
            time.sleep(PAUSA_TRA_SCENARI)

            self.scenario_ssh_debole(ip)
            time.sleep(PAUSA_TRA_SCENARI)

            self.scenario_esfiltrazione_simulata(ip)
            time.sleep(PAUSA_TRA_SCENARI)

        print(f"\n[✓] Tutti gli scenari completati. Totale eventi: {len(self.risultati)}")
        return self.risultati


# ─── Test standalone ───────────────────────────────────────────────
if __name__ == "__main__":
    from logger import Logger

    # Dispositivi fittizi per test
    dispositivi_test = [
        {"ip": "192.168.1.1", "hostname": "router"},
    ]

    logger = Logger()
    engine = ScenarioEngine(logger, dispositivi_test)
    engine.esegui_tutti()
    logger.chiudi()
