#!/usr/bin/env python3
"""
Simulatore di Audit - Launcher Portable
Funziona su Windows, Mac e qualsiasi distro Linux.
Installa automaticamente le dipendenze nella cartella locale deps/.
"""

import sys
import os
import subprocess
import platform

IS_WIN   = platform.system() == "Windows"
IS_MAC   = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


# ─── Colori ANSI ──────────────────────────────────────────────────

def abilita_colori_windows():
    """Abilita i colori ANSI su Windows 10+."""
    if IS_WIN:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

def c(testo, colore):
    codici = {
        "verde":  "\033[92m",
        "giallo": "\033[93m",
        "rosso":  "\033[91m",
        "reset":  "\033[0m"
    }
    return f"{codici.get(colore, '')}{testo}{codici['reset']}"


# ─── Controlli di sistema ──────────────────────────────────────────

def controlla_python():
    """Verifica Python >= 3.9"""
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 9):
        print(c(f"[ERRORE] Python {v.major}.{v.minor} non supportato. Serve 3.9+", "rosso"))
        sys.exit(1)
    print(c(f"[✓] Python {v.major}.{v.minor}.{v.micro} su {platform.system()}", "verde"))


def controlla_privilegi():
    """Controlla e avvisa se mancano i privilegi di rete."""
    if IS_WIN:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print(c("[!] Non stai eseguendo come Amministratore.", "giallo"))
                print(c("    Lo scanner di rete potrebbe non funzionare.", "giallo"))
                print(c("    Riesegui con tasto destro -> Esegui come amministratore.\n", "giallo"))
        except Exception:
            pass
    elif IS_MAC or IS_LINUX:
        if os.geteuid() != 0:
            print(c("[!] Non stai eseguendo come root.", "giallo"))
            print(c("    Usa: sudo python3 avvia.py\n", "giallo"))


# ─── Dipendenze ────────────────────────────────────────────────────

def installa_dipendenze():
    """
    Installa fpdf2 e paramiko nella cartella locale deps/.
    Non tocca il sistema — tutto portable e autocontenuto.
    """
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    deps_dir    = os.path.join(script_dir, "deps")
    fpdf_ok     = os.path.exists(os.path.join(deps_dir, "fpdf"))
    paramiko_ok = os.path.exists(os.path.join(deps_dir, "paramiko"))

    if fpdf_ok and paramiko_ok:
        print(c("[✓] Dipendenze gia' installate.", "verde"))
    else:
        print(c("[*] Prima installazione dipendenze...", "giallo"))
        os.makedirs(deps_dir, exist_ok=True)
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "fpdf2", "paramiko",
                "--target", deps_dir,
                "--quiet"
            ])
            print(c("[✓] Dipendenze installate in deps/", "verde"))
        except subprocess.CalledProcessError:
            print(c("[ERRORE] Installazione dipendenze fallita.", "rosso"))
            print(c("         Controlla la connessione internet.", "rosso"))
            input("\nPremi INVIO per uscire...")
            sys.exit(1)

    # Aggiunge deps al path Python
    if deps_dir not in sys.path:
        sys.path.insert(0, deps_dir)


# ─── Banner ────────────────────────────────────────────────────────

def stampa_banner():
    sistema = platform.system()
    if IS_WIN:
        etichetta = "Windows"
    elif IS_MAC:
        etichetta = "Mac"
    else:
        # Prova a leggere il nome della distro
        try:
            with open("/etc/os-release") as f:
                for riga in f:
                    if riga.startswith("PRETTY_NAME"):
                        etichetta = riga.split("=")[1].strip().strip('"')
                        break
                else:
                    etichetta = "Linux"
        except Exception:
            etichetta = "Linux"

    print(c(f"""
  ================================================
    Simulatore di Audit - Versione Portable
    {etichetta}
  ================================================
""", "verde"))


# ─── Main ──────────────────────────────────────────────────────────

def main():
    abilita_colori_windows()
    stampa_banner()
    controlla_python()
    installa_dipendenze()
    controlla_privilegi()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    print(c("\n[*] Avvio simulatore...\n", "verde"))

    try:
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
