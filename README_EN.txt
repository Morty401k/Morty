PortaCore - Insider Threat Simulator
School Project 3AL 2025/2026 - EasyTech ICT


DESCRIPTION

Ethical audit tool that simulates suspicious behavior of a malicious
employee within a corporate network. Generates a PDF report highlighting
identified security gaps.

Use only on networks you own or have written authorization for.
Unauthorized use is illegal.


FILES

main.py               main entry point
scanner.py            network and port scanning
scenario_engine.py    insider threat scenarios
logger.py             timestamped logging
report_engine.py      PDF report generation
avvia.py              portable launcher Windows/Mac/Linux
avvia_tails.sh        launcher for Tails Linux
build_windows.bat     builds executable for Windows
build_unix.sh         builds executable for Linux and Mac
build.sh              builds executable in Tails Persistent Storage
config.json           configuration file
requirements.txt      Python dependencies


SCENARIOS

1. silent port scan
2. SMB folder enumeration
3. SSH with weak credentials
4. simulated HTTP data exfiltration


PORTABLE VERSION - WINDOWS

Run directly without compiling:
  python avvia.py

Or build a standalone executable:
  double click build_windows.bat
  or from PowerShell: .\build_windows.bat
  output: dist\PortaCore.exe
  run: right click - Run as administrator


PORTABLE VERSION - MAC

Run directly without compiling:
  sudo python3 avvia.py

Or build a standalone executable:
  bash build_unix.sh
  output: dist/PortaCore_mac
  run: sudo ./dist/PortaCore_mac


PORTABLE VERSION - LINUX

Run directly without compiling:
  sudo python3 avvia.py

Or build a standalone executable:
  bash build_unix.sh
  output: dist/PortaCore_linux
  run: sudo ./dist/PortaCore_linux


TAILS LINUX VERSION

Everything runs in RAM. Logs and reports disappear after reboot.
The program is saved in Persistent Storage and remains available.

Run directly:
  bash avvia_tails.sh

Or build in Persistent Storage (once only):
  bash build.sh
  output: /home/amnesia/Persistent/PortaCore/PortaCore
  run: sudo /home/amnesia/Persistent/PortaCore/PortaCore

Run without leaving any trace without compiling:
  sudo python3 main.py --ram-mode


CONFIGURATION

config.json supports the following parameters:
  rete              IP range to scan, null for automatic
  porte_extra       additional ports to scan
  pausa_scenari     seconds between scenarios
  telegram_token    Telegram bot token for alerts
  telegram_chat_id  Telegram chat ID for alerts


DEPENDENCIES

fpdf2 and paramiko
automatically installed by avvia.py in the deps/ folder
or manually with: pip install -r requirements.txt


NOTES

Educational project, for learning purposes only.
