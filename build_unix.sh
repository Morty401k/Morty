#!/bin/bash
# build_unix.sh - Compila SimulatoreAudit su Linux o Mac
# Funziona su: Ubuntu, Kali, Debian, Fedora, Arch, macOS

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

OS=$(uname -s)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}"
echo "  ================================================"
if [ "$OS" = "Darwin" ]; then
    echo "    Build - Simulatore di Audit per Mac"
else
    echo "    Build - Simulatore di Audit per Linux"
fi
echo "  ================================================"
echo -e "${NC}"

# Controlla Python
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERRORE] Python3 non trovato.${NC}"
    if [ "$OS" = "Darwin" ]; then
        echo "Installalo con: brew install python3"
    else
        echo "Installalo con: sudo apt install python3 python3-pip"
    fi
    exit 1
fi

echo -e "${GREEN}[✓] Python: $(python3 --version)${NC}"

# Installa dipendenze
echo -e "${YELLOW}[*] Installazione dipendenze...${NC}"

if [ "$OS" = "Darwin" ]; then
    # Mac: usa pip normale
    pip3 install pyinstaller fpdf2 paramiko -q
else
    # Linux: prova prima senza flag, poi con --break-system-packages
    pip3 install pyinstaller fpdf2 paramiko -q 2>/dev/null || \
    pip3 install pyinstaller fpdf2 paramiko -q --break-system-packages
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERRORE] Installazione dipendenze fallita.${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Dipendenze installate.${NC}"

# Compila
echo -e "${YELLOW}[*] Compilazione in corso (qualche minuto)...${NC}"
cd "$SCRIPT_DIR"

if [ "$OS" = "Darwin" ]; then
    NOME="SimulatoreAudit_mac"
else
    NOME="SimulatoreAudit_linux"
fi

python3 -m PyInstaller --onefile \
            --name "$NOME" \
            --hidden-import fpdf \
            --hidden-import paramiko \
            avvia.py

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERRORE] Compilazione fallita.${NC}"
    exit 1
fi

# Dai permessi di esecuzione
chmod +x "$SCRIPT_DIR/dist/$NOME"

# Pulizia
rm -rf build "$NOME.spec"

echo -e "${GREEN}"
echo "  ================================================"
echo "  Compilazione completata!"
echo "  Eseguibile: dist/$NOME"
echo ""
echo "  Per avviarlo:"
echo "  sudo ./dist/$NOME"
echo "  ================================================"
echo -e "${NC}"
