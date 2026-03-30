#!/bin/bash
# build.sh - Compila il SimulatoreAudit nel Persistent Storage di Tails
# Esegui una sola volta dopo aver abilitato il Persistent Storage

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PERSISTENT="/home/amnesia/Persistent"
PROGETTO="$PERSISTENT/SimulatoreAudit"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}"
echo "  ================================================"
echo "    Build - Simulatore di Audit per Tails"
echo "  ================================================"
echo -e "${NC}"

# Controlla Persistent Storage
if [ ! -d "$PERSISTENT" ]; then
    echo -e "${RED}[ERRORE] Persistent Storage non trovato.${NC}"
    echo "Abilitalo da Applications → Tails → Persistent Storage"
    read -p "Premi INVIO per uscire..."
    exit 1
fi

echo -e "${GREEN}[✓] Persistent Storage trovato.${NC}"

# Crea cartella progetto nel Persistent
mkdir -p "$PROGETTO"
echo -e "${GREEN}[*] Copia file in $PROGETTO...${NC}"
cp "$SCRIPT_DIR"/*.py "$PROGETTO/"
cp "$SCRIPT_DIR/config.json" "$PROGETTO/" 2>/dev/null || true
cp "$SCRIPT_DIR/requirements.txt" "$PROGETTO/" 2>/dev/null || true

# Installa dipendenze
echo -e "${YELLOW}[*] Installazione dipendenze...${NC}"
pip install pyinstaller fpdf2 paramiko --break-system-packages -q

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERRORE] Installazione fallita. Controlla la connessione.${NC}"
    read -p "Premi INVIO per uscire..."
    exit 1
fi

echo -e "${GREEN}[✓] Dipendenze installate.${NC}"

# Compila eseguibile
echo -e "${YELLOW}[*] Compilazione eseguibile (potrebbe richiedere qualche minuto)...${NC}"
cd "$PROGETTO"

pyinstaller --onefile \
            --name "SimulatoreAudit" \
            --hidden-import fpdf \
            --hidden-import paramiko \
            --distpath "$PROGETTO" \
            --workpath /tmp/build \
            --specpath /tmp \
            avvia.py

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERRORE] Compilazione fallita.${NC}"
    read -p "Premi INVIO per uscire..."
    exit 1
fi

# Dai permessi di esecuzione
chmod +x "$PROGETTO/SimulatoreAudit"

# Pulizia file temporanei di build
rm -rf /tmp/build /tmp/SimulatoreAudit.spec

echo -e "${GREEN}"
echo "  ================================================"
echo "  Compilazione completata!"
echo "  Eseguibile: $PROGETTO/SimulatoreAudit"
echo ""
echo "  Per avviarlo:"
echo "  sudo $PROGETTO/SimulatoreAudit"
echo "  ================================================"
echo -e "${NC}"

read -p "Premi INVIO per uscire..."
