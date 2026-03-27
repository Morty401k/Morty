Audit Simulator - Insider Threat Tool School Project 3AL 2025/2026 -
EasyTech ICT

DESCRIPTION

Ethical audit tool that simulates suspicious behavior of a malicious
employee within a corporate network. It generates a PDF report
highlighting identified security gaps.

Use only on networks you own or have written authorization for.
Unauthorized use is illegal.

FILES

main.py main entry point scanner.py network and port scanning
scenario_engine.py insider threat scenarios logger.py timestamped
logging report_engine.py PDF report generation avvia.py portable
launcher Windows/Mac/Linux avvia_tails.sh launcher for Tails Linux
config.json configuration file requirements.txt Python dependencies

SCENARIOS

1.  silent port scan
2.  SMB folder enumeration
3.  SSH with weak credentials
4.  simulated HTTP data exfiltration

INSTALLATION

pip install -r requirements.txt

RUN

Windows python avvia.py

Mac / Linux sudo python3 avvia.py

Tails Linux bash avvia_tails.sh

Manual RAM mode (no traces) sudo python3 main.py –ram-mode

TAILS - PERSISTENT STORAGE

Logs and reports are stored in RAM and disappear after reboot. The
program itself can be saved in Persistent Storage.

To build the executable on Tails: pip install pyinstaller fpdf2 paramiko
–break-system-packages pyinstaller –onefile –name AuditSimulator
avvia.py cp dist/AuditSimulator /home/amnesia/Persistent/

CONFIGURATION

config.json supports the following parameters: network IP range to scan,
null for automatic extra_ports additional ports to scan scenario_delay
seconds between scenarios telegram_token Telegram bot token for alerts
telegram_chat_id Telegram chat ID for alerts

DEPENDENCIES

fpdf2 and paramiko (automatically installed by avvia.py)

NOTES

Educational project, for learning purposes only.
