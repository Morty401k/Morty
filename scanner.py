"""
Simulatore di Audit - scanner.py
Scopre dispositivi e servizi attivi sulla rete locale.
Ottimizzato per Raspberry Pi Zero 2 W (512MB RAM).
"""

import socket
import subprocess
import ipaddress
import json
from datetime import datetime


# ─── Configurazione ───────────────────────────────────────────────
PORTE_COMUNI = [21, 22, 23, 80, 139, 443, 445, 3389, 8080]
TIMEOUT_PORTA = 0.5   # secondi - basso per non sprecare RAM
TIMEOUT_PING  = 1     # secondi


# ─── Funzioni principali ───────────────────────────────────────────

def ottieni_rete_locale():
    """Rileva automaticamente il range IP della rete locale."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_locale = s.getsockname()[0]
        s.close()
        # Costruisce il range /24 (es. 192.168.1.0/24)
        parti = ip_locale.rsplit(".", 1)
        return f"{parti[0]}.0/24", ip_locale
    except Exception as e:
        print(f"[ERRORE] Impossibile rilevare la rete: {e}")
        return None, None


def ping(ip):
    """Invia un ping a un IP. Restituisce True se risponde."""
    try:
        risultato = subprocess.run(
            ["ping", "-c", "1", "-W", str(TIMEOUT_PING), str(ip)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return risultato.returncode == 0
    except Exception:
        return False


def risolvi_hostname(ip):
    """Prova a risolvere il nome host da un IP."""
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except socket.herror:
        return "sconosciuto"


def scansiona_porta(ip, porta):
    """Controlla se una porta è aperta su un IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT_PORTA)
        risultato = s.connect_ex((str(ip), porta))
        s.close()
        return risultato == 0
    except Exception:
        return False


def scansiona_dispositivo(ip):
    """
    Analizza un singolo dispositivo:
    - verifica se è online
    - risolve il nome host
    - scansiona le porte comuni
    Restituisce un dizionario con i risultati.
    """
    ip_str = str(ip)

    if not ping(ip_str):
        return None  # dispositivo offline, saltiamo

    hostname = risolvi_hostname(ip_str)
    porte_aperte = []

    for porta in PORTE_COMUNI:
        if scansiona_porta(ip_str, porta):
            porte_aperte.append(porta)

    return {
        "ip": ip_str,
        "hostname": hostname,
        "porte_aperte": porte_aperte,
        "timestamp": datetime.now().isoformat()
    }


def esegui_scansione(rete=None):
    """
    Scansiona l'intera rete locale uno per uno (sequenziale,
    ottimizzato per 512MB RAM — niente threading pesante).
    Restituisce la lista dei dispositivi trovati.
    """
    if rete is None:
        rete, ip_locale = ottieni_rete_locale()
        if rete is None:
            return []
    else:
        ip_locale = None

    print(f"\n[*] Avvio scansione rete: {rete}")
    print(f"[*] IP del Raspberry: {ip_locale}")
    print(f"[*] Porte monitorate: {PORTE_COMUNI}\n")

    dispositivi = []
    rete_obj = ipaddress.IPv4Network(rete, strict=False)
    totale = sum(1 for _ in rete_obj.hosts())

    for i, ip in enumerate(rete_obj.hosts(), 1):
        # Salta il proprio IP
        if str(ip) == ip_locale:
            continue

        print(f"[{i}/{totale}] Controllo {ip}...", end="\r")
        risultato = scansiona_dispositivo(ip)

        if risultato:
            dispositivi.append(risultato)
            print(f"[+] Trovato: {risultato['ip']} ({risultato['hostname']}) "
                  f"| Porte aperte: {risultato['porte_aperte']}")

    print(f"\n[✓] Scansione completata. Dispositivi trovati: {len(dispositivi)}")
    return dispositivi


def salva_risultati(dispositivi, percorso="logs/scan_risultati.json"):
    """Salva i risultati della scansione in un file JSON."""
    import os
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, "w") as f:
        json.dump(dispositivi, f, indent=2, ensure_ascii=False)
    print(f"[✓] Risultati salvati in: {percorso}")


# ─── Test standalone ───────────────────────────────────────────────
if __name__ == "__main__":
    dispositivi = esegui_scansione()
    if dispositivi:
        salva_risultati(dispositivi)
        print("\n── Riepilogo ──")
        for d in dispositivi:
            print(f"  {d['ip']:16} | {d['hostname']:30} | porte: {d['porte_aperte']}")
    else:
        print("[!] Nessun dispositivo trovato.")
