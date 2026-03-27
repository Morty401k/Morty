#!/bin/bash
# ================================================================
#  Simulatore di Audit - Launcher per Tails Linux
#  Tutto gira in RAM — nessun dato scritto su disco
#  Doppio click per avviare
# ================================================================

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}"
echo "  ================================================"
echo "    Simulatore di Audit - Launcher Tails Linux"
echo "  ================================================"
echo -e "${NC}"

# ── Controlla che siamo su Tails ─────────────────────────────────
if ! grep -q "Tails" /etc/os-release 2>/dev/null; then
    echo -e "${YELLOW}[WARN] Non sembra Tails Linux — continuo comunque...${NC}"
fi

# ── Crea cartella di lavoro in RAM (/tmp sparisce al riavvio) ─────
WORKDIR=$(mktemp -d /tmp/simulatore_audit_XXXXXX)
echo -e "${GREEN}[*] Cartella di lavoro in RAM: $WORKDIR${NC}"

# ── Copia i file del progetto nella RAM ───────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR"/*.py "$WORKDIR/"
cp "$SCRIPT_DIR/config.json" "$WORKDIR/" 2>/dev/null || true

cd "$WORKDIR"

# ── Controlla Python ──────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERRORE] Python3 non trovato!${NC}"
    read -p "Premi INVIO per uscire..."
    exit 1
fi

echo -e "${GREEN}[*] Python: $(python3 --version)${NC}"

# ── Installa dipendenze in RAM (--target evita scritture di sistema)
echo -e "${YELLOW}[*] Installazione dipendenze in RAM...${NC}"
DEPS_DIR="$WORKDIR/deps"
mkdir -p "$DEPS_DIR"

pip install fpdf2 paramiko --target="$DEPS_DIR" -q --no-deps 2>/dev/null || \
pip3 install fpdf2 paramiko --target="$DEPS_DIR" -q --no-deps 2>/dev/null

# Aggiunge le dipendenze al path Python
export PYTHONPATH="$DEPS_DIR:$PYTHONPATH"

# ── Avvia il simulatore ───────────────────────────────────────────
echo -e "${GREEN}[*] Avvio simulatore...${NC}\n"
sudo python3 "$WORKDIR/main.py" --ram-mode

EXIT_CODE=$?

# ── Pulizia sicura della RAM ──────────────────────────────────────
echo -e "\n${YELLOW}[*] Pulizia dati dalla RAM...${NC}"
rm -rf "$WORKDIR"
echo -e "${GREEN}[✓] Nessuna traccia lasciata.${NC}"

if [ $EXIT_CODE -ne 0 ]; then
    echo -e "${RED}[!] Il simulatore è uscito con errore $EXIT_CODE${NC}"
fi

read -p "Premi INVIO per chiudere..."
