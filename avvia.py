#!/usr/bin/env python3
"""
Simulatore di Audit - Launcher Portable
Funziona su Windows, Mac e Linux senza installare niente.
Installa automaticamente le dipendenze nella cartella locale.
"""

import sys
import os
import subprocess
import platform

# ── Colori ANSI (disabilitati su Windows vecchio) ─────────────────
IS_WIN = platform.system() == "Windows"

def c(testo, colore):
    codici = {"verde": "\033[92m", "giallo": "\033[93m",
              "rosso": "\033[91m", "reset": "\033[0m"}
    if IS_WIN:
        try:
            os.system("color")  # abilita ANSI su Windows 10+
        except Exception:
            return testo
    return f"{codici.get(colore, '')}{testo}{codici['reset']}"

def stampa_banner():
    print(c("""
  ================================================
    Simulatore di Audit - Versione Portable
    Windows | Mac | Linux
  ================================================
""", "verde"))

def controlla_python():
    """Verifica che Python sia >= 3.9"""
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 9):
        print(c(f"[ERRORE] Python {v.major}.{v.minor} non supportato. Serve Python 3.9+", "rosso"))
        sys.exit(1)
    print(c(f"[✓] Python {v.major}.{v.minor}.{v.micro}", "verde"))

def installa_dipendenze():
    """
    Installa fpdf2 e paramiko nella cartella locale ./deps/
    Non tocca il sistema — tutto portable.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    deps_dir   = os.path.join(script_dir, "deps")

    # Controlla se già installate
    fpdf_ok    = os.path.exists(os.path.join(deps_dir, "fpdf"))
    paramiko_ok = os.path.exists(os.path.join(deps_dir, "paramiko"))

    if fpdf_ok and paramiko_ok:
        print(c("[✓] Dipendenze già installate.", "verde"))
    else:
        print(c("[*] Installazione dipendenze in corso...", "giallo"))
        os.makedirs(deps_dir, exist_ok=True)
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "fpdf2", "paramiko",
            "--target", deps_dir,
            "--quiet"
        ])
        print(c("[✓] Dipendenze installate.", "verde"))

    # Aggiunge deps al path
    if deps_dir not in sys.path:
        sys.path.insert(0, deps_dir)

def avvisa_privilegi():
    """Avvisa se non si hanno i privilegi di amministratore/root."""
    sistema = platform.system()
    if sistema == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print(c("[WARN] Non stai eseguendo come Amministratore.", "giallo"))
                print(c("       Lo scanner di rete potrebbe non funzionare correttamente.", "giallo"))
                print(c("       Riesegui come Amministratore per risultati migliori.\n", "giallo"))
        except Exception:
            pass
    elif sistema in ("Linux", "Darwin"):
        if os.geteuid() != 0:
            print(c("[WARN] Non stai eseguendo come root.", "giallo"))
            print(c("       Usa 'sudo python3 avvia.py' per risultati migliori.\n", "giallo"))

def main():
    stampa_banner()
    controlla_python()
    installa_dipendenze()
    avvisa_privilegi()

    # Aggiunge la cartella del progetto al path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    print(c("\n[*] Avvio simulatore...\n", "verde"))

    try:
        # Importa e avvia main
        import main as simulatore
        simulatore.main()
    except ImportError as e:
        print(c(f"[ERRORE] File mancante: {e}", "rosso"))
        print(c("         Assicurati che tutti i file .py siano nella stessa cartella.", "rosso"))
        input("\nPremi INVIO per uscire...")
        sys.exit(1)
    except KeyboardInterrupt:
        print(c("\n\n[!] Interrotto dall'utente.", "giallo"))
    except Exception as e:
        print(c(f"\n[ERRORE] {e}", "rosso"))
        input("\nPremi INVIO per uscire...")
        sys.exit(1)

if __name__ == "__main__":
    main()
